# -*- coding: UTF-8 -*-
from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    coucou = fields.Char(string='Coucou')
