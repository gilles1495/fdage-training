# -*- coding: utf-8 -*-
from odoo import http, exceptions, _


class ResPartnerController(http.Controller):
    @http.route('/get_res_partner_information/', type='json', auth='user', csrf=False)
    def get_res_partner_information(self, res_partner_id, **kwargs):
        result = {}
        record = http.request.env['res.partner'].browse(res_partner_id)
        if record:
            result['ref'] = record.ref if record.ref else ''
            result['name'] = record.name if record.name else ''
            result['title'] = record.title.name if record.title and record.title.name else ''
            result['phone'] = record.phone if record.phone else ''
            result['email'] = record.email if record.email else ''
            result['street'] = record.street if record.street else ''
            result['street2'] = record.street2 if record.street2 else ''
            result['city'] = record.city if record.city else ''
            result['zip'] = record.zip if record.zip else ''
        return result
