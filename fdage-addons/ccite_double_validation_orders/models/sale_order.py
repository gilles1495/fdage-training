# -*- coding: UTF-8 -*-
from odoo import api, fields, models, _

from odoo.exceptions import ValidationError


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    has_client_validate_order = fields.Boolean('Is Order Validated By Client ?', default=False)

    def write(self, vals):

        if 'has_client_validate_order' in vals:
            if self.env.user.has_group('sales_team.group_sale_manager'):
                current_date = fields.datetime.now().strftime('%d/%m/%Y %H:%M:%S')
                if vals['has_client_validate_order']:
                    message_confirm = _('Auto validation At ') + current_date
                else:
                    message_confirm = _('Client Validation Cancel At ') + current_date
                self.message_post(body=message_confirm)
            else:
                if self.has_client_validate_order != vals['has_client_validate_order']:
                    raise ValidationError(_('You Cannot Validate this data.'))
        return super(SaleOrder, self).write(vals)
