# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


# Extends the line of the vacancy request wizard with the teaching line it
# was proposed for. A teaching line carries the subject, the weekly hours
# and the classes, and takes its job position from the teacher job
# position of the wizard.
class CreateRecruitmentVacancyFromManpowerPlanningLine(models.TransientModel):
    _name = "create_recruitment_vacancy_from_manpower_planning_line"
    _inherit = ["create_recruitment_vacancy_from_manpower_planning_line"]

    # The job position of a teaching line is filled by the teacher job
    # position of the wizard, so it cannot be required by the database.
    # The constraint below keeps it mandatory for every line.
    job_id = fields.Many2one(
        required=False,
    )
    teaching_id = fields.Many2one(
        string="Teaching Assignment Plan",
        comodel_name="manpower_planning_teaching",
        ondelete="cascade",
        help="Vacant teaching line of the planning this line requests a "
        "teacher for. Empty for a line of a job position.",
    )
    subject_id = fields.Many2one(
        string="Subject",
        comodel_name="school_subject",
        related="teaching_id.subject_id",
        readonly=True,
        help="Subject of the teaching line.",
    )
    weekly_hours = fields.Integer(
        string="Weekly Hours",
        help="Lesson hours per week of the teaching line, for all of " "its classes.",
    )
    total_class = fields.Integer(
        string="Total Classes",
        help="Number of classes of the teaching line.",
    )

    @api.constrains("job_id", "teaching_id")
    def _check_job_id(self):
        """Reject lines that have no job position.

        :raises ValidationError: when the condition method returns False
        """
        for record in self.sudo():
            if not record._check_job_id_condition():
                error_message = """
Context: Create or update a vacancy request line
Database ID: %s
Problem: The job position of the line is empty
Solution: Select the Teacher Job Position of the wizard for a teaching
line, or the Job Position of the line for any other line
""" % (
                    record.id,
                )
                raise ValidationError(_(error_message))

    def _check_job_id_condition(self):
        """Tell whether the line has a job position.

        :return: True when the job position is set; never raises
        """
        self.ensure_one()
        return bool(self.job_id)
