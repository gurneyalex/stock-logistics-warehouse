# Copyright 2021 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

import logging

from odoo import _

from odoo.addons.component.core import Component

_logger = logging.getLogger(__name__)


class ZippcubeDevice(Component):
    _name = "zippcube.device.component"
    _inherit = "measuring.device.component"
    _usage = "zippcube"

    def _update_packaging_measures(self, measures):
        self.collection.ensure_one()
        packaging = self.env["product.packaging"].search(
            [("zippcube_device_id", "=", self.collection.id)], order="write_date DESC"
        )
        self._validate_packaging(packaging)
        packaging_to_update = packaging[0]

        self.env["measuring.wizard.line"].flush(
            ["packaging_id", "wizard_id", "scan_requested"]
        )
        self.env["measuring.wizard"].flush(["device_id"])
        wizard_line = self.collection.env["measuring.wizard.line"].search(
            [
                ("packaging_id", "=", packaging_to_update.id),
                (
                    "wizard_id.device_id",
                    "=",
                    "zippcube.device,{}".format(self.collection.id),
                ),
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

        packaging_to_update._release_measuring_device()
        return packaging_to_update
