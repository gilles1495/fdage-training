{
    "name": "C'cité - Family",
    "version": "15.0.1.0",
    "author": "Lucas Pfister",
    "category": "Custom",
    "depends": [
        'contacts'
    ],
    "license": "AGPL-3",
    "data": [
        "security/ir.model.access.csv",
        "views/partner_family_views.xml",
        "views/res_partner_views.xml"
    ],
    'assets': {
        'web.assets_backend': [
            'faal_family/static/src/scss/faal_family.scss'
        ]
    },
    'demo': [],
    'installable': True,
    'application': False,
    'auto_install': False
}
