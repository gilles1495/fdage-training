import datetime

from odoo import models
from odoo.exceptions import UserError


class StockMove(models.Model):
    _name = "stock.move"
    _inherit = 'stock.move'

    def get_reservation_days(self):
        try:
            parameter = self.env['ir.config_parameter'].sudo().search_read([('key', '=', 'stock.reservation.days')], ['value'])
            return int(parameter[0]['value']) if parameter else 0
        except ValueError:
            raise UserError("Le paramètre système 'stock.reservation.days' doit être un entier.")

    def _action_assign(self):
        days = self.get_reservation_days()
        if days > 0:
            recordset = self.filtered(lambda m: m.date < (datetime.datetime.now() + datetime.timedelta(days=days)))
            super(StockMove, recordset)._action_assign()
        else:
            super(StockMove, self)._action_assign()
