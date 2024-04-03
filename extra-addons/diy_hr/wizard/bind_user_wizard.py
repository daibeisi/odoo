# -*- coding: utf-8 -*-
from odoo import models, fields, api, tools, _
from odoo.exceptions import ValidationError, Warning
import datetime


class BindUserWizard(models.TransientModel):
    _name = "diy.hr.bind.user.wizard"
    _description = "绑定用户"

    def _search_res_users(self):
        # return [('groups_id', 'not in', self.env.ref("base.group_system").id), ('employee_id', '=', False)]
        return []

    user_id = fields.Many2one("res.users", string=u"用户", required=True, domain=_search_res_users)

    def bind_user(self, values):
        """
        绑定用户
        """
        self.ensure_one()
        res_model = values.get("active_model")
        res_id = values.get("active_id")
        employee = self.env[res_model].browse(res_id)
        employee.write({
            'user_id': self.user_id.id
        })
        self.user_id.write({
            'employee_id': employee.id,
            'groups_id': [(6, False, employee.group_ids.ids)]
        })
