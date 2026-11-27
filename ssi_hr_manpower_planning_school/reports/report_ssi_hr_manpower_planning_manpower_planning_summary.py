# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, models


# Extends the manpower planning summary report of
# ``ssi_hr_manpower_planning`` with the school sections: the teaching
# lines, the additional assignments, the workload per employee and the
# recap per school and academic year. A planning without school data
# gets empty lists, so nothing is added to its printout.
class ReportSsiHrManpowerPlanningManpowerPlanningSummary(models.AbstractModel):
    _name = "report.ssi_hr_manpower_planning.manpower_planning_summary"
    _inherit = ["report.ssi_hr_manpower_planning.manpower_planning_summary"]

    @api.model
    def _get_field_label(self, model_name, field_name, value):
        """Return the display label of a selection value.

        :param model_name: technical name of the model of the field
        :param field_name: name of the selection field
        :param value: technical value of the selection
        :return: label of the selection value, or the value itself when
            the selection has no such key
        :rtype: str
        """
        field = self.env[model_name]._fields[field_name]
        labels = dict(field._description_selection(self.env))
        return labels.get(value, value or "")

    def _get_teaching_lines(self, planning):
        """Return the teaching lines of a planning.

        :param planning: a single ``manpower_planning`` record
        :return: list of dicts with the keys ``subject``, ``grade``,
            ``classes``, ``weekly_hours``, ``total_class``,
            ``total_weekly_hours``, ``teacher``, ``co_teacher`` and
            ``is_vacant``; empty list when the planning has no
            teaching line
        :rtype: list
        """
        result = []
        for line in planning.teaching_ids.sorted("id"):
            result.append(
                {
                    "subject": line.subject_id,
                    "grade": line.grade_id,
                    "classes": ", ".join(line.grade_class_ids.mapped("name")),
                    "weekly_hours": line.weekly_hours,
                    "total_class": line.total_class,
                    "total_weekly_hours": line.total_weekly_hours,
                    "teacher": line.employee_id,
                    "co_teacher": line.co_employee_id,
                    "is_vacant": line.is_vacant,
                }
            )
        return result

    def _get_assignment_lines(self, planning):
        """Return the additional assignment lines of a planning.

        :param planning: a single ``manpower_planning`` record
        :return: list of dicts with the keys ``type``, ``category``
            (label), ``hour_basis`` (label), ``employee``, ``hours``,
            ``class_count`` and ``is_vacant``; empty list when the
            planning has no assignment line
        :rtype: list
        """
        result = []
        for line in planning.assignment_ids.sorted("id"):
            result.append(
                {
                    "type": line.type_id,
                    "category": self._get_field_label(
                        "manpower_planning_assignment",
                        "category",
                        line.category,
                    ),
                    "hour_basis": self._get_field_label(
                        "manpower_planning_assignment",
                        "hour_basis",
                        line.hour_basis,
                    ),
                    "employee": line.employee_id,
                    "hours": line.hours,
                    "class_count": line.class_count,
                    "is_vacant": line.is_vacant,
                }
            )
        return result

    def _get_workload_lines(self, planning):
        """Return the workload per employee of a planning.

        The row that gathers the lines without an employee is labelled
        "Vacant".

        :param planning: a single ``manpower_planning`` record
        :return: list of dicts with the keys ``employee``,
            ``employee_label``, ``teaching_hours``,
            ``co_teaching_hours``, ``assignment_weekly_hours``,
            ``picket_weekly_hours``, ``total_weekly_hours``,
            ``mandatory_weekly_hours``, ``lack_weekly_hours`` and
            ``excess_weekly_hours``; empty list when the planning has
            no teaching or assignment line
        :rtype: list
        """
        for model_name in (
            "manpower_planning",
            "manpower_planning_teaching",
            "manpower_planning_assignment",
            "school",
        ):
            self.env[model_name].flush()
        workloads = self.env["manpower_planning_workload"].search(
            [("planning_id", "=", planning.id)],
            order="employee_id",
        )
        result = []
        for workload in workloads:
            result.append(
                {
                    "employee": workload.employee_id,
                    "employee_label": workload.employee_id.name or _("Vacant"),
                    "teaching_hours": workload.teaching_hours,
                    "co_teaching_hours": workload.co_teaching_hours,
                    "assignment_weekly_hours": workload.assignment_weekly_hours,
                    "picket_weekly_hours": workload.picket_weekly_hours,
                    "total_weekly_hours": workload.total_weekly_hours,
                    "mandatory_weekly_hours": workload.mandatory_weekly_hours,
                    "lack_weekly_hours": workload.lack_weekly_hours,
                    "excess_weekly_hours": workload.excess_weekly_hours,
                }
            )
        return result

    def _get_school_recap(self, plannings):
        """Return the manpower recap per school, year and category.

        The figures are the sums of the summary rows of every printed
        planning that has a school, grouped per school, academic year
        and category. The percentages are computed from those sums, not
        averaged over the rows.

        :param plannings: ``manpower_planning`` recordset to recap
        :return: list of dicts with the keys ``school``,
            ``academic_year``, ``category`` (label),
            ``quantity_needed``, ``quantity_filled``,
            ``quantity_vacant``, ``percent_filled`` and
            ``percent_vacant``; empty list when no planning has a
            school
        :rtype: list
        """
        self.env["manpower_planning_formation"].flush()
        for model_name in (
            "manpower_planning",
            "manpower_planning_teaching",
            "manpower_planning_assignment",
        ):
            self.env[model_name].flush()
        summaries = self.env["manpower_planning_summary"].search(
            [
                ("planning_id", "in", plannings.ids),
                ("school_id", "!=", False),
            ],
            order="school_id, academic_year_id, category",
        )
        totals = {}
        for summary in summaries:
            key = (
                summary.school_id,
                summary.academic_year_id,
                summary.category,
            )
            total = totals.setdefault(key, {"needed": 0, "filled": 0, "vacant": 0})
            total["needed"] += summary.quantity_needed
            total["filled"] += summary.quantity_filled
            total["vacant"] += summary.quantity_vacant
        result = []
        for key, total in totals.items():
            school, year, category = key
            result.append(
                {
                    "school": school,
                    "academic_year": year,
                    "category": self._get_category_label(category),
                    "quantity_needed": total["needed"],
                    "quantity_filled": total["filled"],
                    "quantity_vacant": total["vacant"],
                    "percent_filled": self._get_percent(
                        total["filled"], total["needed"]
                    ),
                    "percent_vacant": self._get_percent(
                        total["vacant"], total["needed"]
                    ),
                }
            )
        return result

    @api.model
    def _get_report_values(self, docids, data=None):
        """Add the school sections to the rendering context.

        :param docids: ids of the ``manpower_planning`` records to print
        :param data: unused, present for the report engine signature
        :return: the dict of the base with, in each doc, the keys
            ``teaching_lines``, ``assignment_lines``, ``workload_lines``
            and ``school_recap`` (the recap of that planning), and at
            the top level ``school_recap`` of all printed plannings
        """
        result = super()._get_report_values(docids, data=data)
        for doc in result["docs"]:
            planning = doc["planning"]
            doc["teaching_lines"] = self._get_teaching_lines(planning)
            doc["assignment_lines"] = self._get_assignment_lines(planning)
            doc["workload_lines"] = self._get_workload_lines(planning)
            doc["school_recap"] = self._get_school_recap(planning)
        plannings = self.env["manpower_planning"].browse(docids)
        result["school_recap"] = self._get_school_recap(plannings)
        return result
