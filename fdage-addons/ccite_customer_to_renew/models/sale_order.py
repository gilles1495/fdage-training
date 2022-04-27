# -*- coding: utf-8 -*-

from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def action_confirm(self):
        result = super(SaleOrder, self).action_confirm()
        self.partner_id.customer_to_renew = False
        return result
