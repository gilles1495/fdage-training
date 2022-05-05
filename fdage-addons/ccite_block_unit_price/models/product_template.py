# -*- coding: UTF-8 -*-
from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    is_unit_price_editable = fields.Boolean()
