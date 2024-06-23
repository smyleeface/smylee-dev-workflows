import troposphere.apigateway as apigateway
import troposphere.awslambda as awslambda
import troposphere.iam as iam
from awacs.aws import Action, Allow, PolicyDocument, Principal, Statement
from troposphere import GetAtt, Ref, Sub, Template
from troposphere.iam import Policy


class FunctionDispatcher:

    def __init__(
        self,
        app_prefix,
        application_s3_param,
        application_zip_param,
        api_gateway_rest_api,
        app_parameter_store_path,
        primary_kms_arn,
        s3_bucket_for_payloads
    ):
        self._app_name = "FunctionDispatcher"
        self._api_path_part = "github-dispatcher"
        self._app_prefix = app_prefix
        self._application_s3_param = application_s3_param
        self._application_zip_param = application_zip_param
        self._api_gateway_rest_api = api_gateway_rest_api
        self._app_parameter_store_path = app_parameter_store_path
        self._primary_kms_arn = primary_kms_arn
        self._s3_bucket_for_payloads = s3_bucket_for_payloads

    def get_function_definition(self, function_role) -> awslambda.Function:
        return awslambda.Function(
            self._app_name,
            Handler="dev_workflow.dispatcher.handler.lambda_handler",
            Role=GetAtt(function_role, "Arn"),
            FunctionName=self._app_prefix + "-" + self._app_name,
            Runtime="python3.11",
            Timeout=120,
            Code=awslambda.Code(
                S3Bucket=Ref(self._application_s3_param), S3Key=Ref(self._application_zip_param)
            ),
            Environment=awslambda.Environment(
                Variables={"S3_BUCKET_FOR_PAYLOADS": Ref(self._s3_bucket_for_payloads)}
            )
        )

    def get_function_api_gateway_resource(self) -> apigateway.Resource:
        return apigateway.Resource(
            self._app_name + "ApiGatewayResource",
            ParentId=GetAtt(self._api_gateway_rest_api, "RootResourceId"),
            PathPart=self._api_path_part,
            RestApiId=Ref(self._api_gateway_rest_api),
        )

    def get_function_api_gateway_method(
        self, api_gateway_resource: apigateway.Resource, function_definition: awslambda.Function
    ) -> apigateway.Method:
        return apigateway.Method(
            self._app_name + "ApiGatewayMethod",
            HttpMethod="POST",
            ResourceId=Ref(api_gateway_resource),
            RestApiId=Ref(self._api_gateway_rest_api),
            AuthorizationType="NONE",
            MethodResponses=[apigateway.MethodResponse(StatusCode="200")],
            Integration=apigateway.Integration(
                Type="AWS",
                IntegrationHttpMethod="POST",
                Uri=Sub(
                    "arn:aws:apigateway:${AWS::Region}:lambda:path/2015-03-31/functions/${FunctionArn}/invocations",
                    FunctionArn=GetAtt(function_definition, "Arn"),
                ),
                PassthroughBehavior="WHEN_NO_MATCH",
                IntegrationResponses=[apigateway.IntegrationResponse(StatusCode="200")],
                RequestParameters={"integration.request.header.X-Amz-Invocation-Type": "'Event'"},
                RequestTemplates={
                    "application/json": """
##  See https://docs.aws.amazon.com/apigateway/latest/developerguide/api-gateway-mapping-template-reference.html
##  This template will pass through all parameters including path, querystring, header, stage variables, and context through to the integration endpoint via the body/payload
#set($allParams = $input.params())
{
"body" : "$util.escapeJavaScript($input.body).replaceAll("\\'","'")",
"params" : {
#foreach($type in $allParams.keySet())
    #set($params = $allParams.get($type))
"$type" : {
    #foreach($paramName in $params.keySet())
    "$paramName" : "$util.escapeJavaScript($params.get($paramName))"
        #if($foreach.hasNext),#end
    #end
}
    #if($foreach.hasNext),#end
#end
},
"stage-variables" : {
#foreach($key in $stageVariables.keySet())
"$key" : "$util.escapeJavaScript($stageVariables.get($key))"
    #if($foreach.hasNext),#end
#end
},
"context" : {
    "account-id" : "$context.identity.accountId",
    "api-id" : "$context.apiId",
    "api-key" : "$context.identity.apiKey",
    "authorizer-principal-id" : "$context.authorizer.principalId",
    "caller" : "$context.identity.caller",
    "cognito-authentication-provider" : "$context.identity.cognitoAuthenticationProvider",
    "cognito-authentication-type" : "$context.identity.cognitoAuthenticationType",
    "cognito-identity-id" : "$context.identity.cognitoIdentityId",
    "cognito-identity-pool-id" : "$context.identity.cognitoIdentityPoolId",
    "http-method" : "$context.httpMethod",
    "stage" : "$context.stage",
    "source-ip" : "$context.identity.sourceIp",
    "user" : "$context.identity.user",
    "user-agent" : "$context.identity.userAgent",
    "user-arn" : "$context.identity.userArn",
    "request-id" : "$context.requestId",
    "resource-id" : "$context.resourceId",
    "resource-path" : "$context.resourcePath"
    }
}
                """
                },
            ),
        )

    def add_resource(self, current_template: Template) -> Template:
        function_role = self.get_function_role_and_policy()
        function_definition = self.get_function_definition(function_role)
        function_event_invoke_config = self.get_function_event_invoke_config(function_definition)
        awslambda_permission = self.get_lambda_trigger_permissions(function_definition)
        api_gateway_resource = self.get_function_api_gateway_resource()
        api_gateway_method = self.get_function_api_gateway_method(
            api_gateway_resource, function_definition
        )

        current_template.add_resource(function_role)
        current_template.add_resource(function_definition)
        current_template.add_resource(function_event_invoke_config)
        current_template.add_resource(awslambda_permission)
        current_template.add_resource(api_gateway_resource)
        current_template.add_resource(api_gateway_method)

        return current_template

    def get_lambda_trigger_permissions(self, function_definition) -> awslambda.Permission:
        return awslambda.Permission(
            self._app_name + "ApiGatewayLambdaPermission",
            Action="lambda:InvokeFunction",
            FunctionName=Ref(function_definition),
            Principal="apigateway.amazonaws.com",
            SourceArn=Sub(
                "arn:aws:execute-api:${AWS::Region}:${AWS::AccountId}:${ApiGatewayDefinition}/*/POST/${PathPart}",
                ApiGatewayDefinition=Ref(self._api_gateway_rest_api),
                PathPart=self._api_path_part,
            ),
        )

    def get_function_event_invoke_config(
        self, function_definition: awslambda.Function
    ) -> awslambda.EventInvokeConfig:
        return awslambda.EventInvokeConfig(
            self._app_name + "EventInvokeConfig",
            FunctionName=Ref(function_definition),
            MaximumRetryAttempts=0,
            Qualifier="$LATEST",
        )

    def get_function_role_and_policy(self) -> iam.Role:
        allow_write_to_log_statement = Statement(
            Effect=Allow,
            Action=[
                Action("logs", "CreateLogGroup"),
                Action("logs", "CreateLogStream"),
                Action("logs", "PutLogEvents"),
            ],
            Resource=["*"],
        )

        allow_publish_to_topic = Statement(
            Effect=Allow,
            Action=[
                Action("sns", "Publish"),
            ],
            Resource=[Sub("arn:aws:sns:${AWS::Region}:${AWS::AccountId}:DevWorkflow-*")],
        )

        allow_write_to_s3_bucket = Statement(
            Effect=Allow,
            Action=[
                Action("s3", "PutObject"),
                Action("s3", "GetObject*"),
                Action("s3", "ListAllMyBuckets"),
            ],
            Resource=[
                f"arn:aws:s3:::{self._s3_bucket_for_payloads.resource['Properties']['BucketName']}/*",
                f"arn:aws:s3:::{self._s3_bucket_for_payloads.resource['Properties']['BucketName']}",
            ],
        )

        allow_get_parameter_statement = Statement(
            Effect=Allow,
            Action=[
                Action("ssm", "GetParameter*"),
            ],
            Resource=[
                Sub(
                    "arn:aws:ssm:${AWS::Region}:${AWS::AccountId}:parameter${AppParameterStorePath}/*",
                    AppParameterStorePath=self._app_parameter_store_path,
                )
            ],
        )

        allow_kms_decrypt = Statement(
            Effect=Allow,
            Action=[
                Action("kms", "Decrypt"),
            ],
            Resource=[self._primary_kms_arn],
        )

        policy_document = PolicyDocument(
            Version="2012-10-17",
            Id="LambdaExecutionPolicy",
            Statement=[
                allow_write_to_log_statement,
                allow_get_parameter_statement,
                allow_kms_decrypt,
                allow_publish_to_topic,
                allow_write_to_s3_bucket
            ],
        )

        # trust relationship for lambda
        assume_role_statement = Statement(
            Effect=Allow,
            Principal=Principal("Service", ["lambda.amazonaws.com", "ssm.amazonaws.com"]),
            Action=[Action("sts", "AssumeRole")],
        )

        assume_role_policy_document = PolicyDocument(
            Version="2012-10-17",
            Id="AssumeRolePolicy",
            Statement=[assume_role_statement],
        )

        function_execution_role = iam.Role(
            self._app_name + "FunctionRole",
            AssumeRolePolicyDocument=assume_role_policy_document,
            Policies=[Policy(PolicyName="LambdaAllowResources", PolicyDocument=policy_document)],
        )

        return function_execution_role
