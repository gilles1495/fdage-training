from odoo import api, fields, models, modules


class Etablishement(models.Model):
    _name = 'etablishements'
    _description = 'Etablissements'

    name = fields.Char(string=u'Nom')
    code = fields.Char(string=u'Code')

