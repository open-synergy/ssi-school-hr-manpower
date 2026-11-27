# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


# Extends the vacancy request wizard of the manpower planning with the
# vacant teaching lines of a school planning: one proposed line per vacant
# teaching line that has no vacancy yet, and the teacher job position
# shared by those lines.
class CreateRecruitmentVacancyFromManpowerPlanning(models.TransientModel):
    _name = "create_recruitment_vacancy_from_manpower_planning"
    _inherit = ["create_recruitment_vacancy_from_manpower_planning"]

    teaching_job_id = fields.Many2one(
        string="Teacher Job Position",
        comodel_name="hr.job",
        help="Job position of the vacancies requested for the teaching "
        "lines. It is copied to every teaching line of the wizard.",
    )

    @api.onchange("teaching_job_id")
    def onchange_teaching_job_id(self):
        """Copy the teacher job position to the teaching lines."""
        for line in self.line_ids.filtered("teaching_id"):
            line.job_id = self.teaching_job_id

    @api.model
    def _prepare_default_line_values(self, planning):
        """Add one proposed line per vacant teaching line without vacancy.

        A teaching line is requested when no non-cancelled vacancy of the
        planning is linked to it. The job position stays empty until the
        teacher job position of the wizard is selected.

        :param planning: the ``manpower_planning`` record
        :return: list of dicts of line values
        """
        result = super()._prepare_default_line_values(planning)
        planning = planning.sudo()
        vacancies = planning.recruitment_vacancy_ids.filtered(
            lambda x: x.state != "cancel"
        )
        requested = vacancies.mapped("manpower_planning_teaching_id")
        teachings = planning.teaching_ids.filtered("is_vacant") - requested
        for teaching in teachings:
            result.append(
                {
                    "teaching_id": teaching.id,
                    "weekly_hours": teaching.total_weekly_hours,
                    "total_class": teaching.total_class,
                    "quantity": 1,
                }
            )
        return result

    def _prepare_vacancy_values(self, line):
        """Add the teaching data of the line to the vacancy values.

        :param line: the wizard line the vacancy is created for
        :return: dict of ``recruitment_vacancy`` values
        """
        result = super()._prepare_vacancy_values(line)
        if line.teaching_id:
            result.update(
                {
                    "manpower_planning_teaching_id": line.teaching_id.id,
                    "subject_id": line.teaching_id.subject_id.id,
                    "weekly_hours": line.weekly_hours,
                    "total_class": line.total_class,
                }
            )
        return result
