# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
# pylint: disable=C8101
{
    "name": "HR - Manpower Planning - School",
    "version": "14.0.1.6.2",
    "website": "https://simetri-sinergi.id",
    "author": "OpenSynergy Indonesia, PT. Simetri Sinergi Indonesia",
    "license": "AGPL-3",
    "installable": True,
    "application": False,
    "depends": [
        "ssi_hr_manpower_planning",
        "ssi_school",
        "ssi_school_academic",
        "ssi_master_data_mixin",
        "web_tour",
    ],
    "data": [
        "security/res_groups/manpower_planning_assignment_type.xml",
        "security/ir_model_access/manpower_planning_assignment_type.xml",
        "security/ir_model_access/manpower_planning.xml",
        "security/ir_model_access/import_teaching_assignment.xml",
        "security/ir_rule/manpower_planning_workload.xml",
        "views/school.xml",
        "views/manpower_planning_assignment_type.xml",
        "views/manpower_planning.xml",
        "views/manpower_planning_summary.xml",
        "views/manpower_planning_workload.xml",
        "wizards/import_teaching_assignment.xml",
        "reports/manpower_planning_summary_templates.xml",
        "views/assets.xml",
    ],
    "demo": [],
}
