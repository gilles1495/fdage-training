# -*- coding: UTF-8 -*-
from odoo import api, fields, models


class PartnerFamily(models.Model):
    _name = 'partner.family'
    _description = 'Family from partners'

    name = fields.Char("Name")
    partner_ids = fields.One2many('family.role', 'family_id')
    family_members = fields.Integer(compute='_compute_family_total')

    @api.depends('partner_ids')
    def _compute_family_total(self):
        total = []
        for role in self.partner_ids:
            if role.family_role_id not in total:
                total.append(role.family_role_id)
            if role.family_role_to_id not in total:
                total.append(role.family_role_to_id)
        self.family_members = len(total)
