{
    "name": "Fédération des Aveugles GE",
    "version": "1.1.0",
    "author": "TeMPO Consulting",
    "category": "Custom",
    "depends": [
        'web', 'board', 'calendar', 'contacts', 'base_automation', 'account_accountant',
        'sale', 'purchase', 'sale_management', 'delivery', 'l10n_fr_siret', 'web_map',
        'stock', 'account', 'mrp', 'partner_credit_limit', 'purchase_discount', 'account_followup', 'ccite_binders',
    ],
    "data": [
        'security/ir.model.access.csv',
        'data/res_country_data.xml',
        'data/cron.xml',
        'data/crm_team.xml',
        'data/res_partner_title.xml',
        'data/account.account.xml',
        'data/payment_terms.xml',
        'data/etablishement.xml',
        'data/my_company.xml',
        'data/product_category.xml',
        'data/delivery_carrier.xml',
        'views/res_partner.xml',
        'views/sale_order.xml',
        # 'views/binders.xml',
        # 'wizard/switch_binders.xml',
        'views/account_move_lines.xml',
        'report/report.xml',
        'report/report_sale_order.xml',
        'report/delivery_report.xml',
        'report/report_picking.xml',
        'report/account_report_invoice.xml',
        'report/report_expedition_ticket.xml',
        # 'report/report_doeth.xml',
        'report/repere_purchase_order.xml',
        'views/stock_picking.xml',
        'report/report_dpd.xml',
        'report/purchase_order_repere.xml',
        'report/report_sale_order_repere.xml',
        'report/account_report_repere_invoice.xml',
        'report/delivery_repere_report.xml',
        'report/report_repere_picking.xml',
        'report/account_report_invoice_esat.xml',
        'report/report_sale_order_esat.xml',
        'report/sale_report_views.xml',
        'report/purchase_order.xml',
        'report/report_sale_order_proforma_repere_invoice.xml',
        'report/report_followup.xml',
        'views/l10n_form_inherith_view.xml',
    ],
    'demo': [],
    'installable': True,
    'application': True,
    'auto_install': False
}
