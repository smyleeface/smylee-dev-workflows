import troposphere.apigateway as apigateway
from troposphere import Ref, GetAtt, Sub
from troposphere.logs import LogGroup


class Apis:
    def __init__(self):
        self.api_gateway_rest_api = None
        self.api_gateway_deployment = None
        self.api_gateway_deployment2 = None
        self.api_gateway_stage_logs = None
        self.api_gateway_stage = None

    def set_resource(self):

        self.api_gateway_rest_api = apigateway.RestApi("DevWorkflowApi", Name="DevWorkflowApi")

        self.api_gateway_deployment = apigateway.Deployment(
            "DevWorkflowApiGatewayDeployment",
            RestApiId=Ref(self.api_gateway_rest_api),
            Description="Deployment for the DevWorkflow API",
            DependsOn=self.api_gateway_rest_api,
            StageDescription=apigateway.StageDescription(
                LoggingLevel="INFO",
                MetricsEnabled=True,
                DataTraceEnabled=True,
            ),
        )

        self.api_gateway_deployment2 = apigateway.Deployment(
            "DevWorkflowApiGatewayDeployment2",
            RestApiId=Ref(self.api_gateway_rest_api),
            Description="Deployment for the DevWorkflow API",
            DependsOn=self.api_gateway_rest_api,
        )

        # self.api_gateway_stage_logs = LogGroup(
        #     "DevWorkflowApiGatewayStageProdLogs",
        #     LogGroupName=Sub(
        #         "/aws/api-gateway/${ApiId}/DevWorkflow/Prod",
        #         ApiId=Ref(self.api_gateway_rest_api)
        #     ),
        # )

        self.api_gateway_stage = apigateway.Stage(
            "DevWorkflowApiGatewayStage",
            DependsOn=self.api_gateway_deployment,
            StageName="Prod",
            RestApiId=Ref(self.api_gateway_rest_api),
            DeploymentId=Ref(self.api_gateway_deployment2),
            MethodSettings=[
                apigateway.MethodSetting(
                    HttpMethod="*",
                    ResourcePath="/*",
                    MetricsEnabled=True,
                    DataTraceEnabled=True,
                    LoggingLevel="INFO",
                )
            ],
            # AccessLogSetting=apigateway.AccessLogSetting(
            #     DestinationArn=GetAtt(self.api_gateway_stage_logs, 'Arn')
            # )
        )
