# -*- coding: UTF-8 -*-
from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    family_relation_ids = fields.One2many('family.role', 'family_role_id')
