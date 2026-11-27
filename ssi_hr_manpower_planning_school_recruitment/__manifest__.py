# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
# pylint: disable=C8101
{
    "name": "HR - Manpower Planning - School - Recruitment",
    "version": "14.0.1.0.2",
    "website": "https://simetri-sinergi.id",
    "author": "OpenSynergy Indonesia, PT. Simetri Sinergi Indonesia",
    "license": "AGPL-3",
    "installable": True,
    "auto_install": True,
    "application": False,
    "depends": [
        "ssi_hr_manpower_planning_school",
        "ssi_hr_manpower_planning_recruitment",
        "web_tour",
    ],
    "data": [
        "views/recruitment_vacancy.xml",
        "wizards/create_recruitment_vacancy_from_manpower_planning.xml",
        "views/assets.xml",
    ],
    "demo": [],
}
