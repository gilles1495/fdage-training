# -*- coding: UTF-8 -*-
from odoo import api, fields, models, _

from odoo.exceptions import ValidationError


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    has_client_validate_order = fields.Boolean('Customer Validation', default=False)

    def write(self, vals):

        if 'has_client_validate_order' in vals:
            if self.env.user.has_group('sales_team.group_sale_manager'):
                current_date = fields.datetime.now().strftime('%d/%m/%Y %H:%M:%S')
                if vals['has_client_validate_order']:
                    self.signed_by = self.env.user.name
                    self.signed_on = fields.Datetime.now()
                    message_confirm = _('Validated on ') + current_date
                else:
                    self.signed_by = False
                    self.signed_on = False
                    self.signature = False
                    message_confirm = _('Validation Canceled On ') + current_date
                self.message_post(body=message_confirm)
            else:
                if self.has_client_validate_order != vals['has_client_validate_order']:
                    raise ValidationError(_('You do not have the right to validate this quote.'))
        return super(SaleOrder, self).write(vals)

    def action_cancel(self):
        self.has_client_validate_order = False
        self.write({'state': 'cancel'})

    def has_to_be_signed(self, include_draft=False):
        return (self.state == 'sent' or (self.state == 'draft' and include_draft)) and not self.is_expired and self.require_signature and not self.signed_by
