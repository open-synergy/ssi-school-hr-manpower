# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


# Extends the recruitment vacancy with the teaching data of the school
# manpower planning line it was requested for: the subject, the weekly
# lesson hours and the number of classes. Every field is optional, so a
# vacancy that does not come from a teaching line is unchanged.
class RecruitmentVacancy(models.Model):
    _name = "recruitment_vacancy"
    _inherit = ["recruitment_vacancy"]

    manpower_planning_teaching_id = fields.Many2one(
        string="Teaching Assignment Plan",
        comodel_name="manpower_planning_teaching",
        readonly=True,
        ondelete="restrict",
        help="Teaching line of the manpower planning this vacancy was "
        "requested for. Optional and filled when the vacancy is created "
        "from a vacant teaching line.",
    )
    subject_id = fields.Many2one(
        string="Subject",
        comodel_name="school_subject",
        readonly=True,
        states={"draft": [("readonly", False)]},
        help="Subject the new teacher will teach.",
    )
    weekly_hours = fields.Integer(
        string="Weekly Hours",
        readonly=True,
        states={"draft": [("readonly", False)]},
        help="Lesson hours per week the new teacher will teach.",
    )
    total_class = fields.Integer(
        string="Total Classes",
        readonly=True,
        states={"draft": [("readonly", False)]},
        help="Number of classes the new teacher will teach.",
    )
