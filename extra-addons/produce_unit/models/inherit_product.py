# -*- coding: utf-8 -*-

from odoo import models, fields, api


class InheritProduct(models.Model):
    _inherit = "product.template"

    sku = fields.Char(string='库存单位', compute='_compute_sku', readonly=True)

    def _compute_sku(self):
        for record in self:
            uom_objects = self.env['uom.uom'].search([])
            record.sku = ",".join([uom_object.name for uom_object in uom_objects])

    uom_category_id = fields.Many2one('uom.category', 'Uom Category', related="uom_id.category_id")
    produce_unit_id = fields.Many2one('uom.uom', '生产单位', domain=[("category_id", "=", uom_category_id)])

    @api.model_create_multi
    def create(self, vals_list):
        # 在创建记录时，设置默认的department_id
        # vals['department_id'] = self.env.context.get('default_department_id')
        records = super(InheritProduct, self).create(vals_list)
        return records


