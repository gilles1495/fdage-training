# -*- coding: UTF-8 -*-
from odoo import api, fields, models


class CrmTeam(models.Model):
    _inherit = 'crm.team'

    rule_quotations = fields.Html('Règles concernant les devis')
    rule_sale_order = fields.Html('Règles concernant les commandes')
    rule_prospect = fields.Html('Règles concernant les prospect')
    rule_customer = fields.Html('Règles concernant les clients')
