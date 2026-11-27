# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo_yaml_test import YamlTransactionCase

from odoo.tests import tagged


@tagged("post_install", "-at_install")
class TestImportTeachingAssignment(YamlTransactionCase):
    """Cover the import of teaching lines from teaching assignments."""

    def test_import_teaching_assignment(self):
        """Run the grouping, idempotency, co-teacher and guard scenarios."""
        self.run_yaml_scenario("test_data_import_teaching_assignment.yaml")
