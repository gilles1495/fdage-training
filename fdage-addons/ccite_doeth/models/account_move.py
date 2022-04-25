# -*- coding: utf-8 -*-

from odoo import api, fields, models, modules, _
from odoo.exceptions import UserError, ValidationError


class AccountMove(models.Model):
    _inherit = 'account.move'

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

    def action_generate_doeth(self):
        reference_partner_id = None
        year = None
        invoices_names = []
        subtotal_without_shipping = 0.0
        for record in self:
            if not reference_partner_id:
                reference_partner_id = record.partner_id
            else:
                # Check if all invoices are linked to the same res.partner
                if reference_partner_id != record.partner_id:
                    raise UserError("Les factures doivent toutes être rattachées au même client.")
            if year is None:
                year = record.invoice_date.year
            else:
                if year != record.invoice_date.year:
                    raise UserError("Les factures doivent toutes être de la même année.")
            invoices_names.append(record.name)
            for line in record.invoice_line_ids:
                if 'frais de port' not in line.name.lower():
                    subtotal_without_shipping += line.price_subtotal
        report_doeth_id = self.env['report.doeth'].create({
            'partner_id': reference_partner_id.id,
            'invoices_names': ', '.join(invoices_names),
            'subtotal_without_shipping': subtotal_without_shipping,
            'year': year
        })
        return self.env.ref('ccite_doeth.doeth_generation_report').report_action(report_doeth_id)
