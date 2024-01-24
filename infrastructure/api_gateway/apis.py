import os

from troposphere import GetAtt, Ref
import troposphere.apigateway as apigateway
import troposphere.awslambda as awslambda


def get_resource():

    api_gateway_rest_api = apigateway.RestApi("DevWorkflowApi", Name="DevWorkflowApi")

    api_gateway_deployment = apigateway.Deployment("DevWorkflowApiGatewayDeployment",
                                                   RestApiId=Ref(api_gateway_rest_api),
                                                   Description="Deployment for PlaylistMonitorApi")
    api_gateway_stage = apigateway.Stage("DevWorkflowApiGatewayStage",
                                         StageName="Prod",
                                         RestApiId=Ref(api_gateway_rest_api),
                                         DeploymentId=Ref(api_gateway_deployment))

    return api_gateway_rest_api, api_gateway_deployment, api_gateway_stage
