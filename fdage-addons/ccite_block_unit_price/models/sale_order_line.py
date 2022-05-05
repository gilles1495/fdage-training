# -*- coding: UTF-8 -*-
from odoo import api, fields, models


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    product_reference = fields.Char(string='Reference', store=True, related='product_template_id.default_code')
    is_unit_price_editable = fields.Boolean(string='Is unit Price Editable By Salesman',
                                            related='product_template_id.is_unit_price_editable')
