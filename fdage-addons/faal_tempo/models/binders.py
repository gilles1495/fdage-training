from odoo import api, fields, models, modules


class Binders(models.Model):
    _name = 'binders'
    _description = ' Classeurs'

    code = fields.Char(string='Code')
    name = fields.Char(string='Nom')
    vendor_id = fields.Many2one('res.users', string='Vendeur')
    etablishement_id = fields.Many2one('etablishements', string='Etablissement')

    @api.onchange('vendor_id')
    def _swap_vendor_client(self):
        if self.ids and self.ids[0]:
            self_record_id = self.env['binders'].browse(self.ids[0])
            for user in self.env['res.partner'].search([('binder_id', '=', self_record_id.id)]):
                if self.vendor_id:
                    user.user_id = self.vendor_id.id
                else:
                    user.user_id = False
