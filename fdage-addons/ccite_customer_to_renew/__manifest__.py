{
    "name": "C'Cite Customer to Renew",
    "version": "15.0.1.0",
    "author": "Lucas Pfister",
    "category": "Custom",
    "license": "AGPL-3",
    "depends": [
        'contacts', 'account', 'sale',
    ],
    "data": [
        'views/res_partner_views.xml',
        'data/cron.xml',
    ],
    'assets': {

    },
    'demo': [],
    'installable': True,
    'application': True,
    'auto_install': False
}
