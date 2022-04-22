{
    "name": "C'Cite Binders",
    "version": "15.0.0.1.0",
    "author": "Lucas Pfister",
    "category": "Custom",
    "depends": [
        'web', 'contacts', 'sale', 'sale_management',
    ],
    "data": [
        'security/ir.model.access.csv',
        'views/binders.xml',
        'views/sale_order_views.xml',
        'views/res_partner_views.xml',
        'wizard/switch_binders.xml',
    ],
    'assets': {

    },
    'demo': [],
    'installable': True,
    'application': True,
    'auto_install': False
}
