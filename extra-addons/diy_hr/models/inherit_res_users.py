# -*- coding: utf-8 -*-
from odoo import api, models, fields


class User(models.Model):

    _inherit = ['res.users']

    employee_id = fields.Many2one("diy.hr.employee", string=u"员工")

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            vals['tz'] = 'Asia/Shanghai'
            vals['lang'] = 'zh_CN'
        users = super(User, self).create(vals_list)
        return users
