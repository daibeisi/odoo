# -*- coding: utf-8 -*-
# from odoo import http


# class ProduceUnit(http.Controller):
#     @http.route('/produce_unit/produce_unit', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/produce_unit/produce_unit/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('produce_unit.listing', {
#             'root': '/produce_unit/produce_unit',
#             'objects': http.request.env['produce_unit.produce_unit'].search([]),
#         })

#     @http.route('/produce_unit/produce_unit/objects/<model("produce_unit.produce_unit"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('produce_unit.object', {
#             'object': obj
#         })
