# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo_yaml_test import YamlTransactionCase

from odoo.tests import tagged


@tagged("post_install", "-at_install")
class TestManpowerPlanningQuantity(YamlTransactionCase):
    """Cover the header quantities that follow the school positions."""

    def test_manpower_planning_quantity(self):
        """Run the header quantity scenarios."""
        self.run_yaml_scenario("test_data_manpower_planning_quantity.yaml")
