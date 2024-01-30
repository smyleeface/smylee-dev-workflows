import os

from troposphere import Template, Parameter, ImportValue
from api_gateway import apis
from function_dispatcher import FunctionDispatcher

import sys


if __name__ == "__main__":
    template_file = sys.argv[1]

    main_template = Template()

    # parameters
    primary_kms_arn = os.environ['KMS_KEY_ID_ARN']
    github_app_private_key_ssm_path = Parameter(
        "GHAppPrivateKeySSMPath",
        Type="String",
        Description="KMS Encrypted GitHub App Private Key SSM Parameter Path",
        Default='/SmyleeDevWorkflows/GitHubApp/PrivateKey'
    )

    # primary s3 bucket for uploading artifacts
    s3_bucket_for_artifacts_param_name = "BucketForUploadsUsWest2"
    s3_buckets_for_artifacts_import = ImportValue("S3::BucketForUploadsUsWest2-Name")
    s3_bucket_for_artifacts = Parameter(
        s3_bucket_for_artifacts_param_name,
        Type="String"
    )

    # Base API Gateway
    api_gateway_rest_api, api_gateway_deployment, api_gateway_stage = apis.get_resource()
    main_template.add_resource(api_gateway_rest_api)
    main_template.add_resource(api_gateway_deployment)
    main_template.add_resource(api_gateway_stage)

    # Dispatcher Function
    dispatcher_function_s3_zip_path_param_name = "DispatcherFunctionS3ZipPath"
    dispatcher_function_s3_zip_path = Parameter(
        dispatcher_function_s3_zip_path_param_name,
        Type="String"
    )
    dispatcher_function = FunctionDispatcher("DevWorkflow-DispatcherFunction",
                                             s3_bucket_for_artifacts_param_name,
                                             dispatcher_function_s3_zip_path_param_name,
                                             api_gateway_rest_api,
                                             '/SmyleeDevWorkflows',
                                             primary_kms_arn)
    main_template = dispatcher_function.add_resource(main_template)

    # add parameters to template
    main_template.add_parameter(s3_bucket_for_artifacts)
    main_template.add_parameter(dispatcher_function_s3_zip_path)

    with open(os.path.join(os.path.dirname(__file__), template_file), "w") as cf_file:
        cf_file.write(main_template.to_yaml())

    print(main_template.to_yaml())
