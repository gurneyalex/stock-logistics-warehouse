# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import fields, models


class StockWarehouse(models.Model):
    _inherit = "stock.warehouse"

    zippcube_device_ids = fields.One2many(
        "zippcube.device", "warehouse_id", string="Zippcube Devices"
    )
