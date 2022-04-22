# -*- coding: UTF-8 -*-
from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    binder_id = fields.Many2one(string='Classeur', related='partner_id.binder_id')
