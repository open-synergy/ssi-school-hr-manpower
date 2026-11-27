# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


# Extends the school with the picket hours counted per picket day. The
# manpower planning workload multiplies the daily picket hours of an
# employee by this value to get the weekly picket hours.
class School(models.Model):
    _name = "school"
    _inherit = ["school"]

    manpower_picket_weekly_hours_per_day = fields.Integer(
        string="Picket Hours per Day",
        default=1,
        help="Weekly lesson hours counted for each picket day. The "
        "manpower planning workload multiplies the picket days of an "
        "employee by this value.",
    )

    @api.constrains("manpower_picket_weekly_hours_per_day")
    def _check_manpower_picket_weekly_hours_per_day(self):
        """Reject a negative number of picket hours per day.

        :raises ValidationError: when the value is below zero
        """
        for record in self:
            if record.manpower_picket_weekly_hours_per_day < 0:
                error_message = """
Document Type: %s
Context: Save school
Database ID: %s
Problem: Picket hours per day is negative
Solution: Set picket hours per day to zero or more
""" % (
                    self._description.lower(),
                    record.id,
                )
                raise ValidationError(_(error_message))
