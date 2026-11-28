# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import io
import re
import zipfile

from odoo_yaml_test import YamlTransactionCase

from odoo.tests import tagged

REPORT_NAME = "report.ssi_hr_manpower_planning.manpower_planning_summary"
XLSX_NAME = "report.ssi_hr_manpower_planning.manpower_planning_summary_xlsx"
ACTION_HTML = "ssi_hr_manpower_planning.action_report_manpower_planning_summary_html"
ACTION_PDF = "ssi_hr_manpower_planning.action_report_manpower_planning_summary_pdf"
TEACHING_RE = re.compile(r"<h5[^>]*>\s*(?:Teaching|Pengajaran)\s*</h5>")
CONTRACT_RE = re.compile(r"<h5[^>]*>\s*(?:Contract Review|Tinjauan Kontrak)\s*</h5>")


@tagged("post_install", "-at_install")
class TestManpowerPlanningSchoolReport(YamlTransactionCase):
    """Test the school sections of the manpower planning printout."""

    def setUp(self):
        """Create the school, employee and assignment type fixtures.

        ``YamlTransactionCase`` only provides ``self.env`` per test in
        ``setUp``, so the fixtures are built here and recreated for every
        test method.
        """
        super().setUp()
        env = self.env
        grade_type = env["school_grade_type"].create(
            {"name": "MPP Print Grade Type", "code": "/", "sequence": 10}
        )
        self.school = env["school"].create(
            {
                "name": "MPP Print School",
                "code": "/",
                "grade_type_id": grade_type.id,
                "teacher_mandatory_weekly_hours": 24,
            }
        )
        self.grade = env["school_grade"].create(
            {
                "name": "MPP Print Grade X",
                "code": "/",
                "sequence": 10,
                "type_id": grade_type.id,
            }
        )
        self.grade_class = env["school_grade_class"].create(
            {
                "name": "MPP Print X-1",
                "code": "/",
                "school_id": self.school.id,
                "grade_id": self.grade.id,
            }
        )
        self.subject = env["school_subject"].create(
            {
                "name": "MPP Print Mathematics",
                "code": "/",
                "grade_ids": [(6, 0, [self.grade.id])],
            }
        )
        self.year = env["school_academic_year"].create(
            {
                "name": "MPP Print Academic Year",
                "code": "/",
                "date_start": "2026-07-01",
                "date_end": "2027-06-30",
            }
        )
        self.department = env["hr.department"].create({"name": "MPP Print Department"})
        self.teacher = env["hr.employee"].create({"name": "MPP Print Teacher"})
        self.co_teacher = env["hr.employee"].create({"name": "MPP Print Co-Teacher"})
        self.clerk = env["hr.employee"].create({"name": "MPP Print Clerk"})
        self.job = env["hr.job"].create({"name": "MPP Print Job"})
        self.type_structural = env["manpower_planning_assignment_type"].create(
            {
                "name": "MPP Print Vice Principal",
                "code": "/",
                "category": "structural",
                "hour_basis": "week",
                "default_hours": 6,
            }
        )
        self.type_non_teacher = env["manpower_planning_assignment_type"].create(
            {
                "name": "MPP Print Librarian",
                "code": "/",
                "category": "non_teacher",
                "hour_basis": "week",
                "default_hours": 0,
            }
        )
        self.report_obj = env[REPORT_NAME]

    def _create_planning(self, with_school=True):
        """Create a planning of the department, with or without school.

        :param with_school: when true the planning gets the school and
            the academic year of the fixtures
        :return: the new ``manpower_planning`` record
        """
        values = {
            "department_id": self.department.id,
            "date_start": "2026-07-01",
            "date_end": "2027-06-30",
        }
        if with_school:
            values.update(
                {
                    "school_id": self.school.id,
                    "academic_year_id": self.year.id,
                }
            )
        return self.env["manpower_planning"].create(values)

    def _add_teaching(self, planning, teacher=None, co_teacher=None):
        """Add a one-class teaching line of 4 weekly hours.

        :param planning: planning that owns the line
        :param teacher: teacher of the line, vacant when empty
        :param co_teacher: co-teacher of the line, none when empty
        :return: the new ``manpower_planning_teaching`` record
        """
        return self.env["manpower_planning_teaching"].create(
            {
                "planning_id": planning.id,
                "subject_id": self.subject.id,
                "grade_id": self.grade.id,
                "grade_class_ids": [(6, 0, [self.grade_class.id])],
                "weekly_hours": 4,
                "employee_id": teacher and teacher.id or False,
                "co_employee_id": co_teacher and co_teacher.id or False,
            }
        )

    def _add_assignment(self, planning, assignment_type, employee=None, hours=6):
        """Add an additional assignment line.

        :param planning: planning that owns the line
        :param assignment_type: ``manpower_planning_assignment_type``
        :param employee: holder of the line, vacant when empty
        :param hours: hours of the line
        :return: the new ``manpower_planning_assignment`` record
        """
        return self.env["manpower_planning_assignment"].create(
            {
                "planning_id": planning.id,
                "type_id": assignment_type.id,
                "employee_id": employee and employee.id or False,
                "hours": hours,
            }
        )

    def _render_xlsx(self, plannings):
        """Render the planning workbook and open it as a zip archive.

        :param plannings: ``manpower_planning`` recordset to print
        :return: the opened ``zipfile.ZipFile`` of the workbook
        """
        report_xlsx = self.env[XLSX_NAME].with_context(active_model="manpower_planning")
        content, content_type = report_xlsx.create_xlsx_report(plannings.ids, {})
        self.assertEqual(content_type, "xlsx")
        return zipfile.ZipFile(io.BytesIO(content))

    def test_school_lines_of_a_planning(self):
        """Assert the helpers return the teaching, assignment and workload.

        Pure Python — trigger P1 (L-01: ``call`` discards the method
        return value, so the returned lists can't be asserted from
        YAML).
        """
        planning = self._create_planning()
        self._add_teaching(planning, self.teacher, self.co_teacher)
        self._add_assignment(planning, self.type_structural, self.teacher)
        teaching = self.report_obj._get_teaching_lines(planning)
        self.assertEqual(len(teaching), 1)
        self.assertEqual(teaching[0]["subject"], self.subject)
        self.assertEqual(teaching[0]["teacher"], self.teacher)
        self.assertEqual(teaching[0]["co_teacher"], self.co_teacher)
        self.assertEqual(teaching[0]["total_weekly_hours"], 4)
        self.assertFalse(teaching[0]["is_vacant"])
        assignment = self.report_obj._get_assignment_lines(planning)
        self.assertEqual(len(assignment), 1)
        self.assertEqual(assignment[0]["type"], self.type_structural)
        self.assertEqual(assignment[0]["category"], "Structural")
        self.assertEqual(assignment[0]["hour_basis"], "Per Week")
        self.assertEqual(assignment[0]["hours"], 6)
        workload = self.report_obj._get_workload_lines(planning)
        by_employee = {x["employee"].id: x for x in workload}
        self.assertEqual(len(workload), 2)
        self.assertEqual(by_employee[self.teacher.id]["teaching_hours"], 4)
        self.assertEqual(by_employee[self.teacher.id]["assignment_weekly_hours"], 6)
        self.assertEqual(by_employee[self.teacher.id]["mandatory_weekly_hours"], 24)
        self.assertAlmostEqual(
            by_employee[self.co_teacher.id]["co_teaching_hours"], 2.0, places=6
        )

    def test_planning_html_report_renders_school_sections(self):
        """Assert the QWeb report renders without error and has sections.

        Pure Python — trigger P8 (L-01: ``call`` discards the rendered
        bytes, so the HTML can't be asserted from YAML; L-19: the base
        class is locked to ``TransactionCase``, so report rendering
        can't reach an ``HttpCase``-only helper).
        """
        planning = self._create_planning()
        self._add_teaching(planning, self.teacher, self.co_teacher)
        self._add_assignment(planning, self.type_structural, self.teacher)
        report = self.env.ref(
            "ssi_hr_manpower_planning.action_report_manpower_planning_summary_html"
        )
        content, content_type = report._render_qweb_html([planning.id])
        html = content.decode("utf-8")
        self.assertEqual(content_type, "html")
        for title in (
            "School Recap",
            "Teaching</h5>",
            "Additional Assignments</h5>",
            "Workload</h5>",
        ):
            self.assertIn(title, html)

    def test_xlsx_has_school_sections_and_recap_sheet(self):
        """Assert the workbook has the three sections and the recap sheet.

        Pure Python — trigger P8 (L-01: ``call`` discards the rendered
        bytes, so the workbook can't be asserted from YAML; L-19: the
        base class is locked to ``TransactionCase``).
        """
        planning = self._create_planning()
        self._add_teaching(planning, self.teacher, self.co_teacher)
        self._add_assignment(planning, self.type_structural, self.teacher)
        archive = self._render_xlsx(planning)
        workbook = archive.read("xl/workbook.xml").decode("utf-8")
        strings = archive.read("xl/sharedStrings.xml").decode("utf-8")
        self.assertIn("School Recap", workbook)
        for title in ("Teaching", "Additional Assignments", "Workload"):
            self.assertIn("<t>%s</t>" % title, strings)

    def test_school_recap_merges_plannings_of_same_school_and_year(self):
        """Assert two plannings of one school and year share one group.

        Pure Python — trigger P1 (L-01: ``call`` discards the method
        return value) and P2 (L-04: the 50 percent fraction is checked
        with ``assertAlmostEqual``).
        """
        first = self._create_planning()
        self._add_teaching(first, self.teacher)
        self._add_assignment(first, self.type_structural)
        second = self._create_planning()
        self._add_teaching(second)
        recap = self.report_obj._get_school_recap(first | second)
        groups = {x["category"]: x for x in recap}
        self.assertEqual(len(recap), 2)
        self.assertEqual(groups["Teaching"]["school"], self.school)
        self.assertEqual(groups["Teaching"]["academic_year"], self.year)
        self.assertEqual(groups["Teaching"]["quantity_needed"], 2)
        self.assertEqual(groups["Teaching"]["quantity_filled"], 1)
        self.assertEqual(groups["Teaching"]["quantity_vacant"], 1)
        self.assertAlmostEqual(groups["Teaching"]["percent_filled"], 50.0, places=6)
        self.assertEqual(groups["Structural"]["quantity_needed"], 1)
        self.assertEqual(groups["Structural"]["quantity_vacant"], 1)
        values = self.report_obj._get_report_values((first | second).ids)
        self.assertEqual(len(values["school_recap"]), 2)

    def test_non_teacher_planning_has_no_teaching_section(self):
        """Assert a planning of non-teacher staff prints no teaching part.

        Pure Python — trigger P1 (L-01: ``call`` discards the method
        return value) and P8 (L-01: the rendered workbook bytes can't
        be asserted from YAML).
        """
        planning = self._create_planning()
        self.env["manpower_planning_formation"].create(
            {"planning_id": planning.id, "job_id": self.job.id, "quantity": 1}
        )
        self._add_assignment(planning, self.type_non_teacher, self.clerk, hours=0)
        self.assertEqual(self.report_obj._get_teaching_lines(planning), [])
        workload = self.report_obj._get_workload_lines(planning)
        self.assertEqual(len(workload), 1)
        self.assertEqual(workload[0]["employee"], self.clerk)
        self.assertEqual(workload[0]["lack_weekly_hours"], 0.0)
        self.assertEqual(workload[0]["excess_weekly_hours"], 0.0)
        doc = self.report_obj._get_report_values(planning.ids)["docs"][0]
        self.assertEqual(doc["teaching_lines"], [])
        archive = self._render_xlsx(planning)
        strings = archive.read("xl/sharedStrings.xml").decode("utf-8")
        self.assertNotIn("<t>Teaching</t>", strings)
        self.assertIn("<t>Workload</t>", strings)
        self.assertTrue(archive.read("xl/workbook.xml"))

    def test_planning_without_school_prints_as_the_base(self):
        """Assert a planning without school adds nothing to the printout.

        Pure Python — trigger P1 (L-01: ``call`` discards the method
        return value) and P8 (L-01: the rendered workbook bytes can't
        be asserted from YAML).
        """
        planning = self._create_planning(with_school=False)
        self.env["manpower_planning_formation"].create(
            {"planning_id": planning.id, "job_id": self.job.id, "quantity": 1}
        )
        doc = self.report_obj._get_report_values(planning.ids)["docs"][0]
        for key in (
            "teaching_lines",
            "assignment_lines",
            "workload_lines",
            "school_recap",
        ):
            self.assertEqual(doc[key], [])
        self.assertEqual(self.report_obj._get_school_recap(planning), [])
        archive = self._render_xlsx(planning)
        workbook = archive.read("xl/workbook.xml").decode("utf-8")
        strings = archive.read("xl/sharedStrings.xml").decode("utf-8")
        self.assertNotIn("School Recap", workbook)
        for title in ("Teaching", "Additional Assignments", "Workload"):
            self.assertNotIn("<t>%s</t>" % title, strings)
        report = self.env.ref(
            "ssi_hr_manpower_planning.action_report_manpower_planning_summary_html"
        )
        content, content_type = report._render_qweb_html(planning.ids)
        self.assertNotIn("School Recap", content.decode("utf-8"))

    def test_xlsx_sections_keep_the_base_order(self):
        """Assert the school sections sit right before the contract part.

        Pure Python — trigger P1 (L-01: ``call`` discards the method
        return value, so the returned list of names can't be asserted
        from YAML).
        """
        sections = self.env[XLSX_NAME]._get_xlsx_sections()
        self.assertEqual(
            sections,
            [
                "_write_xlsx_header",
                "_write_xlsx_summary",
                "_write_xlsx_category_recap",
                "_write_xlsx_teaching",
                "_write_xlsx_assignment",
                "_write_xlsx_workload",
                "_write_xlsx_contract",
            ],
        )

    def _install_lang(self, code):
        """Install a language with its translations loaded.

        :param code: language code to install, such as ``id_ID``
        """
        wizard = self.env["base.language.install"].create(
            {"lang": code, "overwrite": True}
        )
        wizard.lang_install()

    def _render_actions(self, planning, lang=None):
        """Render the HTML and PDF actions of a planning.

        In test mode the PDF action falls back to the HTML renderer,
        so no wkhtmltopdf is needed.

        :param planning: ``manpower_planning`` record to print
        :param lang: language code of the render context, if any
        :return: list of the two rendered HTML strings
        """
        result = []
        for xmlid, method in (
            (ACTION_HTML, "_render_qweb_html"),
            (ACTION_PDF, "_render_qweb_pdf"),
        ):
            report = self.env.ref(xmlid)
            if lang:
                report = report.with_context(lang=lang)
            content, content_type = getattr(report, method)(planning.ids)
            self.assertIn(content_type, ("html", "pdf"))
            result.append(content.decode("utf-8"))
        return result

    def test_reports_render_with_school_in_indonesian(self):
        """Assert both actions render the school planning in id_ID.

        Pure Python — trigger P8 (L-01: ``call`` discards the rendered
        bytes, so the HTML can't be asserted from YAML; L-19: the base
        class is locked to ``TransactionCase``).
        """
        self._install_lang("id_ID")
        planning = self._create_planning()
        self._add_teaching(planning, self.teacher, self.co_teacher)
        self._add_assignment(planning, self.type_structural, self.teacher)
        for html in self._render_actions(planning, lang="id_ID"):
            self.assertIn("Tinjauan Kontrak", html)
            teaching = TEACHING_RE.search(html)
            contract = CONTRACT_RE.search(html)
            self.assertTrue(teaching)
            self.assertTrue(contract)
            self.assertLess(teaching.start(), contract.start())

    def test_reports_render_without_school_in_indonesian(self):
        """Assert both actions render the base planning in id_ID.

        Pure Python — trigger P8 (L-01: ``call`` discards the rendered
        bytes, so the HTML can't be asserted from YAML; L-19: the base
        class is locked to ``TransactionCase``).
        """
        self._install_lang("id_ID")
        planning = self._create_planning(with_school=False)
        for html in self._render_actions(planning, lang="id_ID"):
            self.assertIn("Tinjauan Kontrak", html)
            self.assertFalse(TEACHING_RE.search(html))

    def test_reports_render_in_english(self):
        """Assert both actions render school and base plannings in en_US.

        Pure Python — trigger P8 (L-01: ``call`` discards the rendered
        bytes, so the HTML can't be asserted from YAML; L-19: the base
        class is locked to ``TransactionCase``).
        """
        school = self._create_planning()
        self._add_teaching(school, self.teacher, self.co_teacher)
        self._add_assignment(school, self.type_structural, self.teacher)
        for html in self._render_actions(school):
            self.assertIn("Contract Review", html)
            teaching = TEACHING_RE.search(html)
            contract = CONTRACT_RE.search(html)
            self.assertTrue(teaching)
            self.assertLess(teaching.start(), contract.start())
        base = self._create_planning(with_school=False)
        for html in self._render_actions(base):
            self.assertIn("Contract Review", html)
            self.assertFalse(TEACHING_RE.search(html))
