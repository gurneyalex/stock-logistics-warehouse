# Copyright 2021 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)
import logging

from odoo import _, fields, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class MeasuringDevice(models.AbstractModel):
    _name = "measuring.device"
    _description = "Measuring and Weighing Device"
    _order = "warehouse_id, name"

    name = fields.Char("Name", required=True)
    warehouse_id = fields.Many2one("stock.warehouse", "Warehouse")
    device_type = fields.Selection(selection=[])

    _sql_constraints = [
        (
            "name_uniq",
            "unique (name)",
            "The name of the measuring/weighing device must be unique.",
        ),
    ]

    def _validate_packaging(self, packaging):
        self.ensure_one()
        if len(packaging) == 0:
            error_msg = _(
                "No package found pending a scan by this device {}. "
                "This could mean the selected product does not have this "
                "kind of package set.".format(self.name)
            )
            _logger.error(error_msg)
            raise UserError(error_msg)

        elif len(packaging) > 1:
            warning_msg = _(
                "Several packagings ({}) found to update by "
                "device {}. Will update the first: {}".format(
                    packaging, self.name, packaging[0]
                )
            )
            _logger.warning(warning_msg)
        return True
