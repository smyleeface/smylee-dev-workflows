from troposphere.iam import Policy
import troposphere.iam as iam
from awacs.aws import Action, Allow, PolicyDocument, Principal, Statement


def get_resource() -> iam.Role:

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
        "PlaylistMonitorFunctionRole",
        AssumeRolePolicyDocument=assume_role_policy_document,
        Policies=[
            Policy(
                PolicyName="LambdaAllowResources",
                PolicyDocument=policy_document
            )
        ]
    )

    return function_execution_role
