from odoo import api, fields, models, modules


class ResUsers(models.Model):
    _inherit = 'res.users'

    prenom = fields.Char(string=u'Prénom')
    nom = fields.Char(string=u'Nom')


