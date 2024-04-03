import random
from odoo import api, fields, models
from odoo import tools, _
from odoo.exceptions import ValidationError


class Employee(models.Model):
    _name = "diy.hr.employee"
    _description = "员工"

    def _search_res_groups(self):
        # return [('category_id', '=', self.env.ref("hr_diy.module_kamax_category").id)]
        return []

    # 系统用户信息
    user_id = fields.Many2one('res.users', string=u'用户', ondelete='cascade')
    login = fields.Char(related='user_id.login', readonly=True)
    user_active = fields.Boolean(related='user_id.active', readonly=True)
    login_date = fields.Datetime(related='user_id.login_date', string=u'上次登录', readonly=True)

    # 基本信息
    name = fields.Char(string=u"名字")
    image = fields.Image('头像', max_width=1024, max_height=1024)
    position = fields.Char(string=u"职位")
    dep_id = fields.Many2one('diy.hr.department', string=u'所属部门')
    manage_department_ids = fields.One2many('diy.hr.department', 'manager_id',
                                            string=u'管理部门', readonly=True)
    birthday = fields.Date('生日')
    identification_id = fields.Char(string='身份证号')
    gender = fields.Selection([
        ('2', 'Male'),
        ('1', 'Female'),
        ('0', 'Other')
    ], string=u"性别")
    telephone = fields.Char(u'座机电话')
    mobile_phone = fields.Char(u'手机号码')
    work_email = fields.Char(u'电子邮箱')
    work_location = fields.Char(u'工作地点')
    group_ids = fields.Many2many("res.groups", 'hr_diy_employee_res_groups_rel',
                                 string=u"角色", domain=_search_res_groups)

    def write(self, vals):
        if vals.get("group_ids") and self.user_id:
            self.user_id.sudo().write({"groups_id": vals["group_ids"]})
        return super(Employee, self).write(vals)

    def toggle_active(self):
        for record in self:
            record.user_id.sudo().write({
                "active": not record.user_active
            })

    def unlink(self):
        return super().unlink()

