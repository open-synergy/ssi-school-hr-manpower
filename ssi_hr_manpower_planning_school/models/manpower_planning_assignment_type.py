# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ManpowerPlanningAssignmentType(models.Model):
    """
    Master data of the assignment types used by the additional
    assignment lines of a school manpower planning. A type belongs to a
    category (structural, additional duty, non-teacher, picket,
    achievement coaching or extracurricular coach) and states whether
    its hours are counted per week or per day.
    """

    _name = "manpower_planning_assignment_type"
    _inherit = ["mixin.master_data"]
    _description = "Manpower Planning Assignment Type"

    category = fields.Selection(
        string="Category",
        selection=[
            ("structural", "Structural"),
            ("additional", "Additional Duty"),
            ("non_teacher", "Non-Teacher"),
            ("picket", "Picket"),
            ("binpres_academic", "Academic Achievement Coaching"),
            ("binpres_non_academic", "Non-Academic Achievement Coaching"),
            ("extracurricular", "Extracurricular Coach"),
        ],
        required=True,
        help="Kind of assignment this type stands for. It decides how "
        "the assignment line is grouped and which fields it shows.",
    )
    hour_basis = fields.Selection(
        string="Hour Basis",
        selection=[
            ("week", "Per Week"),
            ("day", "Per Day"),
        ],
        required=True,
        default="week",
        help="Period the hours of an assignment line of this type are "
        "counted in: per week or per day (for example a picket duty).",
    )
    default_hours = fields.Integer(
        string="Default Hours",
        help="Hours copied to a new assignment line of this type. The "
        "line hours can still be changed.",
    )
    job_id = fields.Many2one(
        string="Job Position",
        comodel_name="hr.job",
        ondelete="restrict",
        help="Job position this assignment type is usually given to. " "Optional.",
    )
