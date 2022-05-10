# -*- coding: utf-8 -*-

from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    type_global = fields.Char(string='Type global', compute='compute_type_global')

    def compute_type_global(self):
        for record in self:
            if record.is_company:
                record.type_global = 'Entreprise'
            else:
                if record.type == 'contact':
                    record.type_global = "Contact"
                elif record.type == 'delivery':
                    record.type_global = "Adresse de livraison"
                elif record.type == 'invoice':
                    record.type_global = "Adresse de facturation"
                else:
                    record.type_global = "Autre"
