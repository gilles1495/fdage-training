from odoo import fields, models


class SaleReport(models.Model):
    _inherit = 'sale.report'

    wallet_period = fields.Char('Portefeuille', readonly=True)
    binder_id = fields.Many2one('binders', 'Classeur', readonly=True)

    def _query(self, with_clause='', fields={}, groupby='', from_clause=''):
        fields.update({
            'faal_tempo': ', s.wallet_period as wallet_period, partner.binder_id as binder_id'
        })
        groupby += ',s.wallet_period,partner.binder_id'
        return super()._query(with_clause=with_clause, fields=fields, groupby=groupby, from_clause=from_clause)
