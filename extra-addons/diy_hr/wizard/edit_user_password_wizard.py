# -*- coding: utf-8 -*-
from odoo import models, fields, api, tools, _
from odoo.exceptions import UserError


class EditUserPasswordWizard(models.TransientModel):

    _name = "diy.hr.edit.user.password.wizard"
    _description = "更改密码"

    user_id = fields.Many2one("res.users", string=u"用户", required=True)
    password = fields.Char(string=u"登录密码", required=True)
    confirm_password = fields.Char(string=u"确认密码", required=True)

    def check_user_exist(self):
        for record in self:
            user = self.env["res.users"].sudo().search([('login', '=', record.user_id.login)], limit=1)
            if user:
                raise UserError(u"登录账号已存在，请更改登录账号。")

    def edit_password(self):
        self.ensure_one()
        if self.password != self.confirm_password:
            raise UserError(u"两次输入的密码不一致。")
        self.check_user_exist()
        self.user_id.write({
            'password': self.password
        })

