{
    "name": "C'Cité CRM Rights",
    "version": "15.0.1.0",
    "author": "Lucas Pfister",
    "category": "Custom",
    "license": "AGPL-3",
    "depends": [
        'sale', 'mail', 'ccite_def',
    ],
    "data": [
        "security/ir_rules.xml",
        "security/crm_security.xml",
        "security/crm_security_rules.xml",
        "views/product_views.xml",
        "views/res_partner_views.xml",
    ],
    'demo': [],
    'installable': True,
    'application': True,
    'auto_install': False
}
