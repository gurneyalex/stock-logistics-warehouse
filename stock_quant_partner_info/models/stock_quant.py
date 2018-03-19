# -*- coding: utf-8 -*-
# © 2016 Oihane Crucelaegui - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import api, fields, models


class StockQuant(models.Model):
    _inherit = 'stock.quant'

    dest_partner_id = fields.Many2one(
        comodel_name='res.partner', compute='_compute_partner_id',
        string='Partner', store=True)

    @api.depends('location_id', 'history_ids')
    def _compute_partner_id(self):
        for quant in self:
            moves = quant.history_ids.sorted(key=lambda m: m.date)
            if moves:
                move = moves[-1]
                if move.location_id in ('customer', 'supllier'):
                    picking = move.picking_id
                    dest_partner = picking.partner_id.commercial_partner_id
                else:
                    dest_partner = False
            else:
                dest_partner = False
            quant.dest_partner_id = dest_partner
