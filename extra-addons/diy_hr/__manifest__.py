# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'DIY HR',
    'summary': '自定义组织管理模块',
    'description': """
    自定义组织管理模块
    """,
    'version': '1.1',
    'category': 'daibeisi',
    'images': [
        'static/src/img/default_image.png',
    ],
    'depends': ['base'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'wizard/create_user_wizard.xml',
        'wizard/edit_user_password_wizard.xml',
        'wizard/bind_user_wizard.xml',
        'views/inherit_res_user.xml',
        'views/employee.xml',
        'views/department.xml',
        'views/menu.xml',
    ],
    'demo': [
        # 'data/hr_demo.xml'
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'qweb': [],
    'license': 'LGPL-3',
}
