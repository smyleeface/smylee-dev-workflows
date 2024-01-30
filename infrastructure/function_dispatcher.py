import os

from troposphere import GetAtt, Ref, Sub, Template
import troposphere.awslambda as awslambda
from troposphere.iam import Policy
import troposphere.iam as iam
import troposphere.apigateway as apigateway
from awacs.aws import Action, Allow, PolicyDocument, Principal, Statement


class FunctionDispatcher:

    def __init__(self, app_prefix, application_s3_param, application_zip_param, api_gateway_rest_api, app_parameter_store_path, primary_kms_arn):
        self._app_name = "FunctionDispatcher"
        self._api_path_part = 'github-dispatcher'
        self._app_prefix = app_prefix
        self._application_s3_param = application_s3_param
        self._application_zip_param = application_zip_param
        self._api_gateway_rest_api = api_gateway_rest_api
        self._app_parameter_store_path = app_parameter_store_path
        self._primary_kms_arn = primary_kms_arn

    def get_function_definition(self, function_role) -> awslambda.Function:
        return awslambda.Function(
            self._app_name,
            Handler="handler.lambda_handler",
            Role=GetAtt(function_role, "Arn"),
            FunctionName=self._app_prefix + self._app_name,
            Runtime="python3.11",
            Timeout=60,
            Code=awslambda.Code(
                S3Bucket=Ref(self._application_s3_param),
                S3Key=Ref(self._application_zip_param)
            ),
        )

    def get_function_api_gateway_resource(self) -> apigateway.Resource:
        return apigateway.Resource(self._app_name + "ApiGatewayResource",
                                   ParentId=GetAtt(self._api_gateway_rest_api, "RootResourceId"),
                                   PathPart=self._api_path_part,
                                   RestApiId=Ref(self._api_gateway_rest_api))

    def get_function_api_gateway_method(self, api_gateway_resource: apigateway.Resource, function_definition: awslambda.Function) -> apigateway.Method:
        return apigateway.Method(self._app_name + "ApiGatewayMethod",
                                 HttpMethod="POST",
                                 ResourceId=Ref(api_gateway_resource),
                                 RestApiId=Ref(self._api_gateway_rest_api),
                                 AuthorizationType="NONE",
                                 Integration=apigateway.Integration(
                                     IntegrationHttpMethod="POST",
                                     Type="AWS_PROXY",
                                     Uri=Sub(
                                         "arn:aws:apigateway:${AWS::Region}:lambda:path/2015-03-31/functions/${FunctionArn}/invocations",
                                         FunctionArn=GetAtt(function_definition, 'Arn')),
                                 ))

    def add_resource(self, current_template: Template) -> Template:
        function_role = self.get_function_role_and_policy()
        function_definition = self.get_function_definition(function_role)
        function_event_invoke_config = self.get_function_event_invoke_config(function_definition)
        awslambda_permission = self.get_lambda_trigger_permissions(function_definition)
        api_gateway_resource = self.get_function_api_gateway_resource()
        api_gateway_method = self.get_function_api_gateway_method(api_gateway_resource, function_definition)

        current_template.resources['DevWorkflowApiGatewayDeployment'].resource['DependsOn'] = api_gateway_method.title
        current_template.add_resource(function_role)
        current_template.add_resource(function_definition)
        current_template.add_resource(function_event_invoke_config)
        current_template.add_resource(awslambda_permission)
        current_template.add_resource(api_gateway_resource)
        current_template.add_resource(api_gateway_method)

        return current_template

    def get_lambda_trigger_permissions(self, function_definition) -> awslambda.Permission:
        return awslambda.Permission(self._app_name + "ApiGatewayLambdaPermission",
                                    Action="lambda:InvokeFunction",
                                    FunctionName=Ref(function_definition),
                                    Principal="apigateway.amazonaws.com",
                                    SourceArn=Sub("arn:aws:execute-api:${AWS::Region}:${AWS::AccountId}:${ApiGatewayDefinition}/*/POST/${PathPart}",
                                                  ApiGatewayDefinition=Ref(self._api_gateway_rest_api),
                                                  PathPart=self._api_path_part))

    def get_function_event_invoke_config(self, function_definition: awslambda.Function) -> awslambda.EventInvokeConfig:
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
                Action("logs", "PutLogEvents")
            ],
            Resource=["*"],
        )

        allow_get_parameter_statement = Statement(
            Effect=Allow,
            Action=[
                Action("ssm", "GetParameter*"),
            ],
            Resource=[Sub("arn:aws:ssm:${AWS::Region}:${AWS::AccountId}:parameter${AppParameterStorePath}/*",
                          AppParameterStorePath=self._app_parameter_store_path)],
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
                allow_kms_decrypt
            ],
        )

        # trust relationship for lambda
        assume_role_statement = Statement(
            Effect=Allow,
            Principal=Principal("Service", ["lambda.amazonaws.com", "ssm.amazonaws.com"]),
            Action=[Action("sts", "AssumeRole")]
        )

        assume_role_policy_document = PolicyDocument(
            Version="2012-10-17",
            Id="AssumeRolePolicy",
            Statement=[
                assume_role_statement
            ],
        )

        function_execution_role = iam.Role(
            self._app_name + "FunctionRole",
            AssumeRolePolicyDocument=assume_role_policy_document,
            Policies=[
                Policy(
                    PolicyName="LambdaAllowResources",
                    PolicyDocument=policy_document
                )
            ]
        )

        return function_execution_role
