import troposphere.sns as sns
from troposphere import Template


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

    def add_resource(self, current_template: Template) -> Template:
        return current_template
