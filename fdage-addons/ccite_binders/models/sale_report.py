# -*- coding: UTF-8 -*-
from odoo import api, fields, models


class SaleReport(models.Model):
    _inherit = 'sale.report'

    binder_id = fields.Many2one(string='Classeur', related='partner_id.binder_id', store=True)

    def _query(self, with_clause='', fields={}, groupby='', from_clause=''):
        fields.update({
            'ccite_binders': ', partner.binder_id as binder_id'
        })
        groupby += ',partner.binder_id'
        return super()._query(with_clause=with_clause, fields=fields, groupby=groupby, from_clause=from_clause)
