# Copyright 2021 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import _, api, fields, models


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

    def zippcube_select_for_measure(self):
        """Current line has been selected for measurement

        This implies that the device is acquired and locked,
        and the packaging is assigned the device."""
        self.ensure_one()
        success = True
        if not self.packaging_id:
            self.wizard_id._notify(_("This packaging is not set for the product."))
            success = False
        if self.wizard_id.device_id._is_being_used():
            self.wizard_id._notify(_("Measurement machine already in use."))
            success = False

        if success:
            self.scan_requested = True
            self.env["product.packaging"]._acquire_measuring_device()
            self.packaging_id._assign_measuring_device(self.wizard_id.device_id)
        return success

    def zippcube_select_for_measure_cancel(self):
        """Current line has been de-selected for measurement

        This implies that the packaging clears is assigned device."""
        self.ensure_one()
        self.scan_requested = False
        self.packaging_id._clear_measuring_device()
        return True
