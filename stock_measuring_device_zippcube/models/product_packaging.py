from odoo import api, fields, models


class ProductPackaging(models.Model):
    _inherit = "product.packaging"

    scan_device_id = fields.Many2one(
        "zippcube.device",
        copy=False,
        string="Zippcube device which will scan the package",
        help="Technical field set when an operator uses the device "
        "to scan this package",
    )

    @api.model
    def _acquire_measuring_device(self):
        """Attempt to lock a scanning device

         Prevent that it can be assigned to any other product packaging."""
        self.env.cr.execute("SELECT scan_device_id FROM product_packaging FOR UPDATE")

    def _assign_measuring_device(self, device):
        self.ensure_one()
        self.scan_device_id = device

    def _clear_measuring_device(self):
        self.ensure_one()
        self.scan_device_id = False
