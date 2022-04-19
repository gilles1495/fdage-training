from odoo import fields, models
import datetime


class ReportDOETH(models.TransientModel):
    _name = 'report.doeth'
    _description = 'Création de rapport DOETH'

    partner_id = fields.Many2one(
        'res.partner',
        string="Client",
    )
    invoices_names = fields.Char("Factures")
    subtotal_without_shipping = fields.Float("Sous-total")
    year = fields.Integer("Année")

    def get_president_name(self):
        president_name = "Gabriel Reeb"
        company_id = self.env['res.partner'].search([
            ('name', 'like', '%Fédération des Aveugles Alsace Lorraine%')
        ])
        if company_id:
            company_id = company_id[0]
            president_id = self.env['res.partner'].search([
                ('parent_id', '=', company_id.id),
                ('type', '=', 'contact'),
                ('function', '=', 'Président')
            ])
            if president_id:
                president_id = president_id[0]
                president_name = president_id.name
        return president_name

    def get_client_info(self, search):
        value = ''
        if search == 'name':
            value = self.partner_id.name
        elif search == 'street':
            if self.partner_id.street:
                value = self.partner_id.street
            if self.partner_id.street2 and value:
                value += ' ' + self.partner_id.street
        elif search == 'zip':
            if self.partner_id.zip:
                value = self.partner_id.zip
            if self.partner_id.city:
                value += ' ' + self.partner_id.city
        return value

    @staticmethod
    def get_date():
        date = datetime.datetime.now()
        month_name = {
            1: 'janvier',
            2: 'février',
            3: 'mars',
            4: 'avril',
            5: 'mai',
            6: 'juin',
            7: 'juillet',
            8: 'août',
            9: 'septembre',
            10: 'octobre',
            11: 'novembre',
            12: 'décembre',
        }
        return f'{date.day} {month_name[date.month]} {date.year}'
