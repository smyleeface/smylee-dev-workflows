from awacs.aws import Action, Allow, PolicyDocument, Principal, Statement
from troposphere import Sub, Template
import troposphere.sns as sns
import troposphere.iam as iam
from troposphere.iam import Policy


class FunctionPullRequestOpen:

    def __init__(
        self,
        app_prefix,
        application_s3_param,
        application_zip_param,
        app_parameter_store_path,
        primary_kms_arn,
    ):
        self._app_name = "FunctionPROpen"
        self._app_prefix = app_prefix
        self._application_s3_param = application_s3_param
        self._application_zip_param = application_zip_param
        self._app_parameter_store_path = app_parameter_store_path
        self._primary_kms_arn = primary_kms_arn

    def get_function_sns_topic_resource(self) -> sns.Topic:
        return sns.Topic(
            self._app_name + "Topic", TopicName=self._app_prefix + "-" + self._app_name
        )

    def add_resource(self, current_template: Template) -> Template:
        function_role = self.get_function_role_and_policy()
        sns_topic_resource = self.get_function_sns_topic_resource()
        current_template.add_resource(function_role)
        current_template.add_resource(sns_topic_resource)

        return current_template

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
