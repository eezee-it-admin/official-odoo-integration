# -*- coding: utf-8 -*-
{
    'name': 'MultiSafepay payments',

    'description': '''
        Accept, manage and stimulate online sales with MultiSafepay.
        Increase conversion rates with MultiSafepay unique solutions,
        create the perfect checkout experience and the best payment method mix.
        ''',

    'summary': '''E-commerce is part of our DNA''',

    'author': 'MultiSafepay',
    'website': 'http://www.multisafepay.com',

    'license': 'Other OSI approved licence',

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'eCommerce',
    'version': '1.1.1',

    # any module necessary for this one to work correctly
    'depends': ['payment', 'sale', 'delivery'],
    'external_dependencies': {'python': ['multisafepay']},

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/payment_views.xml',
        'views/payment_templates.xml',
        'views/account_move_views.xml',

        'data/payment_acquirer.xml',
        'data/payment_icon.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    'images': ['static/description/main.png'],
    'installable': True,
    'application': True,
    'auto_install': False,
}
