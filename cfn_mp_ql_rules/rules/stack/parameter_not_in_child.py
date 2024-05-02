"""
  Copyright 2018 Amazon.com, Inc. or its affiliates. All Rights Reserved.

  Permission is hereby granted, free of charge, to any person obtaining a copy of this
  software and associated documentation files (the "Software"), to deal in the Software
  without restriction, including without limitation the rights to use, copy, modify,
  merge, publish, distribute, sublicense, and/or sell copies of the Software, and to
  permit persons to whom the Software is furnished to do so.

  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
  INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
  PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
  HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
  OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
  SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""


import os
from cfnlint import decode
from cfnlint.rules import CloudFormationLintRule, RuleMatch
from .stack_helper import template_url_to_path


class ParameterNotInChild(CloudFormationLintRule):
    """Check for passed parameters that don't exist in child template."""

    id = "E9904"
    experimental = True
    shortdesc = "Parameters in passed to stack resource but not defined in child"
    description = (
        "A parameter defined in template stack resource but not "
        "defined in the child template."
    )
    source_url = "https://github.com/aws-ia/cfn-ia-rules/blob/main/cfn_ia_rules/rules/stack/parameter_not_in_child.py"
    tags = ["case"]

    @staticmethod
    def missing_in_child_check(
        current_template_path,
        resource_parameters,
        child_template_url,
        mappings,
    ):
        missing_parameters = []

        # Hack out the QS bits and get the file_name
        template_file = template_url_to_path(
            current_template_path=current_template_path,
            template_url=child_template_url,
            template_mappings=mappings,
        )
        if isinstance(template_file, list) and len(template_file) == 1:
            template_file = template_file[0]
        elif isinstance(template_file, list):
            raise ValueError(f"expecting single template in a list {template_file}")

        # Load child stack
        # template_parser = MyTemplateParser()
        # template_parsed = template_parser.my_load_yaml_function(
        #     template_file=template_file
        # )
        template_parsed = decode.cfn_yaml.load(template_file)

        # Iterate over template resource parameters and check they exist
        # In the child template
        child_parameters = template_parsed.get("Parameters")
        if child_parameters is None:
            child_parameters = {}

        for parameter in resource_parameters.keys():
            # We have a parameter in the parent matching the child
            if parameter not in child_parameters.keys():
                missing_parameters.append(parameter)

        return missing_parameters

    def match(self, cfn):
        """Basic Matching"""
        matches = []
        # try:
        resources = cfn.get_resources(resource_type=["AWS::CloudFormation::Stack"])

        for r_name, r_values in resources.items():
            properties = r_values.get("Properties")
            child_template_url = properties.get("TemplateURL")

            child_template_parameters = properties.get("Parameters")
            if child_template_parameters is None:
                child_template_parameters = {}

            not_passed_to_child = self.missing_in_child_check(
                current_template_path=os.path.abspath(cfn.filename),
                resource_parameters=child_template_parameters,
                child_template_url=child_template_url,
                mappings=cfn.get_mappings(),
            )

            for e in not_passed_to_child:
                path = ["Resources", r_name, "Properties", "Parameters", e]
                message = f"Parameter {e} not present in child template {r_name}"
                matches.append(RuleMatch(path, message))
        return matches
