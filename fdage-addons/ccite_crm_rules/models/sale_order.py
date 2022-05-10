# -*- coding: utf-8 -*-

from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    rule_quotations = fields.Html('Règles concernant les devis', related='user_id.sale_team_id.rule_quotations')
    rule_sale_order = fields.Html('Règles concernant les commandes', related='user_id.sale_team_id.rule_sale_order')
