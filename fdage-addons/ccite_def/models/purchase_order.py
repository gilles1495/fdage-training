from odoo import api, fields, models, modules
from .utils import Utils


class PurcharseOrderInherit(models.Model):
    _inherit = 'purchase.order'

    swing_number = fields.Char(string=u'Numéro CEGID', index=True, copy=False)
    swing_ref = fields.Char(string=u'Référence CEGID', copy=False)

    def get_ref_fourni_code(self, record):
        ref_product_code = ''
        if self.partner_id and record.product_id:
            for info in self.env['product.supplierinfo'].search([('name', '=', self.partner_id.id), ('product_tmpl_id', '=', record.product_id.id)]):
                ref_product_code = info.product_code
        if not ref_product_code and record.product_id:
            ref_product_code = record.product_id.code
        return ref_product_code

    def get_parent_info(self, user_id, search_type, search_value):
        text_value = ''

        if user_id.parent_id:
            info_records = self.env['res.partner'].search([('type', '=', search_type), ('parent_id', '=', user_id.parent_id.id)])
            if len(info_records) > 1:
                info_records = self.env['res.partner'].search([('type', '=', search_type), ('parent_id', '=', user_id.parent_id.id)])[0]

            if info_records:
                if search_value == 'name':
                    text_value = info_records.name
                if search_value == 'phone':
                    text_value = info_records.phone
                if search_value == 'mobile':
                    text_value = info_records.mobile
                if search_value == 'email':
                    text_value = info_records.email
                if search_value == 'street':
                    text_value = info_records.street
                if search_value == 'street2':
                    text_value = info_records.street2
                if search_value == 'zip':
                    text_value = info_records.zip
                if search_value == 'city':
                    text_value = info_records.city

        return text_value

    def get_contact_information(self):
        text_value = ''
        contact_record = self.env['res.partner'].search([('name', 'like', '%repères%')])
        if len(contact_record) > 1:
            contact_record = self.env['res.partner'].search([('name', 'like', '%repères%')])[0]

        get_contact_record = self.env['res.partner'].search([('parent_id', '=', contact_record.id), ('type', '=', 'contact')])
        if len(get_contact_record) > 1:
            get_contact_record = self.env['res.partner'].search([('parent_id', '=', contact_record.id), ('type', '=', 'contact')])[0]

        if get_contact_record.name:
            text_value += get_contact_record.name
        if get_contact_record.phone:
            text_value += ' - ' + get_contact_record.phone
        if get_contact_record.email:
            text_value += ' - ' + get_contact_record.email

        return text_value

    def get_sub_price(self, amount):
        return Utils.get_sub_price(amount)

    def get_repere_information(self, search_value):
        repere_info = ''
        repere_record = self.env['res.users'].search([('name', 'like', '%repères%'), ('login', '=', 'contact@reperes-signaletique.com')])
        if repere_record:
            if search_value == 'name':
                return  repere_record.name
            if search_value == 'street':
                return repere_record.street
            if repere_record.street2 and search_value == 'street2':
                return repere_record.street2
            if search_value == 'postal':
                return (repere_record.zip or '') + ' ' + (repere_record.city or '')
            if repere_record.country_id and search_value == 'country':
                return repere_record.country_id.name
        return repere_info
