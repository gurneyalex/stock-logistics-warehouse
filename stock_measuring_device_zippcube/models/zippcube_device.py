# Copyright 2021 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)
import logging

from odoo import _, fields, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class ZippcubeDevice(models.Model):
    _name = "zippcube.device"
    _description = "Measuring Device Zippcube"
    _order = "warehouse_id, name"

    name = fields.Char("Name", required=True)
    warehouse_id = fields.Many2one("stock.warehouse", "Warehouse")

    _sql_constraints = [
        (
            "name_uniq",
            "unique (name)",
            "The name of the zippcube device must be unique.",
        ),
    ]

    def open_wizard(self):
        self.ensure_one()
        return {
            "name": _("Zippcube Wizard"),
            "res_model": "zippcube.wizard",
            "type": "ir.actions.act_window",
            "view_id": False,
            "view_mode": "form",
            "context": {"default_device_id": self.id},
            "target": "fullscreen",
            "flags": {
                "withControlPanel": False,
                "form_view_initial_mode": "edit",
                "no_breadcrumbs": True,
            },
        }

    def _is_being_used(self):
        """Returns whether the device is in use

        A device is in use if it has been assigned to a product packaging."""
        return bool(
            self.env["product.packaging"].search(
                [("scan_device_id", "=", self.id)], count=True, limit=1
            )
        )

    def _update_packaging_measures(self, measures):
        self.ensure_one()
        packaging = self.env["product.packaging"].search(
            [("scan_device_id", "=", self.id)], order="write_date DESC"
        )

        if len(packaging) == 0:
            error_msg = _(
                f"No package found pending a scan by this device {self.name}. "
                f"This could mean the selected product does not have this "
                f"kind of package set."
            )
            _logger.error(error_msg)
            raise UserError(error_msg)

        elif len(packaging) > 1:
            warning_msg = _(
                f"Several packagings ({packaging}) found to update by "
                f"device {self.name}. Will update the first: {packaging[0]}"
            )
            _logger.warning(warning_msg)
        packaging_to_update = packaging[0]

        wizard_line = self.env["zippcube.wizard.line"].search(
            [
                ("packaging_id", "=", packaging_to_update.id),
                ("wizard_id.device_id", "=", self.id),
                ("scan_requested", "=", True),
            ],
            order="write_date DESC",
            limit=1,
        )
        if not wizard_line:
            _logger.warning("No wizard line found for this measure.")
            packaging_to_update.write(
                {
                    "max_weight": measures["weight"],
                    "lngth": measures["length"],
                    "width": measures["width"],
                    "height": measures["height"],
                }
            )
        else:
            wizard_line.write(
                {
                    "lngth": measures["length"],
                    "width": measures["width"],
                    "height": measures["height"],
                    "max_weight": measures["weight"],
                    "scan_requested": False,
                }
            )
            wizard_line.wizard_id._notify(_("Please, press the REFRESH button."))

        packaging_to_update._clear_measuring_device()
        return packaging_to_update
