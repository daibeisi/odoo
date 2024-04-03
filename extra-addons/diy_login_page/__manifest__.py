# -*- coding: utf-8 -*-
{
    'name': "DIY login page",
    'summary': """ DIY 登录页面模块 """,
    'description': """
        DIY 登录页面模块
    """,
    'author': "daibeisi",
    'website': "",
    'category': 'daibeisi',
    'version': '1.0',
    'depends': ['web'],
    # always loaded
    'data': [
        'views/login.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'diy_login_page/static/src/css/login.css',
        ],
        'web.assets_backend_prod_only': [
            'diy_login_page/static/src/js/user_menu.js',
        ],
    },

}
