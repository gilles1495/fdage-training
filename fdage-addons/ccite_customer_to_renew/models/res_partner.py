# -*- coding: utf-8 -*-

from odoo import api, fields, models

from dateutil.relativedelta import relativedelta


class ResPartner(models.Model):
    _inherit = 'res.partner'

    customer_to_renew = fields.Boolean()

    def _set_customer_to_renew(self):
        partner_ids = self.env['res.partner'].search(
            [('is_company', '=', True), ('supplier_rank', '=', 0), ('customer_to_renew', '=', False)])
        current_date = fields.datetime.now()
        index = 0
        for partner in partner_ids:
            index += 1
            if partner.sale_order_ids.filtered(lambda so: so.state in ['sent', 'sale', 'done']):
                last_order = partner.sale_order_ids.filtered(lambda so: so.state in ['sent', 'sale', 'done']).sorted('date_order', reverse=True)[0]
                last_order_plus_three_years = last_order.date_order + relativedelta(years=3)
                if last_order_plus_three_years < current_date:
                    partner.customer_to_renew = True
            else:
                partner.customer_to_renew = True
            if index % 200 == 0:
                self._cr.commit()
