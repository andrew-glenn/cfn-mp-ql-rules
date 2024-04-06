from cfn_mp_ql_rules.stack.DefaultParameter import (
    DefaultParameter,
)  # pylint: disable=E0401
from ... import BaseRuleTestCase


class TestDefaultParameter(BaseRuleTestCase):
    """Test template parameter configurations"""

    def setUp(self):
        """Setup"""
        super(TestDefaultParameter, self).setUp()
        self.collection.register(DefaultParameter())

    def test_file_positive(self):
        """Test Positive"""
        self.helper_file_positive()  # By default, a set of "correct" templates are checked

    def test_file_negative(self):
        """Test failure"""
        prefix = "test/fixtures/templates/bad/resources/stack/"
        self.helper_file_negative(
            "{}{}.yml".format(prefix, "ParameterNotInChild"), 1
        )  # Amount of expected matches
