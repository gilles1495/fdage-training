# -*- coding: utf-8 -*-
from odoo import api, fields, models, modules, _
from odoo.exceptions import UserError, ValidationError
import base64


class Utils(models.Model):
    _name = 'faal_tempo.utils'
    _description = 'Tempo Utils'

    def search_adress(self, item, search):
        value = ''
        if search == 'name' and item.name:
            value += item.name
        if search == 'street' and item.street:
            value += item.street
        if search == 'street2' and item.street2:
            value += item.street2
        if search == 'postal' and item.zip:
            value += item.zip + '    ' + item.city
        if search == 'phone' and item.phone:
            value += item.phone
        if search == 'parent_ref':
            if item.parent_id and item.parent_id.ref:
                value += item.parent_id.ref
        return value

    def get_adress(self, adress_type, search=False, is_delivery=False):
        adresse = ''
        if self.partner_id:
            search_partner_id = self.partner_id.id
            if is_delivery and self.partner_id.parent_id:
                search_partner_id = self.partner_id.parent_id.id

            if search_partner_id:
                adresse_records = self.env['res.partner'].search([('parent_id', '=', search_partner_id), ('type', '=', adress_type)])
                if len(adresse_records) > 1:
                    adresse_records = self.env['res.partner'].search([('parent_id', '=', search_partner_id), ('type', '=', adress_type)])[0]
                if adresse_records:
                    adresse += self.search_adress(adresse_records, search)

        return adresse

    def check_is_repere_partner(self, datas):
        for doc in datas:
            data_info = self.env['purchase.order'].browse(doc)
            if not data_info.user_id or data_info.user_id.ref != 'ARGOS':
                raise UserError(_("Attention vous devez choisir repères comme responsable des achats pour accéder à ce fichier"))

    def generate_attachement(self, pdf_report_name, report_name):
        pdf = self.env.ref(pdf_report_name)._render_qweb_pdf(self.id)
        b64_pdf = base64.b64encode(pdf[0])
        self.env['ir.attachment'].create({
            'name': report_name + '.pdf',
            'type': 'binary',
            'datas': b64_pdf,
            'store_fname': report_name,
            'res_model': self._name,
            'res_id': self.id,
            'mimetype': 'application/pdf'
        })

    @staticmethod
    def get_sub_price(amount):
        return ("%.2f" % amount).replace('.', ',')
