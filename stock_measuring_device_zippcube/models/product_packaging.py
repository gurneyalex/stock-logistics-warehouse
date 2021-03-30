from odoo import api, fields, models


class ProductPackaging(models.Model):
    _inherit = "product.packaging"

    zippcube_device_id = fields.Many2one(
        "zippcube.device",
        copy=False,
        string="Zippcube device which will scan the package",
        help="Technical field set when an operator uses the device "
        "to scan this package",
    )

    @api.model
    def _acquire_measuring_device(self, device):
        if device._name == "zippcube.device":
            self.env.cr.execute(
                "SELECT zippcube_device_id FROM product_packaging FOR UPDATE"
            )
        else:
            super()._acquire_measuring_device(device)

    def _assign_measuring_device(self, device):
        self.ensure_one()
        if device._name == "zippcube.device":
            self.zippcube_device_id = device
        else:
            super()._assign_measuring_device(device)

    def _release_measuring_device(self, device):
        self.ensure_one()
        if device._name == "zippcube.device":
            self.zippcube_device_id = False
        else:
            super()._release_measuring_device(device)
