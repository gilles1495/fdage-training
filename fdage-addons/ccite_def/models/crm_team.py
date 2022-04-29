from odoo import api, fields, models, modules


class CrmTeam(models.Model):
    _inherit = 'crm.team'

    code = fields.Char(string=u'Code')
    establishment_id = fields.Many2one('etablishements', 'Etablissement')
