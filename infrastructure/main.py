import os

from troposphere import Template
from api_gateway import apis
from dispatcher_function import DispatcherFunction

import sys

#todo create uuid for unique names that is used and stored in the cloudformation stack?
if __name__ == "__main__":
    template_file = sys.argv[1]

    main_template = Template()

    # Base API Gateway
    api_gateway_rest_api, api_gateway_deployment, api_gateway_stage = apis.get_resource()
    main_template.add_resource(api_gateway_rest_api)
    main_template.add_resource(api_gateway_deployment)
    main_template.add_resource(api_gateway_stage)

    # Dispatcher Function
    dispatcher_function_package_name = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "dispatcher_function_package.zip")
    dispatcher_function = DispatcherFunction("DevWorkflow-DispatcherFunction", dispatcher_function_package_name, api_gateway_rest_api)
    main_template = dispatcher_function.add_resource(main_template)

    with open(os.path.join(os.path.dirname(__file__), template_file), "w") as cf_file:
        cf_file.write(main_template.to_yaml())

    print(main_template.to_yaml())
