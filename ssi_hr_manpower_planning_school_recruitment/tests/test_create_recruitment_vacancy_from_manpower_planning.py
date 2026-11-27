# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo_yaml_test import YamlTransactionCase

from odoo.tests import tagged


@tagged("post_install", "-at_install")
class TestCreateRecruitmentVacancyFromManpowerPlanningSchool(YamlTransactionCase):
    """Cover the teaching lines of the vacancy request wizard."""

    def test_create_recruitment_vacancy_from_manpower_planning(self):
        """Run the proposal, the execution and the negative path scenarios."""
        self.run_yaml_scenario(
            "test_data_create_recruitment_vacancy_from_manpower_planning.yaml"
        )
