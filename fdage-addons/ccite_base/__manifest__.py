{
    "name": "C'Cité Base",
    "version": "15.0.1.0",
    "author": "Lucas Pfister",
    "category": "Custom",
    "depends": [
        'web', 'board', 'calendar', 'contacts', 'base_automation', 'account_accountant',
        'sale', 'purchase', 'sale_management', 'delivery', 'l10n_fr_siret', 'web_map',
        'stock', 'account', 'mrp', 'partner_credit_limit', 'purchase_discount', 'account_followup', 'faal_tempo',
    ],
    "data": [
        'views/crm_team_views.xml',
        'report/report_sale_order.xml',
    ],
    'demo': [],
    'installable': True,
    'application': True,
    'auto_install': False
}
