from odoo import api, fields, models, modules


class AccountPaymentTerm(models.Model):
    _inherit = 'account.payment.term'

    code = fields.Char(string=u'Code')


