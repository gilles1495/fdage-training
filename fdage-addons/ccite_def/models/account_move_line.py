# -*- coding: utf-8 -*-

from odoo import api, fields, models, modules
from .utils import Utils


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    def _get_unit_price(self):
        for item in self:
            if item.discount and item.price_unit:
                item.unit_price_discount = item.price_unit - ((item.discount/100) * item.price_unit)
            else:
                item.unit_price_discount = item.price_unit if item.price_unit else 0.0

    dont_show_in_export = fields.Boolean(string=u'Cacher la ligne à l\'impression')
    unit_price_discount = fields.Float(string=u'Prix unitaire avec remise', compute='_get_unit_price')

    def _get_computed_name(self):
        self.ensure_one()

        if not self.product_id:
            return ''

        if self.partner_id.lang:
            product = self.product_id.with_context(lang=self.partner_id.lang)
        else:
            product = self.product_id

        values = []
        if product.partner_ref:
            values.append(product.name)
        if self.journal_id.type == 'sale':
            if product.description_sale:
                values.append(product.description_sale)
        elif self.journal_id.type == 'purchase':
            if product.description_purchase:
                values.append(product.description_purchase)
        return '\n'.join(values)
