# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ManpowerPlanningAssignment(models.Model):
    """
    Detail line of a school manpower planning that plans one additional
    assignment: a structural position, an additional duty, a non-teacher
    position, a picket duty, an achievement coaching or an extracurricular
    coach. The line stores the hours and the employee, if any. A line
    without an employee is vacant.
    """

    _name = "manpower_planning_assignment"
    _description = "Additional Assignment Plan"
    _order = "planning_id, id"

    planning_id = fields.Many2one(
        string="# Manpower Planning",
        comodel_name="manpower_planning",
        required=True,
        ondelete="cascade",
        help="Manpower planning document that owns this assignment line.",
    )
    type_id = fields.Many2one(
        string="Assignment Type",
        comodel_name="manpower_planning_assignment_type",
        required=True,
        ondelete="restrict",
        help="Type of the assignment. It gives the category, the hour "
        "basis and the default hours.",
    )
    category = fields.Selection(
        string="Category",
        related="type_id.category",
        store=True,
        compute_sudo=True,
        help="Category of the assignment type, copied from the type.",
    )
    hour_basis = fields.Selection(
        string="Hour Basis",
        related="type_id.hour_basis",
        store=True,
        compute_sudo=True,
        help="Hour basis of the assignment type, copied from the type.",
    )
    employee_id = fields.Many2one(
        string="Employee",
        comodel_name="hr.employee",
        help="Employee who holds the assignment. Leave empty when the "
        "line is vacant.",
    )
    is_vacant = fields.Boolean(
        string="Vacant",
        compute="_compute_is_vacant",
        compute_sudo=True,
        store=True,
        help="Checked automatically when no employee is selected.",
    )
    position = fields.Selection(
        string="Position",
        selection=[
            ("coach", "Coach"),
            ("assistant", "Assistant Coach"),
        ],
        default="coach",
        help="Role in the activity. Used by the coaching and "
        "extracurricular categories only.",
    )
    hours = fields.Integer(
        string="Hours",
        help="Hours of the assignment, counted per week or per day "
        "following the hour basis. Filled with the default hours of the "
        "type and can be changed.",
    )
    class_count = fields.Integer(
        string="Number of Classes",
        help="Number of classes handled by the coaching or the "
        "extracurricular activity.",
    )
    date_start = fields.Date(
        string="Date Start",
        help="First day of the assignment. Optional.",
    )
    date_end = fields.Date(
        string="Date End",
        help="Last day of the assignment. Optional.",
    )
    notes = fields.Text(
        string="Notes",
        help="Free-form remarks about this assignment line.",
    )

    @api.depends("employee_id")
    def _compute_is_vacant(self):
        """Flag the line as vacant when no employee is selected."""
        for record in self:
            result = True
            if record.employee_id:
                result = False
            record.is_vacant = result

    @api.onchange("type_id")
    def onchange_hours(self):
        self.hours = 0
        if self.type_id:
            self.hours = self.type_id.default_hours
