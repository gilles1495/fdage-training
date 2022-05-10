{
    "name": "C'Cité CRM rules",
    "version": "15.0.1.0",
    "author": "Lucas Pfister",
    "category": "Custom",
    "license": "AGPL-3",
    "depends": [
        'sale', 'ccite_def', 'ccite_crm',
    ],
    "data": [
        'views/crm_team_views.xml',
        'views/res_partner_views.xml',
        'views/sale_order_views.xml',
    ],
    'demo': [],
    'installable': True,
    'application': True,
    'auto_install': False
}
