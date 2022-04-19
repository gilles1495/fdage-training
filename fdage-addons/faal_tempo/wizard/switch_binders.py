# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class SwitchBinders(models.TransientModel):
    _name = 'switch.binders'
    _description = 'Echange de classeur'

    binders_id = fields.Many2one('binders', string='Classeur', required=1)
    res_partners_ids = fields.Many2many('res.partner', 'binders_rel', 'id', 'partner_id', string='Utilisateurs')

    def switch_binders(self):
        self.ensure_one()

        for res_partner in self.res_partners_ids:
            res_partner.binder_id = self.binders_id.id
