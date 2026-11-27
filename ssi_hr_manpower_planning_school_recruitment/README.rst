.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

=============================================
HR - Manpower Planning - School - Recruitment
=============================================

Glue between the school manpower planning (MPP) of ``ssi_hr_manpower_planning_school``
and the vacancy request wizard of ``ssi_hr_manpower_planning_recruitment``. When the HR
user requests recruitment vacancies from a running school planning, the wizard also
proposes one line per vacant teaching line (a line without a teacher) that has no
vacancy yet, with its subject, weekly lesson hours and number of classes. The user
selects the teacher job position once and the wizard creates one draft vacancy per line.
A vacancy created from a teaching line records the subject, the weekly hours and the
number of classes, and can be grouped by subject.

This module is installed automatically when both modules it connects are installed.


Work Instruction
================

* `Create Recruitment Vacancy from Manpower Planning <docs/manpower_planning/index.html>`_


Installation
============

To install this module, you need to:

1.  Clone the branch 14.0 of the repository https://github.com/open-synergy/ssi-hr-manpower-planning
2.  Add the path to this repository in your configuration (addons-path)
3.  Update the module list (Must be on developer mode)
4.  Go to menu *Apps -> Apps -> Main Apps*
5.  Search For *HR - Manpower Planning - School - Recruitment*
6.  Install the module


Bug Tracker
===========

Bugs are tracked on `GitHub Issues
<https://github.com/open-synergy/ssi-hr-manpower-planning/issues>`_. In case of trouble, please
check there if your issue has already been reported. If you spotted it first,
help us smash it by providing detailed and welcomed feedback.


Credits
=======

Contributors
------------

* Andhitia Rama <andhitia.r@gmail.com>

Maintainer
----------

.. image:: https://simetri-sinergi.id/logo.png
   :alt: PT. Simetri Sinergi Indonesia
   :target: https://simetri-sinergi.id

This module is maintained by the PT. Simetri Sinergi Indonesia.
