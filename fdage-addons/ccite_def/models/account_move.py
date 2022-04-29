# -*- coding: utf-8 -*-

from odoo import api, fields, models, modules, _
from odoo.exceptions import UserError, ValidationError


class AccountMove(models.Model):
    _inherit = 'account.move'

    amount_option = fields.Float(string=u'Montant souhaité ligne de facture')
    text_option = fields.Char(string=u'Description ligne de facture')

    partner_id = fields.Many2one(
        'res.partner',
        readonly=True,
        tracking=True,
        states={
            'draft': [('readonly', False)]
        },
        domain="['|', ('type', '=', 'contact'), ('type', '=', None)]",
        string="Partner",
        change_default=True,
    )
    partner_shipping_id = fields.Many2one(
        'res.partner',
        string="Delivery Address",
        readonly=True,
        states={
            'draft': [('readonly', False)]
        },
        domain="['&', ('parent_id', '=', partner_id), ('type', '!=', 'contact')]",
        help="Delivery address for current invoice.",
    )

    amount_option = fields.Float(
        string="Montant souhaité ligne de facture",
        readonly=True,
        states={'draft': [('readonly', False)]},
    )
    text_option = fields.Char(
        string="Description ligne de facture",
        readonly=True,
        states={'draft': [('readonly', False)]},
    )

    def get_invoice_info(self):
        return_value = ''
        so_record = self.env['sale.order'].search([('name', '=', self.invoice_origin)])
        if so_record:
            if so_record.display_name:
                return_value += so_record.display_name
            if so_record.date_order.strftime('%d/%m/%Y'):
                return_value += ' du ' + so_record.date_order.strftime('%d/%m/%Y')
            if so_record.ref_swing_id:
                return_value += ' ' + so_record.ref_swing_id
        return return_value

    def get_livraison_info(self):
        return_value = ''
        so_record = self.env['sale.order'].search([('name', '=', self.invoice_origin)])
        outgoing_id = self.env['stock.picking.type'].search([('code', '=', 'outgoing')])
        if so_record and so_record.delivery_count > 0 and outgoing_id:
            delivery_record = self.env['stock.picking'].search([('state', '=', 'done'), ('sale_id', '=', so_record.id), ('picking_type_id', '=', outgoing_id.id)])
            if delivery_record:
                if delivery_record[0].display_name:
                    return_value += delivery_record[0].display_name
                if delivery_record[0].date_done.strftime('%d/%m/%Y'):
                    return_value += ' du ' + delivery_record[0].date_done.strftime('%d/%m/%Y')
                if so_record.ref_swing_id:
                    return_value += ' ' + so_record.ref_swing_id
        return return_value

    # def action_generate_doeth(self):
    #     reference_partner_id = None
    #     year = None
    #     invoices_names = []
    #     subtotal_without_shipping = 0.0
    #     for record in self:
    #         if not reference_partner_id:
    #             reference_partner_id = record.partner_id
    #         else:
    #             # Check if all invoices are linked to the same res.partner
    #             if reference_partner_id != record.partner_id:
    #                 raise UserError("Les factures doivent toutes être rattachées au même client.")
    #         if year is None:
    #             year = record.invoice_date.year
    #         else:
    #             if year != record.invoice_date.year:
    #                 raise UserError("Les factures doivent toutes être de la même année.")
    #         invoices_names.append(record.name)
    #         for line in record.invoice_line_ids:
    #             if 'frais de port' not in line.name.lower():
    #                 subtotal_without_shipping += line.price_subtotal
    #     report_doeth_id = self.env['report.doeth'].create({
    #         'partner_id': reference_partner_id.id,
    #         'invoices_names': ', '.join(invoices_names),
    #         'subtotal_without_shipping': subtotal_without_shipping,
    #         'year': year
    #     })
    #     return self.env.ref('ccite_def.doeth_generation_report').report_action(report_doeth_id)
