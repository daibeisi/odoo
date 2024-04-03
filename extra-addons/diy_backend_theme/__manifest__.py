# -*- coding: utf-8 -*-
{
    "name": "DIY Backend Theme",
    "description": """DIY Backend Theme""",
    "summary": "DIY Backend Theme",
    "category": "diy",
    "version": "16.0.1",
    'author': 'daibeisi',
    'website': "",
    "depends": ['base', 'web'],
    "data": [
        'views/layout.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'diy_backend_theme/static/src/xml/styles.xml',
            'diy_backend_theme/static/src/xml/top_bar.xml',
            'diy_backend_theme/static/src/scss/theme_accent.scss',
            'diy_backend_theme/static/src/scss/navigation_bar.scss',
            'diy_backend_theme/static/src/scss/datetimepicker.scss',
            'diy_backend_theme/static/src/scss/theme.scss',
            'diy_backend_theme/static/src/scss/sidebar.scss',
            'diy_backend_theme/static/src/js/sidebar_menu.js',
            'diy_backend_theme/static/src/js/user_menu.js',
            'diy_backend_theme/static/src/js/colors.js',
        ],
        'web.assets_frontend': [
            'diy_backend_theme/static/src/scss/login.scss',
        ],
    },
    'license': 'LGPL-3',
    'installable': True,
    'application': True,
    'auto_install': False,
}
