# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ManpowerPlanningWorkload(models.Model):
    """
    Read-only SQL view that recaps the workload of every employee in
    every school manpower planning: the teaching hours, the number of
    co-teaching lines, the additional assignment hours per week and per
    day, the picket hours per week, the total weekly hours, and for
    employees who teach the mandatory, lacking and excess hours. The
    lines without an employee are gathered in one row per planning
    that has no employee; it is never judged on mandatory hours. It
    feeds the workload tab of the planning form and the workload
    analysis.
    """

    _name = "manpower_planning_workload"
    _description = "Manpower Planning Workload"
    _auto = False
    _order = "planning_id, employee_id"
    _rec_name = "employee_id"
    # Models the view reads from, flushed before the view is searched.
    _depends = {
        "manpower_planning": [
            "company_id",
            "user_id",
            "school_id",
            "academic_year_id",
            "state",
        ],
        "manpower_planning_teaching": [
            "planning_id",
            "employee_id",
            "co_employee_id",
            "total_weekly_hours",
        ],
        "manpower_planning_assignment": [
            "planning_id",
            "employee_id",
            "category",
            "hour_basis",
            "hours",
        ],
        "school": [
            "manpower_picket_weekly_hours_per_day",
            "teacher_mandatory_weekly_hours",
            "co_teaching_hour_factor",
        ],
    }

    planning_id = fields.Many2one(
        string="# Manpower Planning",
        comodel_name="manpower_planning",
        readonly=True,
        help="Manpower planning document the workload belongs to.",
    )
    employee_id = fields.Many2one(
        string="Employee",
        comodel_name="hr.employee",
        readonly=True,
        help="Employee the workload is recapped for. Empty on the row "
        "that gathers the vacant lines of the planning.",
    )
    company_id = fields.Many2one(
        string="Company",
        comodel_name="res.company",
        readonly=True,
        help="Company of the manpower planning.",
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
    user_id = fields.Many2one(
        string="Responsible",
        comodel_name="res.users",
        readonly=True,
        help="User responsible for the manpower planning.",
    )
    state = fields.Selection(
        string="State",
        selection=[
            ("draft", "Draft"),
            ("confirm", "Waiting for Approval"),
            ("reject", "Rejected"),
            ("open", "On Progress"),
            ("done", "Done"),
            ("cancel", "Cancelled"),
        ],
        readonly=True,
        help="State of the manpower planning.",
    )
    teaching_hours = fields.Integer(
        string="Teaching Hours",
        readonly=True,
        help="Weekly hours of the teaching lines the employee teaches.",
    )
    co_teaching_count = fields.Integer(
        string="Co-Teaching Lines",
        readonly=True,
        help="Number of teaching lines the employee assists as co-teacher.",
    )
    assignment_weekly_hours = fields.Integer(
        string="Assignment Hours per Week",
        readonly=True,
        help="Hours of the additional assignments counted per week.",
    )
    assignment_daily_hours = fields.Integer(
        string="Assignment Hours per Day",
        readonly=True,
        help="Hours of the additional assignments counted per day.",
    )
    picket_weekly_hours = fields.Integer(
        string="Picket Hours per Week",
        readonly=True,
        help="Picket hours counted per day, multiplied by the picket "
        "hours per day of the school of the planning.",
    )
    co_teaching_hours = fields.Float(
        string="Co-Teaching Hours",
        readonly=True,
        help="Weekly hours of the teaching lines the employee assists as "
        "co-teacher, multiplied by the co-teaching hour factor of the "
        "school of the planning.",
    )
    total_weekly_hours = fields.Float(
        string="Total Weekly Hours",
        readonly=True,
        help="Teaching hours plus the co-teaching hours plus the "
        "additional assignment hours counted per week plus the picket "
        "hours per week.",
    )
    is_teacher = fields.Boolean(
        string="Is Teacher",
        readonly=True,
        help="Checked when the employee has at least one teaching line in "
        "the planning, as teacher or as co-teacher.",
    )
    mandatory_weekly_hours = fields.Integer(
        string="Mandatory Weekly Hours",
        readonly=True,
        help="Teacher mandatory weekly hours of the school of the "
        "planning. It is zero for an employee who does not teach.",
    )
    lack_weekly_hours = fields.Float(
        string="Lacking Weekly Hours",
        readonly=True,
        help="Mandatory weekly hours minus the total weekly hours, when "
        "positive. It is zero for an employee who does not teach, and "
        "when the school has no mandatory weekly hours.",
    )
    excess_weekly_hours = fields.Float(
        string="Excess Weekly Hours",
        readonly=True,
        help="Total weekly hours minus the mandatory weekly hours, when "
        "positive. It is zero for an employee who does not teach, and "
        "when the school has no mandatory weekly hours.",
    )

    @property
    def _table_query(self):
        """Return the SQL query that backs this view model.

        :return: SQL string selecting one row per planning and employee
        """
        return "%s %s %s" % (
            self._select(),
            self._from(),
            self._group_by(),
        )

    @api.model
    def _select(self):
        """Return the SELECT clause of the workload view.

        :return: SQL fragment selecting the hours summed per employee
        """
        select_str = """
        SELECT
            ROW_NUMBER() OVER (
                ORDER BY w.planning_id, w.employee_id
            ) AS id,
            w.planning_id AS planning_id,
            w.employee_id AS employee_id,
            p.company_id AS company_id,
            p.school_id AS school_id,
            p.academic_year_id AS academic_year_id,
            p.user_id AS user_id,
            p.state AS state,
            SUM(w.teaching_hours) AS teaching_hours,
            SUM(w.co_teaching_count) AS co_teaching_count,
            SUM(w.assignment_weekly_hours) AS assignment_weekly_hours,
            SUM(w.assignment_daily_hours) AS assignment_daily_hours,
            SUM(w.picket_daily_hours) * COALESCE(
                s.manpower_picket_weekly_hours_per_day, 1
            ) AS picket_weekly_hours,
            SUM(w.co_teaching_base_hours)::float * COALESCE(
                s.co_teaching_hour_factor, 0.5
            ) AS co_teaching_hours,
            %(total)s AS total_weekly_hours,
            SUM(w.teaching_line_count) > 0 AS is_teacher,
            %(mandatory)s AS mandatory_weekly_hours,
            CASE WHEN SUM(w.teaching_line_count) > 0
                AND COALESCE(s.teacher_mandatory_weekly_hours, 0) > 0
                THEN GREATEST(
                    %(mandatory)s::float - %(total)s, 0::float
                )
                ELSE 0::float
            END AS lack_weekly_hours,
            CASE WHEN SUM(w.teaching_line_count) > 0
                AND COALESCE(s.teacher_mandatory_weekly_hours, 0) > 0
                THEN GREATEST(
                    %(total)s - %(mandatory)s::float, 0::float
                )
                ELSE 0::float
            END AS excess_weekly_hours
        """
        return select_str % {
            "total": self._total_hours_sql(),
            "mandatory": self._mandatory_hours_sql(),
        }

    @api.model
    def _total_hours_sql(self):
        """Return the SQL expression of the total weekly hours.

        :return: SQL fragment summing the teaching, co-teaching,
            assignment and picket hours per week of one employee
        """
        return """(
            SUM(w.teaching_hours)::float
            + SUM(w.co_teaching_base_hours)::float * COALESCE(
                s.co_teaching_hour_factor, 0.5
            )
            + SUM(w.assignment_weekly_hours)
            + SUM(w.picket_daily_hours) * COALESCE(
                s.manpower_picket_weekly_hours_per_day, 1
            )
        )"""

    @api.model
    def _mandatory_hours_sql(self):
        """Return the SQL expression of the mandatory weekly hours.

        :return: SQL fragment giving the school mandatory hours for an
            employee who teaches, and zero for any other employee
        """
        return """(
            CASE WHEN SUM(w.teaching_line_count) > 0
                THEN COALESCE(s.teacher_mandatory_weekly_hours, 0)
                ELSE 0
            END
        )"""

    @api.model
    def _from(self):
        """Return the FROM clause of the workload view.

        The inner query unions the teaching lines (as teacher and as
        co-teacher) and the assignment lines, one row per line and
        employee, so the outer query only has to sum them. A teaching
        or assignment line without an employee is kept with an empty
        employee; a teaching line without a teacher does not make an
        employee a teacher. A line without a co-teacher adds no row.

        :return: SQL fragment joining the union to its planning
        """
        from_str = """
        FROM (
            SELECT
                t.planning_id AS planning_id,
                t.employee_id AS employee_id,
                COALESCE(t.total_weekly_hours, 0) AS teaching_hours,
                0 AS co_teaching_count,
                0 AS co_teaching_base_hours,
                CASE WHEN t.employee_id IS NULL THEN 0 ELSE 1 END
                    AS teaching_line_count,
                0 AS assignment_weekly_hours,
                0 AS assignment_daily_hours,
                0 AS picket_daily_hours
            FROM manpower_planning_teaching t
            UNION ALL
            SELECT
                t.planning_id AS planning_id,
                t.co_employee_id AS employee_id,
                0 AS teaching_hours,
                1 AS co_teaching_count,
                COALESCE(t.total_weekly_hours, 0) AS co_teaching_base_hours,
                1 AS teaching_line_count,
                0 AS assignment_weekly_hours,
                0 AS assignment_daily_hours,
                0 AS picket_daily_hours
            FROM manpower_planning_teaching t
            WHERE t.co_employee_id IS NOT NULL
            UNION ALL
            SELECT
                a.planning_id AS planning_id,
                a.employee_id AS employee_id,
                0 AS teaching_hours,
                0 AS co_teaching_count,
                0 AS co_teaching_base_hours,
                0 AS teaching_line_count,
                CASE WHEN a.hour_basis = 'week'
                    THEN COALESCE(a.hours, 0) ELSE 0
                END AS assignment_weekly_hours,
                CASE WHEN a.hour_basis = 'day'
                    THEN COALESCE(a.hours, 0) ELSE 0
                END AS assignment_daily_hours,
                CASE WHEN a.hour_basis = 'day' AND a.category = 'picket'
                    THEN COALESCE(a.hours, 0) ELSE 0
                END AS picket_daily_hours
            FROM manpower_planning_assignment a
        ) w
        JOIN manpower_planning p ON p.id = w.planning_id
        LEFT JOIN school s ON s.id = p.school_id
        """
        return from_str

    @api.model
    def _group_by(self):
        """Return the GROUP BY clause of the workload view.

        :return: SQL fragment grouping per planning and employee
        """
        group_by_str = """
        GROUP BY
            w.planning_id,
            w.employee_id,
            p.company_id,
            p.school_id,
            p.academic_year_id,
            p.user_id,
            p.state,
            s.manpower_picket_weekly_hours_per_day,
            s.co_teaching_hour_factor,
            s.teacher_mandatory_weekly_hours
        """
        return group_by_str
