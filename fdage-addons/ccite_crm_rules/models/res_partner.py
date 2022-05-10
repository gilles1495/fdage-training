# -*- coding: utf-8 -*-

from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    rule_prospect = fields.Html('Règles concernant les prospect', related='user_id.sale_team_id.rule_prospect')
    rule_customer = fields.Html('Règles concernant les clients', related='user_id.sale_team_id.rule_customer')
