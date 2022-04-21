# -*- coding: UTF-8 -*-
from odoo import api, fields, models


class FamilyRole(models.Model):
    _name = 'family.role'
    _description = 'Family role relation'

    family_id = fields.Many2one('partner.family', required=True)
    family_type = fields.Selection([('father', 'Father'), ('mother', 'Mother'), ('brother', 'Brother'), ('sister', 'Sister')], required=True)
    family_role_id = fields.Many2one('res.partner', required=True)
    family_role_to_id = fields.Many2one('res.partner', required=True)
    family_role_to_name = fields.Char(string='Name', related='family_role_to_id.name')