# Copyright 2021 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import api, models


class MeasuringWizard(models.TransientModel):
    _inherit = "measuring.wizard"

    @api.model
    def _select_device_id(self):
        """Retrieve available specific devices"""
        res = super()._select_device_id()
        res.append(("zippcube.device", "Zippcube Device"))
        return res
