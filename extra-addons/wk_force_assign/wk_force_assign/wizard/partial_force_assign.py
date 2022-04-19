# -*- coding: utf-8 -*-
#################################################################################
#
#   Copyright (c) 2016-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#    See LICENSE file for full copyright and licensing details.
#################################################################################

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class PartialForceAssignLine(models.TransientModel):
    _name = "partial.force.assign.line"
    _rec_name = 'product_id'
    _description = 'Partial Force Assign Line'

    product_id = fields.Many2one(
        'product.product', string="Product", required=True,
        domain="[('id', '=', product_id)]", readonly=True,
    )
    product_uom_qty = fields.Float(
        'Demand',
        digits='Product Unit of Measure',
        default=0.0, required=True,
        readonly=True,
    )
    reserved_availability = fields.Float(
        'Reserved', digits='Product Unit of Measure',
        readonly=True, help='Quantity that has already been reserved for this move')
    quantity_done = fields.Float("Done", digits='Product Unit of Measure')
    wizard_id = fields.Many2one('partial.force.assign', string="Wizard")
    move_id = fields.Many2one('stock.move', "Move")


class PartialForceAssign(models.TransientModel):
    _name = 'partial.force.assign'
    _description = 'Partial Force Assign'

    @api.model
    def default_get(self, fields):
        if len(self.env.context.get('active_ids', list())) > 1:
            raise UserError(_("You may perform only one partial force assign picking at a time."))
        res = super(PartialForceAssign, self).default_get(fields)
        if self.env.context.get('active_id') and self.env.context.get('active_model') == 'stock.picking':
            picking = self.env['stock.picking'].browse(self.env.context.get('active_id'))
            if picking.exists():
                res.update({'picking_id': picking.id})
        return res

    picking_id = fields.Many2one('stock.picking')
    force_assign_moves = fields.One2many('partial.force.assign.line', 'wizard_id', 'Moves')

    @api.onchange('picking_id')
    def _onchange_picking_id(self):
        force_assign_moves = [(5,)]
        if self.picking_id and self.picking_id.state == 'draft':
            self.picking_id.action_confirm()

        # default values for creation.
        line_fields = [f for f in self.env['partial.force.assign.line']._fields.keys()]
        force_assign_moves_data_tmpl = self.env['partial.force.assign.line'].default_get(line_fields)
        moves = self.picking_id.move_lines.filtered(lambda move: move.state not in ('draft', 'cancel', 'done'))
        if not moves:
            raise UserError(_('Nothing to check the force availability for.'))
        package_level_done = self.picking_id.package_level_ids.filtered(lambda pl: pl.is_done and pl.state == 'confirmed')
        package_level_done.write({'is_done': False})
        moves._action_assign()
        package_level_done.write({'is_done': True})

        for move in self.picking_id.move_lines:
            if move.scrapped:
                continue
            force_assign_moves_data = dict(force_assign_moves_data_tmpl)
            force_assign_moves_data.update(self._prepare_partial_force_assign_line_vals_from_move(move))
            force_assign_moves.append((0, 0, force_assign_moves_data))
        if self.picking_id and not force_assign_moves:
            raise UserError(_("No products to partial force assign."))
        if self.picking_id:
            self.force_assign_moves = force_assign_moves

    @api.model
    def _prepare_partial_force_assign_line_vals_from_move(self, stock_move):
        return {
            'product_id': stock_move.product_id.id,
            'product_uom_qty': stock_move.product_uom_qty,
            'reserved_availability': stock_move.reserved_availability,
            'quantity_done': stock_move.quantity_done,
            'move_id': stock_move.id,
        }

    def wk_partial_force_assign(self):
        moves = self.picking_id.move_lines
        reserved_availability = {move: move.reserved_availability for move in moves}
        # for move in moves.filtered(lambda m: m.state == 'assigned'):
        #     move.write({
        #         'quantity_done': move.reserved_availability
        #     })
        stock_move_lines = self.env['stock.move.line']
        for rec in self.force_assign_moves:
            move = rec.move_id
            if reserved_availability[move] <= 0 and rec.quantity_done > 0:
                if move.product_id.tracking == 'serial':
                    for i in range(0, int(rec.quantity_done)):
                        stock_move_line_id = stock_move_lines.create(move._prepare_move_line_vals(quantity=0))
                        stock_move_line_id.write({
                            'qty_done': 1,
                        })
                else:
                    stock_move_line_id = stock_move_lines.create(move._prepare_move_line_vals(quantity=0))
                    stock_move_line_id.write({
                        'qty_done': rec.quantity_done,
                    })
                move.write({
                    'state': 'assigned'
                })
            elif reserved_availability[move] > 0 and rec.quantity_done > 0:
                initial_demand = rec.quantity_done
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
                    elif reserved_availability[move] > initial_demand:
                        reserve_serial_line_product = stock_move_lines.search([('move_id', '=', move.id)], order="id desc", limit=int(initial_demand))
                        for line in reserve_serial_line_product:
                            if line.product_uom_qty:
                                line.write({
                                    'qty_done': line.product_uom_qty,
                                })
                else:
                    move.write({
                        'quantity_done': initial_demand,
                    })
                move.write({
                    'state': 'assigned'
                })
        return True
