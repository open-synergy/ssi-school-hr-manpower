# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from collections import OrderedDict

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class ImportTeachingAssignment(models.TransientModel):
    """
    Wizard that fills the teaching tab of a draft school manpower
    planning from the school teaching assignments of one academic term.
    The main lines of the school that share the subject, the grade, the
    teacher employee and the weekly hours become one plan line, with the
    source lines linked to it. Source lines that are already linked to a
    line of the planning are skipped, so importing again adds nothing.
    """

    _name = "import_teaching_assignment"
    _description = "Import Teaching Lines from Teaching Assignment"

    planning_id = fields.Many2one(
        string="# Manpower Planning",
        comodel_name="manpower_planning",
        required=True,
        ondelete="cascade",
        help="Manpower planning that receives the imported teaching lines.",
    )
    academic_year_id = fields.Many2one(
        string="Academic Year",
        comodel_name="school_academic_year",
        related="planning_id.academic_year_id",
        help="Academic year of the planning. When it is filled, only the "
        "academic terms of that year can be selected.",
    )
    allowed_academic_term_ids = fields.Many2many(
        string="Allowed Academic Terms",
        comodel_name="school_academic_term",
        compute="_compute_allowed_academic_term_ids",
        help="Academic terms that can be selected, following the academic "
        "year of the planning.",
    )
    academic_term_id = fields.Many2one(
        string="Academic Term",
        comodel_name="school_academic_term",
        required=True,
        ondelete="restrict",
        help="Academic term (semester) whose teaching assignments are " "imported.",
    )

    @api.depends("academic_year_id")
    def _compute_allowed_academic_term_ids(self):
        """Limit the selectable terms to the year of the planning."""
        term_model = self.env["school_academic_term"]
        for record in self:
            result = term_model.search([])
            if record.academic_year_id:
                result = term_model.search(
                    [("year_id", "=", record.academic_year_id.id)]
                )
            record.allowed_academic_term_ids = result

    @api.model
    def default_get(self, fields_list):
        """Prefill the planning the wizard was opened from.

        The planning comes from the default of the opening button or,
        failing that, from the active record of the context.

        :param fields_list: field names requested by the client
        :return: dict of default values
        """
        res = super().default_get(fields_list)
        context = self.env.context
        if (
            "planning_id" in fields_list
            and not res.get("planning_id")
            and context.get("active_model") == "manpower_planning"
        ):
            res["planning_id"] = context.get("active_id")
        return res

    def action_confirm(self):
        """Create the teaching lines from the teaching assignments.

        :return: an ``ir.actions.act_window_close`` dict
        """
        for record in self.sudo():
            result = record._import_teaching_assignment()
        return result

    def _check_planning_condition(self):
        """Tell whether the planning is a draft with a school.

        :return: True when the planning is in draft and has a school;
            never raises
        """
        self.ensure_one()
        return self.planning_id.state == "draft" and bool(self.planning_id.school_id)

    def _get_source_criteria(self):
        """Build the domain of the teaching assignment lines to import.

        Extension point: override to narrow or widen the source lines.

        :return: search domain of the lines of the selected term in the
            school of the planning that no line of the planning links yet
        """
        self.ensure_one()
        linked = self.planning_id.teaching_ids.mapped("teaching_assignment_line_ids")
        return [
            ("academic_term_id", "=", self.academic_term_id.id),
            ("homeroom_id.school_id", "=", self.planning_id.school_id.id),
            ("id", "not in", linked.ids),
        ]

    def _get_group_key(self, line):
        """Build the key that decides which main lines share a plan line.

        Extension point: override to group the main lines differently.

        :param line: a ``school_teaching_assignment_line`` record
        :return: tuple of subject id, grade id, teacher employee id and
            weekly hours
        """
        return (
            line.subject_id.id,
            line.grade_id.id,
            line.teacher_id.employee_id.id,
            line.weekly_hours,
        )

    def _get_co_teacher(self, main_lines, assistant_lines):
        """Pick the co-teacher of a group of main lines.

        The assistant lines that teach the subject in a class of the
        group are looked at. The co-teacher is set only when they point
        to exactly one employee that is not the teacher.

        :param main_lines: main lines of the group
        :param assistant_lines: all assistant lines still to import
        :return: tuple of the co-teacher ``hr.employee`` record and the
            assistant lines used, both empty when there is no co-teacher
        """
        employee_model = self.env["hr.employee"]
        subject = main_lines[0].subject_id
        classes = main_lines.mapped("grade_class_id")
        used = assistant_lines.filtered(
            lambda x: x.subject_id == subject and x.grade_class_id in classes
        )
        employees = used.mapped("teacher_id.employee_id")
        teacher = main_lines[0].teacher_id.employee_id
        if len(employees) != 1 or employees == teacher:
            return employee_model, used.browse()
        return employees, used

    def _prepare_teaching_values(self, main_lines, assistant_lines):
        """Build the values of one teaching line of the planning.

        :param main_lines: main lines of one group
        :param assistant_lines: all assistant lines still to import
        :return: dict of ``manpower_planning_teaching`` values
        """
        first = main_lines[0]
        co_employee, used = self._get_co_teacher(main_lines, assistant_lines)
        linked = main_lines | used
        return {
            "planning_id": self.planning_id.id,
            "subject_id": first.subject_id.id,
            "grade_id": first.grade_id.id,
            "grade_class_ids": [(6, 0, main_lines.mapped("grade_class_id").ids)],
            "weekly_hours": first.weekly_hours,
            "employee_id": first.teacher_id.employee_id.id,
            "co_employee_id": co_employee.id,
            "teaching_assignment_line_ids": [(6, 0, linked.ids)],
        }

    def _import_teaching_assignment(self):
        """Create one teaching line per group of main lines.

        Side effect: creates ``manpower_planning_teaching`` records in the
        planning. Existing lines are never changed or removed.

        :raises UserError: when the planning is not a draft with a school
        :return: an ``ir.actions.act_window_close`` dict
        """
        self.ensure_one()
        if not self._check_planning_condition():
            error_message = """
Context: Import teaching lines from teaching assignment
Database ID: %s
Problem: Manpower planning is not in draft or has no school
Solution: Select a school on a draft manpower planning before the import
""" % (
                self.planning_id.id,
            )
            raise UserError(_(error_message))
        lines = self.env["school_teaching_assignment_line"].search(
            self._get_source_criteria()
        )
        assistant_lines = lines.filtered(lambda x: x.role == "assistant")
        groups = OrderedDict()
        for line in lines.filtered(lambda x: x.role == "main"):
            key = self._get_group_key(line)
            groups[key] = groups.get(key, line.browse()) | line
        teaching_model = self.env["manpower_planning_teaching"]
        for main_lines in groups.values():
            teaching_model.create(
                self._prepare_teaching_values(main_lines, assistant_lines)
            )
        return {"type": "ir.actions.act_window_close"}
