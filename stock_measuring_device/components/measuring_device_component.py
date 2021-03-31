# Copyright 2021 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

import logging

from odoo import _
from odoo.exceptions import UserError

from odoo.addons.component.core import AbstractComponent

_logger = logging.getLogger(__name__)


class MeasuringDevice(AbstractComponent):
    _name = "measuring.device.component"
    _collection = "measuring.device"

    def open_wizard(self):
        self.collection.ensure_one()
        return {
            "name": _("Measuring Device Wizard"),
            "res_model": "measuring.wizard",
            "type": "ir.actions.act_window",
            "view_id": False,
            "view_mode": "form",
            "context": {"default_device_id": self.collection.id},
            "target": "fullscreen",
            "flags": {
                "withControlPanel": False,
                "form_view_initial_mode": "edit",
                "no_breadcrumbs": True,
            },
        }

    def _is_being_used(self):
        """A device is in use if it has been assigned to a product packaging"""
        return bool(
            self.collection.env["product.packaging"].search_count(
                [("measuring_device_id", "=", self.collection.id)]
            )
        )

    def _validate_packaging(self, packaging):
        if len(packaging) == 0:
            error_msg = _(
                "No package found pending a scan by this device {}. "
                "This could mean the selected product does not have this "
                "kind of package set.".format(self.collection.name)
            )
            _logger.error(error_msg)
            raise UserError(error_msg)

        elif len(packaging) > 1:
            warning_msg = _(
                "Several packagings ({}) found to update by "
                "device {}. Will update the first: {}".format(
                    packaging, self.collection.name, packaging[0]
                )
            )
            _logger.warning(warning_msg)
        return True
