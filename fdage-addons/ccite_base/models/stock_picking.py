# -*- coding: UTF-8 -*-
from odoo import api, fields, models


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    def do_print_picking(self):
        self.write({'printed': True})
        # self.do_print_2()
        return self.env.ref('stock.action_report_picking').report_action(self)

    def do_print_2(self):
        return self.env.ref('stock.action_report_delivery').report_action(self)

