import os

from troposphere import GetAtt, Ref, Sub, Template
import troposphere.awslambda as awslambda
from troposphere.iam import Policy
import troposphere.iam as iam
import troposphere.sns as sns
import troposphere.apigateway as apigateway
from awacs.aws import Action, Allow, PolicyDocument, Principal, Statement


class DispatcherFunction:

    def __init__(self, function_name, application_zip, api_gateway_rest_api):
        self._function_name = function_name
        self._application_zip = application_zip
        self._api_gateway_rest_api = api_gateway_rest_api
        self.api_path_part = 'dispatcher'

    def get_function_definition(self, function_role) -> awslambda.Function:
        return awslambda.Function(
            "DispatcherFunction",
            Handler="handler.lambda_handler",
            Role=GetAtt(function_role, "Arn"),
            FunctionName=self._function_name,
            Runtime="python3.11",
            Timeout=60,
            Code=awslambda.Code(
                ZipFile=self._application_zip
            )
        )

    def get_function_api_gateway_resource(self) -> apigateway.Resource:
        return apigateway.Resource("DevWorkflowApiGatewayResource",
                                   ParentId=GetAtt(self._api_gateway_rest_api, "RootResourceId"),
                                   PathPart=self.api_path_part,
                                   RestApiId=Ref(self._api_gateway_rest_api))

    def get_function_api_gateway_method(self, api_gateway_resource: apigateway.Resource, function_definition: awslambda.Function) -> apigateway.Method:
        return apigateway.Method("DevWorkflowApiGatewayMethod",
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
        awslambda_permission = self.get_lambda_trigger_permissions(function_definition)
        api_gateway_resource = self.get_function_api_gateway_resource()
        api_gateway_method = self.get_function_api_gateway_method(api_gateway_resource, function_definition)

        current_template.resources['DevWorkflowApiGatewayDeployment'].resource['DependsOn'] = api_gateway_method.title
        current_template.add_resource(function_role)
        current_template.add_resource(function_definition)
        current_template.add_resource(awslambda_permission)
        current_template.add_resource(api_gateway_resource)
        current_template.add_resource(api_gateway_method)

        return current_template

    def get_lambda_trigger_permissions(self, function_definition) -> awslambda.Permission:
        return awslambda.Permission("DevWorkflowApiGatewayLambdaPermission",
                                    Action="lambda:InvokeFunction",
                                    FunctionName=Ref(function_definition),
                                    Principal="apigateway.amazonaws.com",
                                    SourceArn=Sub("arn:aws:execute-api:${AWS::Region}:${AWS::AccountId}:${ApiGatewayDefinition}/*/POST/${PathPart}",
                                                  ApiGatewayDefinition=Ref(self._api_gateway_rest_api),
                                                  PathPart=self.api_path_part))

    @staticmethod
    def get_function_role_and_policy() -> iam.Role:
        allow_write_to_log_statement = Statement(
            Effect=Allow,
            Action=[
                Action("logs", "CreateLogGroup"),
                Action("logs", "CreateLogStream"),
                Action("logs", "PutLogEvents")
            ],
            Resource=["*"],
        )

        policy_document = PolicyDocument(
            Version="2012-10-17",
            Id="LambdaExecutionPolicy",
            Statement=[
                allow_write_to_log_statement
            ],
        )

        assume_role_statement = Statement(
            Effect=Allow,
            Principal=Principal("Service", ["lambda.amazonaws.com"]),
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
            "DevWorkflowFunctionRole",
            AssumeRolePolicyDocument=assume_role_policy_document,
            Policies=[
                Policy(
                    PolicyName="LambdaAllowResources",
                    PolicyDocument=policy_document
                )
            ]
        )

        return function_execution_role




