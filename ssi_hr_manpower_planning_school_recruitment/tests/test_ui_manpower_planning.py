# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

# HttpSavepointCase -- NOT HttpCase. In 14.0 only SavepointCase prepares
# ``cls.env`` in ``setUpClass``, which is where the work instruction
# Pre-Condition below is built.
from odoo.tests import HttpSavepointCase, tagged


@tagged("post_install", "-at_install")
class TestUiManpowerPlanning(HttpSavepointCase):
    """Tour tests for the school recruitment extension of the planning."""

    @classmethod
    def setUpClass(cls):
        """Create one open school planning with a vacant teaching line.

        ``base.user_admin`` belongs to the validator and the "All" data
        ownership groups of ``manpower_planning`` and to the vacancy
        validator group, so it can run the tour and sees the fixture.
        The planning gets an explicit ``user_id`` so that the internal
        user record rule cannot hide it from the tour session.
        """
        super().setUpClass()
        env = cls.env
        admin = env.ref("base.user_admin")
        department = env["hr.department"].create({"name": "Tour MPPSR Dept"})
        env["hr.job"].create({"name": "Tour MPPSR Job"})
        grade_type = env["school_grade_type"].create(
            {"name": "Tour MPPSR Grade Type", "code": "/", "sequence": 10}
        )
        school = env["school"].create(
            {
                "name": "Tour MPPSR School",
                "code": "/",
                "grade_type_id": grade_type.id,
            }
        )
        grade = env["school_grade"].create(
            {
                "name": "Tour MPPSR Grade",
                "code": "/",
                "sequence": 10,
                "type_id": grade_type.id,
            }
        )
        grade_class = env["school_grade_class"].create(
            {
                "name": "Tour MPPSR Class",
                "code": "/",
                "school_id": school.id,
                "grade_id": grade.id,
            }
        )
        subject = env["school_subject"].create(
            {
                "name": "Tour MPPSR Subject",
                "code": "/",
                "grade_ids": [(6, 0, [grade.id])],
            }
        )
        cls.planning = (
            env["manpower_planning"]
            .with_user(admin)
            .create(
                {
                    "department_id": department.id,
                    "school_id": school.id,
                    "date_start": "2026-01-01",
                    "date_end": "2026-12-31",
                    "user_id": admin.id,
                    "teaching_ids": [
                        (
                            0,
                            0,
                            {
                                "subject_id": subject.id,
                                "grade_id": grade.id,
                                "grade_class_ids": [(6, 0, [grade_class.id])],
                                "weekly_hours": 2,
                            },
                        )
                    ],
                }
            )
        )
        # The policy fields guarding each button are computed against the
        # state written by the previous transition, so the cache is
        # dropped before every call.
        for method in ("action_confirm", "action_approve_approval"):
            cls.planning.invalidate_cache()
            getattr(cls.planning.with_user(admin), method)()
            cls.planning.invalidate_cache()

    def test_create_recruitment_vacancy(self):
        """Run the create recruitment vacancy tour with a teaching line.

        IK: docs/manpower_planning/16-create-recruitment-vacancy.md
        """
        self.start_tour(
            "/web",
            "ssi_hr_manpower_planning_school_recruitment_manpower_planning_create_recruitment_vacancy",  # noqa: B950
            login="admin",
        )
