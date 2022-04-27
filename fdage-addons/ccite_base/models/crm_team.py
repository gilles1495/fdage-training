# -*- coding: UTF-8 -*-
from odoo import api, fields, models


class CrmTeam(models.Model):
    _inherit = 'crm.team'

    brand_id = fields.Many2one('res.partner')
    brand_template = fields.Selection([('apt', 'Aveugles Pole Travail'), ('reperes', 'Repères')])


