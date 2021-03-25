# Copyright 2021 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class ZippcubeWizardLine(models.TransientModel):
    _name = "zippcube.wizard.line"
    _description = "Zippcube Wizard Line"
    _order = "sequence"

    scan_requested = fields.Boolean()
    wizard_id = fields.Many2one("zippcube.wizard")
    sequence = fields.Integer()
    name = fields.Char("Packaging", readonly=True)
    qty = fields.Float("Quantity")
    max_weight = fields.Float("Weight (kg)", readonly=True)
    # this is not a typo:
    # https://github.com/odoo/odoo/issues/41353#issuecomment-568037415
    lngth = fields.Integer("Length (mm)", readonly=True)
    width = fields.Integer("Width (mm)", readonly=True)
    height = fields.Integer("Height (mm)", readonly=True)
    volume = fields.Float(
        "Volume (m³)",
        digits=(8, 4),
        compute="_compute_volume",
        readonly=True,
        store=False,
    )
    barcode = fields.Char("GTIN")
    packaging_id = fields.Many2one(
        "product.packaging", string="Packaging (rel)", readonly=True
    )
    packaging_type_id = fields.Many2one("product.packaging.type", readonly=True,)
    required = fields.Boolean(related="packaging_type_id.required", readonly=True)

    @api.depends("lngth", "width", "height")
    def _compute_volume(self):
        for line in self:
            line.volume = (line.lngth * line.width * line.height) / 1000.0 ** 3

    def zippcube_measure(self):
        self.ensure_one()
        self.scan_requested = True
        self.packaging_id.scan_device_id = self.wizard_id.device_id
        return True
