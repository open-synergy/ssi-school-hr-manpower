# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo_yaml_test import YamlTransactionCase

from odoo.tests import tagged


@tagged("post_install", "-at_install")
class TestManpowerPlanningGenerateCurriculum(YamlTransactionCase):
    """Cover the generation of teaching lines from the school curriculum."""

    def test_manpower_planning_generate_curriculum(self):
        """Run the generation, idempotency and guard scenarios."""
        self.run_yaml_scenario("test_data_manpower_planning_generate_curriculum.yaml")
