# -*- coding: UTF-8 -*-
from odoo import api, fields, models, modules, _


class Partner(models.Model):
    _inherit = 'res.partner'
    _rec_name = 'display_name'

    binder_id = fields.Many2one('binders', string=u'Classeur')

    def swap_binders(self):
        return {
            'name': _('Choisir un classeur'),
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'switch.binders',
            'view_id': self.env.ref('ccite_binders.view_switch_binders_form').id,
            'type': 'ir.actions.act_window',
            'context': {
                'default_res_partners_ids': self.ids,
            },
            'target': 'new'
        }
