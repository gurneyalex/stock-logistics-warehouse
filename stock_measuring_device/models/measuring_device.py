# Copyright 2021 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)
import logging

from odoo import fields, models

_logger = logging.getLogger(__name__)


class MeasuringDevice(models.Model):
    _name = "measuring.device"
    _inherit = "collection.base"
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

    def _forward(self, method, *args, **kwargs):
        _logger.debug(
            "Measuring Device ID: %s type %s > %s : %s %s",
            self.id,
            self.device_type,
            method,
            args,
            kwargs,
        )
        self.ensure_one()
        measuring_device = self._get_measuring_device()
        return getattr(measuring_device, method)(*args, **kwargs)

    def _get_measuring_device(self):
        with self.work_on(self._name) as work:
            return work.component(usage=self.device_type)

    def open_wizard(self):
        with self.work_on(self._name) as work:
            return work.component(usage=self.device_type)

    # def _is_being_used(self):
    #     with self.work_on(self._name) as work:
    #         return work.component(usage=self.device_type)
    #
    # def _validate_packaging(self, packaging):
    #     with self.work_on(self._name) as work:
    #         return work.component(usage=self.device_type)
