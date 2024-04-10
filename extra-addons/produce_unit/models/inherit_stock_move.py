# -*- coding: utf-8 -*-

from odoo import models, fields, api


class StockMove(models.Model):
    _inherit = 'stock.move'

    @api.depends('product_id')
    def _compute_product_uom(self):
        for move in self:
            move.product_uom = move.product_id.produce_unit_id.id or move.product_id.uom_id.id