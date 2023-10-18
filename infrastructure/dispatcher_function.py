import os

from troposphere import GetAtt
import troposphere.awslambda as awslambda
import troposphere.iam as iam


def get_resource(dispatcher_iam_resource: iam.Role) -> awslambda.Function:

    dispatcher_function = awslambda.Function(
        "DispatcherFunction",
        Handler="handler.lambda_handler",
        Role=GetAtt(dispatcher_iam_resource, "Arn"),
        FunctionName="DispatcherFunction",
        Runtime="python3.11",
        Timeout=60,
        Code=awslambda.Code(
            ZipFile=os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "application.zip")
        )
    )

    return dispatcher_function
