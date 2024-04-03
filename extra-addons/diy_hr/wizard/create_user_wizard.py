# -*- coding: utf-8 -*-
from odoo import models, fields, api, tools, _
from odoo.exceptions import UserError, Warning


class CreateUserWizard(models.TransientModel):

    _name = "diy.hr.create.user.wizard"
    _description = "创建用户"

    login = fields.Char(string=u"登录账号", required=True, size=20)
    password = fields.Char(string=u"登录密码", required=True, size=20)
    confirm_password = fields.Char(string=u"确认密码", required=True, size=20)

    def check_user_exist(self):
        user = self.env["res.users"].sudo().search([('login', '=', self.login)], limit=1)
        if user:
            raise UserError("登录账号已存在，请更改登录账号。")

    def create_res_user(self):
        """
        创建用户
        """
        self.ensure_one()
        if self.password != self.confirm_password:
            raise UserError(u"两次输入的密码不一致。")
        self.check_user_exist()
        res_model = self._context.get("active_model")
        res_id = self._context.get("active_id")
        employee = self.env[res_model].browse(res_id)
        user = self.env["res.users"].sudo().create({
            'name': employee.name,
            'login': self.login,
            'password': self.password,
            'employee_id': res_id,
            'groups_id': [(6, False, employee.group_ids.ids)]
        })
        employee.write({
            'user_id': user.id
        })