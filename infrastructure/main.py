import os

from troposphere import Template
import dispatcher_iam
import dispatcher_function
import sys

#todo create uuid for unique names that is used and stored in the cloudformation stack?
if __name__ == "__main__":
    template_file = sys.argv[1]

    main_template = Template()

    dispatcher_iam_resource = dispatcher_iam.get_resource()
    dispatcher_function_resource = dispatcher_function.get_resource(dispatcher_iam_resource)

    main_template.add_resource(dispatcher_iam_resource)
    main_template.add_resource(dispatcher_function_resource)

    with open(os.path.join(os.path.dirname(__file__), template_file), "w") as cf_file:
        cf_file.write(main_template.to_yaml())

    print(main_template.to_yaml())
