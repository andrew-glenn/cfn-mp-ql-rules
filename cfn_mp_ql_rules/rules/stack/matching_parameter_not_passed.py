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


class MatchingParameterNotPassed(CloudFormationLintRule):
    """Check Nested Stack Parameters"""

    id = "E9902"
    experimental = True
    shortdesc = "Parameters in parent not passed to child"
    description = (
        "A parameter with the same name exists in parent "
        "and child that is not passed to the child."
    )
    source_url = "https://github.com/aws-ia/cfn-ia-rules/blob/main/cfn_ia_rules/rules/stack/matching_parameter_not_passed.py"
    tags = ["case"]

    @staticmethod
    def matching_but_not_used_check(
        current_template_path,
        parent_parameters,
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
        template_parsed = decode.cfn_yaml.load(template_file)

        child_parameters = template_parsed.get("Parameters")
        if child_parameters is None:
            child_parameters = {}

        for parameter in child_parameters:
            # We have a parameter in the parent matching the child
            if parameter in parent_parameters.keys():
                if parameter in resource_parameters.keys():
                    # The Parents value not being passed to the child
                    if parameter not in str(resource_parameters.get(parameter)):
                        # TODO: test for !Ref or the name of the Parameter in the value
                        missing_parameters.append(
                            f"{parameter} ({str(resource_parameters.get(parameter))})"
                        )

        if not len(missing_parameters) == 0:
            return str(missing_parameters)
        else:
            return None

    def match(self, cfn):
        """Basic Matching"""
        matches = []
        # try:
        resources = cfn.get_resources(resource_type=["AWS::CloudFormation::Stack"])

        parent_parameters = cfn.get_parameters()
        if type(parent_parameters) is None:
            parent_parameters = {}

        for r_name, r_values in resources.items():
            properties = r_values.get("Properties")
            child_template_url = properties.get("TemplateURL")

            child_template_parameters = properties.get("Parameters")
            if child_template_parameters is None:
                child_template_parameters = {}

            not_passed_to_child = self.matching_but_not_used_check(
                current_template_path=os.path.abspath(cfn.filename),
                parent_parameters=parent_parameters,
                resource_parameters=child_template_parameters,
                child_template_url=child_template_url,
                mappings=cfn.get_mappings(),
            )

            if not_passed_to_child:
                path = ["Resources", r_name, "Properties", "Parameters"]
                message = (
                    "Parameter defined in Parent with same name as child, "
                    f"however this value is never passed to child. {r_name} {not_passed_to_child}"
                )
                matches.append(RuleMatch(path, message))
        return matches
