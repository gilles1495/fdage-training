{
    "name": "C'Cite Doeth",
    "version": "15.0.0.1.0",
    "author": "Lucas Pfister",
    "category": "Custom",
    "depends": [
        'web', 'board', 'calendar', 'contacts', 'base_automation', 'account_accountant',
        'sale', 'purchase', 'sale_management', 'delivery', 'l10n_fr_siret', 'web_map',
        'stock', 'account', 'mrp', 'partner_credit_limit', 'purchase_discount', 'account_followup',
    ],
    "data": [
        'security/ir.model.access.csv',
        'report/report.xml',
        'report/report_doeth.xml',
    ],
    'assets': {
    },
    'demo': [],
    'installable': True,
    'application': True,
    'auto_install': False
}
