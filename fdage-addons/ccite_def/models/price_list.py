from odoo import api, fields, models, modules


class PriceList(models.Model):
    _inherit = 'product.pricelist'

    code = fields.Char(string=u'Code')


