# Copyright 2021 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)
from odoo import api, models


class ProductPackaging(models.Model):
    _inherit = "product.packaging"

    @api.model
    def _acquire_measuring_device(self, device):
        """Lock the measuring device for other product packaging

        Intended to be extended. Each package defines a set of specific
        measuring devices and depending on device._name it uses one
        or other implementation by calling super()"""
        pass

    def _assign_measuring_device(self, device):
        """Assign the measuring device to the current product packaging

        Intended to be extended. Each package defines a set of specific
        measuring devices and depending on device._name it uses one
        or other implementation by calling super()"""
        self.ensure_one()
        pass

    def _release_measuring_device(self, device):
        """Free the measuring device from the current product packaging

        Intended to be extended. Each package defines a set of specific
        measuring devices and depending on device._name it uses one
        or other implementation by calling super()"""
        self.ensure_one()
        pass
