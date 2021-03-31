# Copyright 2021 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)
from odoo import api, fields, models


class ProductPackaging(models.Model):
    _inherit = "product.packaging"

    measuring_device_id = fields.Many2one(
        "measuring.device",
        copy=False,
        string="Measuring device which will scan the package",
        help="Technical field set when an operator uses the device "
        "to scan this package",
    )

    @api.model
    def _acquire_measuring_device(self):
        """Lock the measuring device for other product packaging"""
        self.env.cr.execute(
            "SELECT measuring_device_id FROM product_packaging FOR UPDATE"
        )

    def _assign_measuring_device(self, device):
        """Assign the measuring device to the current product packaging"""
        self.ensure_one()
        self.measuring_device_id = device

    def _release_measuring_device(self):
        """Free the measuring device from the current product packaging"""
        self.ensure_one()
        self.measuring_device_id = False
