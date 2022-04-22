# -*- coding: UTF-8 -*-
from odoo import api, fields, models


class SaleReport(models.Model):
    _inherit = 'sale.report'

    binder_id = fields.Many2one(string='Classeur', related='partner_id.binder_id')
