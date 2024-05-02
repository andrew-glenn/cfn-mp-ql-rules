"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""


from datetime import datetime, timedelta
from cfnlint.rules.resources.lmbd.DeprecatedRuntime import DeprecatedRuntime
from cfnlint.rules import RuleMatch


class DeprecatedRuntimeEolWarning(DeprecatedRuntime):
    """Check for EOL Lambda Function Runtimes."""

    id = "W9932"
    shortdesc = "Check if EOL Lambda Function Runtimes are used"
    description = "Check if an end of life Lambda Runtime is specified and give a warning if used."
    source_url = "https://github.com/aws-ia/cfn-ia-rules/blob/main/cfn_ia_rules/rules/security/lambda_runtime_eol.py"
    tags = ["resources", "lambda", "runtime"]

    def check_runtime(self, runtime_value, path):
        """Check if the given runtime is valid"""
        matches = []

        runtime = self.deprecated_runtimes.get(runtime_value)
        if runtime:
            eol = datetime.strptime(runtime["eol"], "%Y-%m-%d")
            if eol < self.current_date:
                return matches
            if self.current_date > (eol + timedelta(days=-90)):
                new_id = self.id.replace("W", "E")
                old_id = self.id
                self.id = new_id
                message = (
                    "Runtime ({0}) will be EOL on {1}. Please consider updating to {2}"
                )
                matches.append(
                    RuleMatch(
                        path,
                        message.format(
                            runtime_value, runtime["eol"], runtime["successor"]
                        ),
                    )
                )
            elif self.current_date > (eol + timedelta(days=-365)):
                message = (
                    "Runtime ({0}) will be EOL on {1}. Please consider updating to {2}"
                )
                matches.append(
                    RuleMatch(
                        path,
                        message.format(
                            runtime_value, runtime["eol"], runtime["successor"]
                        ),
                    )
                )
        return matches
