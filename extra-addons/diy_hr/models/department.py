# -*- coding: utf-8 -*-
import logging
from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class Department(models.Model):
    _name = "diy.hr.department"
    _description = "部门"
    _order = "name"

    name = fields.Char(u'名称', required=True)
    code = fields.Char(string=u"编号")
    active = fields.Boolean(default=True)
    parent_id = fields.Many2one('diy.hr.department', string=u'上级部门')
    child_ids = fields.One2many('diy.hr.department', 'parent_id', string=u'下级部门', readonly=True)
    manager_id = fields.Many2one('diy.hr.employee', string=u'负责人')
    member_ids = fields.One2many('diy.hr.employee', 'dep_id', string=u'部门成员')

    _sql_constraints = [
        ("unique_name", "unique(name)", u"名称重复！")
    ]
