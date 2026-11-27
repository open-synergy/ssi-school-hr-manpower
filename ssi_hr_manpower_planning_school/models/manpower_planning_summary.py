# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


# Extends the manpower planning summary of ``ssi_hr_manpower_planning``
# with two sources, the teaching lines and the additional assignment
# lines, and with the school and the academic year of the planning. A
# vacant line counts as needed and vacant, so a planning without school
# data or without teaching lines keeps its formation rows as before.
class ManpowerPlanningSummary(models.Model):
    _name = "manpower_planning_summary"
    _inherit = ["manpower_planning_summary"]
    # Models the added sources and columns read from, flushed before the
    # view is searched. It is merged with the dependencies of the base.
    _depends = {
        "manpower_planning": ["school_id", "academic_year_id"],
        "manpower_planning_teaching": ["planning_id", "employee_id"],
        "manpower_planning_assignment": [
            "planning_id",
            "type_id",
            "employee_id",
            "category",
        ],
        "manpower_planning_assignment_type": ["job_id"],
    }

    category = fields.Selection(
        selection_add=[
            ("teaching", "Teaching"),
            ("structural", "Structural"),
            ("additional", "Additional Duty"),
            ("non_teacher", "Non-Teacher"),
            ("picket", "Picket"),
            ("binpres_academic", "Academic Achievement Coaching"),
            ("binpres_non_academic", "Non-Academic Achievement Coaching"),
            ("extracurricular", "Extracurricular Coach"),
        ],
    )
    school_id = fields.Many2one(
        string="School",
        comodel_name="school",
        readonly=True,
        help="School of the manpower planning.",
    )
    academic_year_id = fields.Many2one(
        string="Academic Year",
        comodel_name="school_academic_year",
        readonly=True,
        help="Academic year of the manpower planning.",
    )

    @api.model
    def _get_source_queries(self):
        """Return the SELECT queries the summary rows are built from.

        It adds the teaching lines and the additional assignment lines
        to the sources of the base. Each line is one needed position;
        it is filled when it has an employee and vacant otherwise. The
        co-teacher is not a position, so it is not counted.

        :return: list of SQL SELECT strings, one per source
        :rtype: list
        """
        result = super()._get_source_queries()
        teaching_query = """
        SELECT
            t.planning_id AS planning_id,
            NULL::integer AS job_id,
            'teaching'::varchar AS category,
            1 AS quantity_needed,
            CASE WHEN t.employee_id IS NULL THEN 0 ELSE 1 END
                AS quantity_filled,
            CASE WHEN t.employee_id IS NULL THEN 1 ELSE 0 END
                AS quantity_vacant
        FROM manpower_planning_teaching t
        """
        assignment_query = """
        SELECT
            a.planning_id AS planning_id,
            ty.job_id AS job_id,
            a.category::varchar AS category,
            1 AS quantity_needed,
            CASE WHEN a.employee_id IS NULL THEN 0 ELSE 1 END
                AS quantity_filled,
            CASE WHEN a.employee_id IS NULL THEN 1 ELSE 0 END
                AS quantity_vacant
        FROM manpower_planning_assignment a
        JOIN manpower_planning_assignment_type ty ON ty.id = a.type_id
        """
        result = result + [teaching_query, assignment_query]
        return result

    @api.model
    def _select(self):
        """Return the SELECT clause of the summary view.

        :return: SQL fragment of the base with the school and the
            academic year of the planning added
        """
        select_str = super()._select()
        select_str += """,
            p.school_id AS school_id,
            p.academic_year_id AS academic_year_id
        """
        return select_str

    @api.model
    def _group_by(self):
        """Return the GROUP BY clause of the summary view.

        :return: SQL fragment of the base with the school and the
            academic year of the planning added
        """
        group_by_str = super()._group_by()
        group_by_str += """,
            p.school_id,
            p.academic_year_id
        """
        return group_by_str
