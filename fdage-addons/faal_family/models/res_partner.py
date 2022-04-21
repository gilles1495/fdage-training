# -*- coding: UTF-8 -*-
from odoo import api, fields, models,_


class ResPartner(models.Model):
    _inherit = 'res.partner'

    family_relation_ids = fields.One2many('family.role', 'family_role_id')
    family_relation_count = fields.Integer(compute='_family_relation_count')

    @api.depends('family_relation_ids')
    def _family_relation_count(self):
        self.family_relation_count = len(self.family_relation_ids)

    def family_relations(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Family Relations'),
            'res_model': 'family.role',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', self.family_relation_ids.ids)],
        }
