# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import UserError


# Extends the manpower planning of ``ssi_hr_manpower_planning`` with the
# school context (school unit, academic year, school curriculum), the teaching
# assignment plan per subject and class, the additional assignments and
# the workload recap per employee. Every new field is optional, so a
# planning without school data keeps working as before.
class ManpowerPlanning(models.Model):
    _name = "manpower_planning"
    _inherit = ["manpower_planning"]

    school_id = fields.Many2one(
        string="School",
        comodel_name="school",
        readonly=True,
        states={"draft": [("readonly", False)]},
        ondelete="restrict",
        help="School unit this manpower planning is made for. Optional.",
    )
    school_branch_id = fields.Many2one(
        string="School Branch",
        comodel_name="school_branch",
        related="school_id.branch_id",
        store=True,
        compute_sudo=True,
        help="Branch of the selected school, copied from the school.",
    )
    academic_year_id = fields.Many2one(
        string="Academic Year",
        comodel_name="school_academic_year",
        readonly=True,
        states={"draft": [("readonly", False)]},
        ondelete="restrict",
        help="Academic year this manpower planning is made for. "
        "Selecting it fills the planning period.",
    )
    curriculum_id = fields.Many2one(
        string="Curriculum",
        comodel_name="school_curriculum",
        readonly=True,
        states={"draft": [("readonly", False)]},
        ondelete="restrict",
        domain="[('school_id', '=', school_id), ('state', '=', 'open')]",
        help="School curriculum this manpower planning follows. It is "
        "filled with the open curriculum of the school and can be "
        "emptied. Optional.",
    )
    teaching_ids = fields.One2many(
        string="Teaching Assignments",
        comodel_name="manpower_planning_teaching",
        inverse_name="planning_id",
        readonly=True,
        states={"draft": [("readonly", False)]},
        copy=True,
        help="Teaching assignment plan per subject, grade and class.",
    )
    assignment_ids = fields.One2many(
        string="Additional Assignments",
        comodel_name="manpower_planning_assignment",
        inverse_name="planning_id",
        readonly=True,
        states={"draft": [("readonly", False)]},
        copy=True,
        help="Structural, additional duty, non-teacher, picket, coaching "
        "and extracurricular coach assignments.",
    )
    workload_ids = fields.One2many(
        string="Workloads",
        comodel_name="manpower_planning_workload",
        inverse_name="planning_id",
        readonly=True,
        help="Teaching and additional hours recap per employee.",
    )

    @api.onchange("academic_year_id")
    def onchange_date_start(self):
        self.date_start = False
        if self.academic_year_id:
            self.date_start = self.academic_year_id.date_start

    @api.onchange("academic_year_id")
    def onchange_date_end(self):
        self.date_end = False
        if self.academic_year_id:
            self.date_end = self.academic_year_id.date_end

    @api.onchange("school_id")
    def onchange_curriculum_id(self):
        """Fill the curriculum with the open curriculum of the school.

        The curriculum is emptied when the school has no open curriculum
        or when the school is cleared.
        """
        self.curriculum_id = False
        if self.school_id:
            curriculum = self.env["school_curriculum"].search(
                self._get_curriculum_criteria(), limit=1
            )
            self.curriculum_id = curriculum

    def _get_curriculum_criteria(self):
        """Build the domain of the curriculum a school planning follows.

        Extension point: override to narrow or widen the choice.

        :return: search domain of the open curriculum of the school
        """
        self.ensure_one()
        return [
            ("school_id", "=", self.school_id.id),
            ("state", "=", "open"),
        ]

    def action_import_teaching_assignment(self):
        """Open the wizard that imports teaching lines from assignments.

        :return: an ``ir.actions.act_window`` dict opening the wizard
        """
        for record in self.sudo():
            result = record._import_teaching_assignment()
        return result

    def _import_teaching_assignment(self):
        """Build the action that opens the import wizard.

        The wizard creates nothing until it is confirmed, so this method
        writes nothing itself.

        :return: an ``ir.actions.act_window`` dict opening the wizard
        """
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": "Import from Teaching Assignment",
            "res_model": "import_teaching_assignment",
            "view_mode": "form",
            "target": "new",
            "context": {"default_planning_id": self.id},
        }

    def action_generate_teaching_from_curriculum(self):
        """Add teaching lines from the lines of the curriculum.

        Triggered by the **Generate from Curriculum** button of a draft
        planning that has a curriculum. Subjects of a grade that already
        have a teaching line are kept as they are, so the button can be
        clicked again safely.

        :return: nothing; the new lines appear on the Teaching tab
        """
        for record in self.sudo():
            record._generate_teaching_from_curriculum()

    def _generate_teaching_from_curriculum(self):
        """Create one teaching line per curriculum line of the planning.

        The line takes the subject, the grade and the weekly hours of the
        curriculum line, and the classes of the school with that grade.
        The teacher is left empty, so the new line is vacant. A subject
        and grade that already has a teaching line is skipped, and so is
        a grade without a class in the school. Existing lines are never
        changed or removed.

        :raises UserError: when the planning is not a draft or has no
            curriculum
        """
        self.ensure_one()
        if not self._check_generate_teaching_condition():
            error_message = """
Context: Generate teaching lines from the curriculum
Database ID: %s
Problem: Manpower planning is not in draft or has no curriculum
Solution: Select a curriculum on a draft manpower planning before the
generation
""" % (
                self.id,
            )
            raise UserError(_(error_message))
        class_model = self.env["school_grade_class"]
        teaching_model = self.env["manpower_planning_teaching"]
        done = {(x.subject_id.id, x.grade_id.id) for x in self.teaching_ids}
        for line in self.curriculum_id.line_ids:
            key = (line.subject_id.id, line.grade_id.id)
            if key in done:
                continue
            grade_classes = class_model.search(
                self._get_curriculum_class_criteria(line)
            )
            if not grade_classes:
                continue
            teaching_model.create(
                self._prepare_teaching_from_curriculum_data(line, grade_classes)
            )
            done.add(key)

    def _check_generate_teaching_condition(self):
        """Tell whether the planning is a draft with a curriculum.

        :return: True when the planning is in draft and has a
            curriculum; never raises
        """
        self.ensure_one()
        return self.state == "draft" and bool(self.curriculum_id)

    def _get_curriculum_class_criteria(self, line):
        """Build the domain of the classes taught for a curriculum line.

        Extension point: override to narrow or widen the classes.

        :param line: a ``school_curriculum_line`` record
        :return: search domain of the classes of the planning school
            that have the grade of the curriculum line
        """
        self.ensure_one()
        return [
            ("school_id", "=", self.school_id.id),
            ("grade_id", "=", line.grade_id.id),
        ]

    def _prepare_teaching_from_curriculum_data(self, line, grade_classes):
        """Build the values of the teaching line of a curriculum line.

        Extension point: override to carry extra fields into the line.

        :param line: the source ``school_curriculum_line`` record
        :param grade_classes: the ``school_grade_class`` records taught
        :return: dict of ``manpower_planning_teaching`` values
        """
        self.ensure_one()
        return {
            "planning_id": self.id,
            "subject_id": line.subject_id.id,
            "grade_id": line.grade_id.id,
            "grade_class_ids": [(6, 0, grade_classes.ids)],
            "weekly_hours": line.weekly_hours,
        }
