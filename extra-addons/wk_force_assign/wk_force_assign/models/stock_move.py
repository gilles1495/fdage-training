# -*- coding: utf-8 -*-
#################################################################################
#
#   Copyright (c) 2016-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#    See LICENSE file for full copyright and licensing details.
#################################################################################

from odoo import models


class StockMove(models.Model):

    _inherit = "stock.move"

    def _wk_force_assign(self):
        """ Allow to work on stock move lines even if the reservation is not possible. We just mark
        the move as assigned, so the view does not block the user.
        """
        stock_move_lines = self.env['stock.move.line']
        reserved_availability = {move: move.reserved_availability for move in self}
        for move in self.filtered(lambda m: m.state == 'assigned'):
            move.write({
                'quantity_done': move.reserved_availability
            })
        for move in self.filtered(lambda m: m.state in ['confirmed', 'waiting', 'partially_available']):
            initial_demand = move.product_uom_qty
            missing_reserved_uom_quantity = initial_demand - reserved_availability[move]
            if move.product_id.tracking == 'serial':
                if missing_reserved_uom_quantity > 0:
                    for i in range(0, int(missing_reserved_uom_quantity)):
                        stock_move_line_id = stock_move_lines.create(move._prepare_move_line_vals(quantity=0))
                        stock_move_line_id.write({
                            'qty_done': 1,
                        })
                    reserve_serial_line_product = stock_move_lines.search([('move_id', '=', move.id)])
                    for line in reserve_serial_line_product:
                        if line.product_uom_qty:
                            line.write({
                                'qty_done': line.product_uom_qty,
                            })
                elif reserved_availability[move] <= 0:
                    for i in range(0, int(initial_demand)):
                        stock_move_line_id = stock_move_lines.create(move._prepare_move_line_vals(quantity=0))
                        stock_move_line_id.write({
                            'qty_done': 1,
                        })
            else:
                if missing_reserved_uom_quantity > 0:
                    move.write({
                        'quantity_done': initial_demand,
                    })
                elif reserved_availability[move] <= 0:
                    stock_move_line_id = stock_move_lines.create(move._prepare_move_line_vals(quantity=0))
                    stock_move_line_id.write({
                            'qty_done': initial_demand,
                        })
            move.write({
                'state': 'assigned'
            })
        return True


        