# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

# HttpSavepointCase, not HttpCase: in 14.0 only SavepointCase prepares
# ``cls.env`` in ``setUpClass``, which is where the Pre-Condition below is
# built.
from odoo.tests import HttpSavepointCase, tagged


def _create_open_curriculum(env, admin, school, year, grade, subject, title):
    """Create a school curriculum and bring it to On Progress.

    The policy fields guarding each button are computed against the state
    written by the previous transition, so the cache is dropped before
    every call. The approval of the curriculum opens it.

    :param env: the environment that creates the records
    :param admin: the ``res.users`` record that runs the transitions
    :param school: the ``school`` of the curriculum
    :param year: the ``school_academic_year`` of the curriculum
    :param grade: the ``school_grade`` of its line
    :param subject: the ``school_subject`` of its line
    :param title: the title of the curriculum
    :return: the ``school_curriculum`` record, On Progress
    """
    curriculum = (
        env["school_curriculum"]
        .with_user(admin)
        .create(
            {
                "title": title,
                "school_id": school.id,
                "academic_year_id": year.id,
                "effective_start": "2026-07-01",
                "effective_end": "2027-06-30",
                "user_id": admin.id,
                "line_ids": [
                    (
                        0,
                        0,
                        {
                            "subject_id": subject.id,
                            "grade_id": grade.id,
                            "weekly_hours": 4,
                            "total_class": 1,
                        },
                    )
                ],
            }
        )
    )
    for method in ("action_confirm", "action_approve_approval"):
        curriculum.invalidate_cache()
        getattr(curriculum.with_user(admin), method)()
        curriculum.invalidate_cache()
    return curriculum


@tagged("post_install", "-at_install")
class TestUiManpowerPlanning(HttpSavepointCase):
    """Tour tests for the school extension of ``manpower_planning``."""

    @classmethod
    def setUpClass(cls):
        """Create the master data the create tour picks from dropdowns.

        The Pre-Condition of the create work instruction asks for a
        department, a school with a grade and a class, a subject taught
        on that grade, an academic year, a teacher and an assignment type.
        The school also has a school curriculum that is On Progress, which
        fills the curriculum of the planning. Master data codes are ``/``
        (no unique code).
        """
        super().setUpClass()
        env = cls.env
        admin = env.ref("base.user_admin")
        env["hr.department"].create({"name": "Tour MPPS Dept"})
        grade_type = env["school_grade_type"].create(
            {"name": "Tour MPPS Grade Type", "code": "/", "sequence": 10}
        )
        school = env["school"].create(
            {
                "name": "Tour MPPS School",
                "code": "/",
                "grade_type_id": grade_type.id,
            }
        )
        grade = env["school_grade"].create(
            {
                "name": "Tour MPPS Grade",
                "code": "/",
                "sequence": 10,
                "type_id": grade_type.id,
            }
        )
        env["school_grade_class"].create(
            {
                "name": "Tour MPPS Class",
                "code": "/",
                "school_id": school.id,
                "grade_id": grade.id,
            }
        )
        subject = env["school_subject"].create(
            {
                "name": "Tour MPPS Subject",
                "code": "/",
                "grade_ids": [(6, 0, [grade.id])],
            }
        )
        year = env["school_academic_year"].create(
            {
                "name": "Tour MPPS Year",
                "code": "/",
                "date_start": "2026-07-01",
                "date_end": "2027-06-30",
            }
        )
        _create_open_curriculum(
            env, admin, school, year, grade, subject, "Tour MPPS Curriculum"
        )
        env["hr.employee"].create({"name": "Tour MPPS Teacher"})
        env["manpower_planning_assignment_type"].create(
            {
                "name": "Tour MPPS Type",
                "code": "/",
                "category": "structural",
                "hour_basis": "week",
                "default_hours": 6,
            }
        )

    def test_create(self):
        """Run the create tour of the school tabs of the planning.

        IK: docs/manpower_planning/01-create.md
        """
        self.start_tour(
            "/web",
            "ssi_hr_manpower_planning_school_manpower_planning_create",
            login="admin",
        )


@tagged("post_install", "-at_install")
class TestUiManpowerPlanningImport(HttpSavepointCase):
    """Tour test of the import of teaching lines from teaching assignments."""

    @classmethod
    def setUpClass(cls):
        """Create a draft school planning and one teaching assignment line.

        The Pre-Condition of the import work instruction asks for a draft
        planning with a school, and for a main teaching assignment line of
        the selected term in a homeroom of that school. The planning gets
        the academic year of the term and an explicit ``user_id`` so the
        internal user record rule cannot hide it from the tour session.
        """
        super().setUpClass()
        env = cls.env
        admin = env.ref("base.user_admin")
        grade_type = env["school_grade_type"].create(
            {"name": "Tour MPPI Grade Type", "code": "/", "sequence": 10}
        )
        school = env["school"].create(
            {
                "name": "Tour MPPI School",
                "code": "/",
                "grade_type_id": grade_type.id,
            }
        )
        grade = env["school_grade"].create(
            {
                "name": "Tour MPPI Grade",
                "code": "/",
                "sequence": 10,
                "type_id": grade_type.id,
            }
        )
        grade_class = env["school_grade_class"].create(
            {
                "name": "Tour MPPI Class",
                "code": "/",
                "school_id": school.id,
                "grade_id": grade.id,
            }
        )
        subject = env["school_subject"].create(
            {
                "name": "Tour MPPI Subject",
                "code": "/",
                "grade_ids": [(6, 0, [grade.id])],
            }
        )
        year = env["school_academic_year"].create(
            {
                "name": "Tour MPPI Year",
                "code": "/",
                "date_start": "2026-07-01",
                "date_end": "2027-06-30",
            }
        )
        term = env["school_academic_term"].create(
            {
                "name": "Tour MPPI Term",
                "code": "/",
                "date_start": "2026-07-01",
                "date_end": "2026-12-31",
                "year_id": year.id,
            }
        )
        homeroom = env["school_homeroom"].create(
            {
                "academic_year_id": year.id,
                "academic_term_id": term.id,
                "school_id": school.id,
                "grade_id": grade.id,
                "grade_class_id": grade_class.id,
            }
        )
        partner = env["res.partner"].create({"name": "Tour MPPI Teacher Home"})
        employee = env["hr.employee"].create(
            {
                "name": "Tour MPPI Teacher",
                "company_id": env.ref("base.main_company").id,
                "address_home_id": partner.id,
            }
        )
        teacher = env["school_teacher"].create(
            {"name": "Tour MPPI Teacher", "code": "/", "employee_id": employee.id}
        )
        assignment = env["school_teaching_assignment"].create(
            {
                "name": "Tour MPPI Assignment",
                "code": "/",
                "teacher_id": teacher.id,
                "academic_term_id": term.id,
            }
        )
        env["school_teaching_assignment_line"].create(
            {
                "assignment_id": assignment.id,
                "homeroom_id": homeroom.id,
                "subject_id": subject.id,
                "role": "main",
                "weekly_hours": 3,
            }
        )
        department = env["hr.department"].create({"name": "Tour MPPI Dept"})
        cls.planning = (
            env["manpower_planning"]
            .with_user(admin)
            .create(
                {
                    "department_id": department.id,
                    "school_id": school.id,
                    "academic_year_id": year.id,
                    "date_start": "2026-07-01",
                    "date_end": "2027-06-30",
                    "user_id": admin.id,
                }
            )
        )

    def test_import_teaching_assignment(self):
        """Run the import tour of the teaching lines of the planning.

        IK: docs/manpower_planning/17-import-teaching-assignment.md
        """
        self.start_tour(
            "/web",
            "ssi_hr_manpower_planning_school_manpower_planning_import_teaching_assignment",
            login="admin",
        )


@tagged("post_install", "-at_install")
class TestUiManpowerPlanningGenerate(HttpSavepointCase):
    """Tour test of the generation of teaching lines from a curriculum."""

    @classmethod
    def setUpClass(cls):
        """Create a draft school planning that follows a curriculum.

        The Pre-Condition of the generate work instruction asks for a
        draft planning whose curriculum is filled, a curriculum line, and
        a class of the planning school for the grade of that line. The
        curriculum is On Progress. The planning gets an explicit
        ``user_id`` so the internal user record rule cannot hide it from
        the tour session.
        """
        super().setUpClass()
        env = cls.env
        admin = env.ref("base.user_admin")
        grade_type = env["school_grade_type"].create(
            {"name": "Tour MPPG Grade Type", "code": "/", "sequence": 10}
        )
        school = env["school"].create(
            {
                "name": "Tour MPPG School",
                "code": "/",
                "grade_type_id": grade_type.id,
            }
        )
        grade = env["school_grade"].create(
            {
                "name": "Tour MPPG Grade",
                "code": "/",
                "sequence": 10,
                "type_id": grade_type.id,
            }
        )
        env["school_grade_class"].create(
            {
                "name": "Tour MPPG Class",
                "code": "/",
                "school_id": school.id,
                "grade_id": grade.id,
            }
        )
        subject = env["school_subject"].create(
            {
                "name": "Tour MPPG Subject",
                "code": "/",
                "grade_ids": [(6, 0, [grade.id])],
            }
        )
        year = env["school_academic_year"].create(
            {
                "name": "Tour MPPG Year",
                "code": "/",
                "date_start": "2026-07-01",
                "date_end": "2027-06-30",
            }
        )
        curriculum = _create_open_curriculum(
            env, admin, school, year, grade, subject, "Tour MPPG Curriculum"
        )
        department = env["hr.department"].create({"name": "Tour MPPG Dept"})
        cls.planning = (
            env["manpower_planning"]
            .with_user(admin)
            .create(
                {
                    "department_id": department.id,
                    "school_id": school.id,
                    "academic_year_id": year.id,
                    "curriculum_id": curriculum.id,
                    "date_start": "2026-07-01",
                    "date_end": "2027-06-30",
                    "user_id": admin.id,
                }
            )
        )

    def test_generate_teaching_from_curriculum(self):
        """Run the generate tour of the teaching lines of the planning.

        IK: docs/manpower_planning/18-generate-teaching-from-curriculum.md
        """
        self.start_tour(
            "/web",
            "ssi_hr_manpower_planning_school_manpower_planning_generate_curriculum",
            login="admin",
        )
