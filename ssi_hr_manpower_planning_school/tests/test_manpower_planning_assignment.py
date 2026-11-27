# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo_yaml_test import YamlTransactionCase

from odoo.tests import tagged


@tagged("post_install", "-at_install")
class TestManpowerPlanningAssignment(YamlTransactionCase):
    """Cover the additional assignment plan lines."""

    def test_manpower_planning_assignment(self):
        """Run the assignment default hours and category scenarios."""
        self.run_yaml_scenario("test_data_manpower_planning_assignment.yaml")
