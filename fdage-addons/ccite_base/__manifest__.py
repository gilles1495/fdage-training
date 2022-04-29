{
    "name": "C'Cité Base",
    "version": "15.0.1.0",
    "author": "Lucas Pfister",
    "category": "Custom",
    "license": "AGPL-3",
    "depends": [
        'web', 'board', 'calendar', 'contacts', 'base_automation', 'account_accountant',
        'sale', 'purchase', 'sale_management', 'delivery', 'l10n_fr_siret', 'web_map',
        'stock', 'account', 'mrp', 'partner_credit_limit', 'purchase_discount', 'account_followup', 'ccite_def',
    ],
    "data": [
        'views/crm_team_views.xml',
        'report/report_sale_order.xml',
    ],
    "assets": {
        "web.assets_backend": [
             "/ccite_base/static/src/css/faal_contact.css",
             "/ccite_base/static/src/js/widgets/faal_contact.js",
        ]
    },
    'demo': [],
    'installable': True,
    'application': True,
    'auto_install': False
}
