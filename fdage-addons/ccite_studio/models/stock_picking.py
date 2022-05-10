# -*- coding: UTF-8 -*-
from odoo import api, fields, models


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    partner_id_code = fields.Char(string='Code', compute='compute_partner_code')
    partner_id_name = fields.Char('Nom', related='partner_id.name')
    partner_id_zip = fields.Char('Code postal', related='partner_id.zip')
    partner_id_city = fields.Char('Ville', related='partner_id.city')

    def compute_partner_code(self):
        for record in self:
            if record.partner_id.parent_id.ref:
                record.partner_id_code = record.partner_id.parent_id.ref
            elif record.partner_id.ref:
                record.partner_id_code = record.partner_id.ref
            else:
                record.partner_id_code = ""
