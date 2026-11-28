# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
#
# Migration: 14.0.1.6.2 -> 14.0.1.7.0
#
# Changes: the stored header quantities of a school manpower planning
#          (needed, filled, vacant) now count the teaching and the
#          additional assignment lines too. Values already stored only
#          counted the formation lines and do not follow by themselves.

import logging

from openupgradelib import openupgrade

_logger = logging.getLogger(__name__)

QUANTITY_FIELDS = ["quantity_needed", "quantity_filled", "quantity_vacant"]


@openupgrade.migrate()
def migrate(env, version):
    """Recompute the stored header quantities of every manpower planning.

    :param env: the migration environment
    :param version: the version being migrated to (unused)
    :return: nothing; recomputes the quantity fields of all plannings
    """
    plannings = env["manpower_planning"].with_context(active_test=False).search([])
    for field_name in QUANTITY_FIELDS:
        env.add_to_compute(plannings._fields[field_name], plannings)
    plannings.flush(QUANTITY_FIELDS)
    _logger.info(
        "Recomputed header quantities on %s manpower planning(s).",
        len(plannings),
    )
