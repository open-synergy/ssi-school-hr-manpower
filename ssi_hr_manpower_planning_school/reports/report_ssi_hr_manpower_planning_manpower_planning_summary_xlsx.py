# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, models

REPORT_NAME = "report.ssi_hr_manpower_planning.manpower_planning_summary"


# Extends the manpower planning summary workbook of
# ``ssi_hr_manpower_planning`` with the Teaching, Additional
# Assignments and Workload sections, written before the contract
# section, and with a "School Recap" worksheet. A section without lines
# writes nothing, and the recap worksheet is added only when a printed
# planning has a school, so a planning without school data is printed as
# before.
class ReportSsiHrManpowerPlanningManpowerPlanningSummaryXlsx(models.AbstractModel):
    _name = "report.ssi_hr_manpower_planning.manpower_planning_summary_xlsx"
    _inherit = ["report.ssi_hr_manpower_planning.manpower_planning_summary_xlsx"]

    @api.model
    def _get_xlsx_sections(self):
        """Return the worksheet sections in the order they are written.

        The school sections are placed right before the contract
        section of the base.

        :return: list of method names, one per worksheet section
        :rtype: list
        """
        sections = super()._get_xlsx_sections()
        school_sections = [
            "_write_xlsx_teaching",
            "_write_xlsx_assignment",
            "_write_xlsx_workload",
        ]
        if "_write_xlsx_contract" in sections:
            index = sections.index("_write_xlsx_contract")
        else:
            index = len(sections)
        return sections[:index] + school_sections + sections[index:]

    def generate_xlsx_report(self, workbook, data, plannings):
        """Write the planning worksheets and the school recap worksheet.

        :param workbook: ``xlsxwriter.Workbook`` to write into
        :param data: unused, present for the abstract report contract
        :param plannings: ``manpower_planning`` recordset to render
        :return: nothing; the output is the side effect on ``workbook``
        """
        super().generate_xlsx_report(workbook, data, plannings)
        report_obj = self.env[REPORT_NAME]
        recap = report_obj._get_school_recap(plannings)
        if recap:
            self._write_xlsx_school_recap_sheet(workbook, recap)

    def _write_xlsx_school_recap_sheet(self, workbook, recap):
        """Write the "School Recap" worksheet.

        :param workbook: ``xlsxwriter.Workbook`` to write into
        :param recap: list returned by ``_get_school_recap``
        :return: nothing; the output is the side effect on ``workbook``
        """
        formats = self._get_xlsx_formats(workbook)
        sheet = workbook.add_worksheet(_("School Recap"))
        sheet.set_column(0, 1, 28)
        sheet.set_column(2, 7, 18)
        sheet.write(0, 0, _("SCHOOL RECAP"), formats["title"])
        headers = [
            _("School"),
            _("Academic Year"),
            _("Category"),
            _("Needed"),
            _("Filled"),
            _("Vacant"),
            _("Filled (%)"),
            _("Vacant (%)"),
        ]
        row = 2
        for column, header in enumerate(headers):
            sheet.write(row, column, header, formats["header"])
        row += 1
        for line in recap:
            sheet.write(row, 0, line["school"].name or "", formats["cell"])
            sheet.write(row, 1, line["academic_year"].name or "", formats["cell"])
            sheet.write(row, 2, line["category"], formats["cell"])
            sheet.write_number(row, 3, line["quantity_needed"], formats["number"])
            sheet.write_number(row, 4, line["quantity_filled"], formats["number"])
            sheet.write_number(row, 5, line["quantity_vacant"], formats["number"])
            sheet.write_number(row, 6, line["percent_filled"], formats["percent"])
            sheet.write_number(row, 7, line["percent_vacant"], formats["percent"])
            row += 1

    def _write_xlsx_teaching(self, sheet, row, planning, formats):
        """Write the teaching lines table, or nothing when empty.

        :param sheet: worksheet of the planning
        :param row: first row to write
        :param planning: a single ``manpower_planning`` record
        :param formats: cell formats from :meth:`_get_xlsx_formats`
        :return: the next free row
        :rtype: int
        """
        lines = self.env[REPORT_NAME]._get_teaching_lines(planning)
        if not lines:
            return row
        sheet.write(row, 0, _("Teaching"), formats["title"])
        row += 1
        headers = [
            _("Subject"),
            _("Grade"),
            _("Classes"),
            _("Weekly Hours per Class"),
            _("Total Classes"),
            _("Total Weekly Hours"),
            _("Teacher"),
            _("Co-Teacher"),
        ]
        for column, header in enumerate(headers):
            sheet.write(row, column, header, formats["header"])
        row += 1
        for line in lines:
            sheet.write(row, 0, line["subject"].name or "", formats["cell"])
            sheet.write(row, 1, line["grade"].name or "", formats["cell"])
            sheet.write(row, 2, line["classes"], formats["cell"])
            sheet.write_number(row, 3, line["weekly_hours"], formats["number"])
            sheet.write_number(row, 4, line["total_class"], formats["number"])
            sheet.write_number(row, 5, line["total_weekly_hours"], formats["number"])
            sheet.write(row, 6, line["teacher"].name or _("Vacant"), formats["cell"])
            sheet.write(row, 7, line["co_teacher"].name or "", formats["cell"])
            row += 1
        return row + 1

    def _write_xlsx_assignment(self, sheet, row, planning, formats):
        """Write the additional assignments table, or nothing when empty.

        :param sheet: worksheet of the planning
        :param row: first row to write
        :param planning: a single ``manpower_planning`` record
        :param formats: cell formats from :meth:`_get_xlsx_formats`
        :return: the next free row
        :rtype: int
        """
        lines = self.env[REPORT_NAME]._get_assignment_lines(planning)
        if not lines:
            return row
        sheet.write(row, 0, _("Additional Assignments"), formats["title"])
        row += 1
        headers = [
            _("Assignment Type"),
            _("Category"),
            _("Hour Basis"),
            _("Employee"),
            _("Hours"),
            _("Number of Classes"),
        ]
        for column, header in enumerate(headers):
            sheet.write(row, column, header, formats["header"])
        row += 1
        for line in lines:
            sheet.write(row, 0, line["type"].name or "", formats["cell"])
            sheet.write(row, 1, line["category"], formats["cell"])
            sheet.write(row, 2, line["hour_basis"], formats["cell"])
            sheet.write(row, 3, line["employee"].name or _("Vacant"), formats["cell"])
            sheet.write_number(row, 4, line["hours"], formats["number"])
            sheet.write_number(row, 5, line["class_count"], formats["number"])
            row += 1
        return row + 1

    def _write_xlsx_workload(self, sheet, row, planning, formats):
        """Write the workload per employee table, or nothing when empty.

        :param sheet: worksheet of the planning
        :param row: first row to write
        :param planning: a single ``manpower_planning`` record
        :param formats: cell formats from :meth:`_get_xlsx_formats`
        :return: the next free row
        :rtype: int
        """
        lines = self.env[REPORT_NAME]._get_workload_lines(planning)
        if not lines:
            return row
        sheet.write(row, 0, _("Workload"), formats["title"])
        row += 1
        headers = [
            _("Employee"),
            _("Teaching Hours"),
            _("Co-Teaching Hours"),
            _("Assignment Hours per Week"),
            _("Picket Hours per Week"),
            _("Total Weekly Hours"),
            _("Mandatory Weekly Hours"),
            _("Lacking Weekly Hours"),
            _("Excess Weekly Hours"),
        ]
        for column, header in enumerate(headers):
            sheet.write(row, column, header, formats["header"])
        row += 1
        for line in lines:
            sheet.write(row, 0, line["employee_label"], formats["cell"])
            sheet.write_number(row, 1, line["teaching_hours"], formats["number"])
            sheet.write_number(row, 2, line["co_teaching_hours"], formats["percent"])
            sheet.write_number(
                row, 3, line["assignment_weekly_hours"], formats["number"]
            )
            sheet.write_number(row, 4, line["picket_weekly_hours"], formats["number"])
            sheet.write_number(row, 5, line["total_weekly_hours"], formats["percent"])
            sheet.write_number(
                row, 6, line["mandatory_weekly_hours"], formats["number"]
            )
            sheet.write_number(row, 7, line["lack_weekly_hours"], formats["percent"])
            sheet.write_number(row, 8, line["excess_weekly_hours"], formats["percent"])
            row += 1
        return row + 1
