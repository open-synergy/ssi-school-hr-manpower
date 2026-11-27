# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class ManpowerPlanningTeaching(models.Model):
    """
    Detail line of a school manpower planning that plans the teaching of
    one subject on one grade: the classes taught, the weekly hours per
    class, the teacher and the co-teacher. A line without a teacher is
    vacant.
    """

    _name = "manpower_planning_teaching"
    _description = "Teaching Assignment Plan"
    _order = "planning_id, id"

    planning_id = fields.Many2one(
        string="# Manpower Planning",
        comodel_name="manpower_planning",
        required=True,
        ondelete="cascade",
        help="Manpower planning document that owns this teaching line.",
    )
    school_id = fields.Many2one(
        string="School",
        comodel_name="school",
        related="planning_id.school_id",
        store=True,
        compute_sudo=True,
        help="School of the manpower planning, copied from the header.",
    )
    subject_id = fields.Many2one(
        string="Subject",
        comodel_name="school_subject",
        required=True,
        ondelete="restrict",
        help="Subject that is taught. It must be applicable to the grade.",
    )
    grade_id = fields.Many2one(
        string="Grade",
        comodel_name="school_grade",
        required=True,
        ondelete="restrict",
        help="Grade the subject is taught on.",
    )
    grade_class_ids = fields.Many2many(
        string="Classes",
        comodel_name="school_grade_class",
        help="Classes of the grade that are taught. A class can be used "
        "by only one line of the same subject in a planning.",
    )
    weekly_hours = fields.Integer(
        string="Weekly Hours per Class",
        required=True,
        default=1,
        help="Lesson hours per week taught in each class. It must be at " "least 1.",
    )
    total_class = fields.Integer(
        string="Total Classes",
        compute="_compute_total_class",
        compute_sudo=True,
        store=True,
        help="Number of classes selected on this line.",
    )
    total_weekly_hours = fields.Integer(
        string="Total Weekly Hours",
        compute="_compute_total_weekly_hours",
        compute_sudo=True,
        store=True,
        help="Weekly hours per class multiplied by the number of classes.",
    )
    employee_id = fields.Many2one(
        string="Teacher",
        comodel_name="hr.employee",
        help="Employee who teaches. Leave empty when the line is vacant.",
    )
    is_vacant = fields.Boolean(
        string="Vacant",
        compute="_compute_is_vacant",
        compute_sudo=True,
        store=True,
        help="Checked automatically when no teacher is selected.",
    )
    co_employee_id = fields.Many2one(
        string="Co-Teacher",
        comodel_name="hr.employee",
        help="Employee who assists the teacher. It must be a different "
        "employee than the teacher.",
    )
    teaching_assignment_line_ids = fields.Many2many(
        string="Teaching Assignment Lines",
        comodel_name="school_teaching_assignment_line",
        relation="manpower_planning_teaching_assignment_line_rel",
        column1="teaching_id",
        column2="assignment_line_id",
        copy=False,
        help="Lines of the school teaching assignment this plan line was "
        "imported from. Optional; the line stays a plan that can be edited.",
    )
    notes = fields.Text(
        string="Notes",
        help="Free-form remarks about this teaching line.",
    )

    @api.depends("grade_class_ids")
    def _compute_total_class(self):
        """Count the classes selected on the line."""
        for record in self:
            result = len(record.grade_class_ids)
            record.total_class = result

    @api.depends("weekly_hours", "total_class")
    def _compute_total_weekly_hours(self):
        """Multiply the weekly hours per class by the number of classes."""
        for record in self:
            result = record.weekly_hours * record.total_class
            record.total_weekly_hours = result

    @api.depends("employee_id")
    def _compute_is_vacant(self):
        """Flag the line as vacant when no teacher is selected."""
        for record in self:
            result = True
            if record.employee_id:
                result = False
            record.is_vacant = result

    @api.constrains("subject_id", "grade_id")
    def _check_subject_grade(self):
        """Reject lines whose subject is not applicable to the grade.

        :raises ValidationError: when the condition method returns False
        """
        for record in self.sudo():
            if not record._check_subject_grade_condition():
                error_message = """
Context: Create or update a teaching assignment plan line
Database ID: %s
Problem: The subject is not applicable to the selected grade
Solution: Select a subject taught on the grade, or add the grade to the
applicable grades of the subject
""" % (
                    record.id,
                )
                raise ValidationError(_(error_message))

    def _check_subject_grade_condition(self):
        """Tell whether the grade is one of the grades of the subject.

        :return: True when valid; never raises
        """
        self.ensure_one()
        return self.grade_id in self.subject_id.grade_ids

    @api.constrains("weekly_hours")
    def _check_weekly_hours(self):
        """Reject lines whose weekly hours per class are lower than one.

        :raises ValidationError: when the condition method returns False
        """
        for record in self.sudo():
            if not record._check_weekly_hours_condition():
                error_message = """
Context: Create or update a teaching assignment plan line
Database ID: %s
Problem: Weekly hours per class must be at least 1
Solution: Set the weekly hours per class to 1 or more
""" % (
                    record.id,
                )
                raise ValidationError(_(error_message))

    def _check_weekly_hours_condition(self):
        """Tell whether the weekly hours per class are at least one.

        Extension point: override to change the minimum hours.

        :return: True when valid; never raises
        """
        self.ensure_one()
        return self.weekly_hours >= 1

    @api.constrains("employee_id", "co_employee_id")
    def _check_co_employee(self):
        """Reject lines where the co-teacher is the teacher.

        :raises ValidationError: when the condition method returns False
        """
        for record in self.sudo():
            if not record._check_co_employee_condition():
                error_message = """
Context: Create or update a teaching assignment plan line
Database ID: %s
Problem: The co-teacher is the same employee as the teacher
Solution: Select another co-teacher or leave the co-teacher empty
""" % (
                    record.id,
                )
                raise ValidationError(_(error_message))

    def _check_co_employee_condition(self):
        """Tell whether the co-teacher differs from the teacher.

        :return: True when valid; never raises
        """
        self.ensure_one()
        if not self.co_employee_id:
            return True
        return self.co_employee_id != self.employee_id

    def _get_class_duplicate_criteria(self):
        """Build the domain of other lines teaching the same classes.

        Extension point: override to widen or narrow the duplicate scope.

        :return: search domain of the lines of the same planning and
            subject that share a class with this line
        """
        self.ensure_one()
        return [
            ("planning_id", "=", self.planning_id.id),
            ("subject_id", "=", self.subject_id.id),
            ("grade_class_ids", "in", self.grade_class_ids.ids),
            ("id", "!=", self.id),
        ]

    @api.constrains("subject_id", "grade_class_ids", "planning_id")
    def _check_class_unique(self):
        """Reject a class used by two lines of one subject in a planning.

        :raises ValidationError: when the condition method returns False
        """
        for record in self.sudo():
            if not record._check_class_unique_condition():
                error_message = """
Context: Create or update a teaching assignment plan line
Database ID: %s
Problem: A class is already used by another line of the same subject in
this planning
Solution: Remove the class from this line or from the other line
""" % (
                    record.id,
                )
                raise ValidationError(_(error_message))

    def _check_class_unique_condition(self):
        """Tell whether no class is shared with another line of the subject.

        :return: True when valid; never raises
        """
        self.ensure_one()
        if not self.grade_class_ids:
            return True
        criteria = self._get_class_duplicate_criteria()
        return self.search_count(criteria) == 0
