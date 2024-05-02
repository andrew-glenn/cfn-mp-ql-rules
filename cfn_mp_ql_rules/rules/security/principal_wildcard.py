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


from cfnlint.rules import CloudFormationLintRule, RuleMatch
from ...common import deep_get

LINT_ERROR_MESSAGE = "Policy should not allow * Principal"

CFN_NAG_RULES = ["F16", "F18", "F20", "F21"]


def determine_wildcard_Principal_violations(cfn, policy_path):
    violating_methods = []
    policy = deep_get(cfn.template, policy_path, [])

    if policy["Effect"] == "Deny":
        return violating_methods
    violating_methods.append(policy_path + ["Principal"])
    return violating_methods


class IAMPrincipalWildcard(CloudFormationLintRule):
    """Check for wildcards in IAM Principal statements."""

    id = "EPolicyWildcardPrincipal"
    shortdesc = "* on Principal property is a bad idea"
    description = "Wildcards should not be used for Principals in IAM policies."
    source_url = "https://github.com/aws-ia/cfn-ia-rules/blob/main/cfn_ia_rules/rules/security/principal_wildcard.py"
    tags = ["iam"]
    SEARCH_PROPS = ["Principal"]

    def match(self, cfn):
        """Basic Matching"""
        violation_matches = []
        term_matches = []
        for prop in self.SEARCH_PROPS:
            term_matches += cfn.search_deep_keys(prop)
        for tm in term_matches:
            if tm[-1] not in ["*", ["*"]]:
                continue
            violating_methods = determine_wildcard_Principal_violations(cfn, tm[:-2])
            for ln in violating_methods:
                violation_matches.append(RuleMatch(ln, LINT_ERROR_MESSAGE))
        return violation_matches
