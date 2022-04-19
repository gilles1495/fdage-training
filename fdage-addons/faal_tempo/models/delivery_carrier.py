from odoo import api, fields, models, modules


class DeliveryCarrier(models.Model):
    _inherit = 'delivery.carrier'

    code = fields.Char(string=u'Code')
