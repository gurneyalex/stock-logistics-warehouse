# Copyright 2021 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)
import logging

from odoo import _, models

_logger = logging.getLogger(__name__)


class ZippcubeDevice(models.Model):
    _name = "zippcube.device"
    _inherit = "measuring.device"
    _description = "Measuring Device Zippcube"

    def open_wizard(self):
        self.ensure_one()
        return {
            "name": _("Zippcube Wizard"),
            "res_model": "measuring.wizard",
            "type": "ir.actions.act_window",
            "view_id": False,
            "view_mode": "form",
            "context": {"default_device_id": "{},{}".format(self._name, self.id)},
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
            self.env["product.packaging"].search_count(
                [("zippcube_device_id", "=", self.id)]
            )
        )

    def _update_packaging_measures(self, measures):
        self.ensure_one()
        packaging = self.env["product.packaging"].search(
            [("zippcube_device_id", "=", self.id)], order="write_date DESC"
        )
        self._validate_packaging(packaging)
        packaging_to_update = packaging[0]

        self.env["measuring.wizard.line"].flush(
            ["packaging_id", "wizard_id", "scan_requested"]
        )
        self.env["measuring.wizard"].flush(["device_id"])
        wizard_line = self.env["measuring.wizard.line"].search(
            [
                ("packaging_id", "=", packaging_to_update.id),
                ("wizard_id.device_id", "=", "zippcube.device,{}".format(self.id)),
                ("scan_requested", "=", True),
            ],
            order="write_date DESC",
            limit=1,
        )
        measures_vals = {
            "max_weight": measures["weight"],
            "lngth": measures["length"],
            "width": measures["width"],
            "height": measures["height"],
        }
        if not wizard_line:
            _logger.warning("No wizard line found for this measure.")
            packaging_to_update.write(measures_vals)
        else:
            measures_vals.update({"scan_requested": False})
            wizard_line.write(measures_vals)
            wizard_line.wizard_id._notify(_("Please, press the REFRESH button."))

        packaging_to_update._release_measuring_device(self)
        return packaging_to_update
