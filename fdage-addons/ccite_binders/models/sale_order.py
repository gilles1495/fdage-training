# -*- coding: UTF-8 -*-
from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'


#### A debugguer pour récupérer le classeur du partner sur le sale order

    #binder_id = fields.Many2one('binders', string=u'Classeur')
    #x_studio_classeur = fields.Many2one('binders', string=u'Classeur')
    binder_id = fields.Char(string='Classeur', related='partner_id.binder_id')
