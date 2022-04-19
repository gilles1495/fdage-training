# -*- coding: utf-8 -*-

from odoo import api, fields, models, modules, _


class AccountAccount(models.Model):
    _inherit = 'account.account'

    @api.model
    def _recouncil_bad_import(self):
        # Recherche des comptes de type reconcile
        for account in self.env['account.account'].search([('reconcile', '=', True)]):
            partner_list = {}
            # Pour ce compte on regarde toute les lignes non reconcilier avec le même partenaire pour avoir l'id
            for move_line in self.env['account.move.line'].search([('account_id', '=', account.id), ('full_reconcile_id', '=', False), ('balance', '!=', 0), ('account_id.reconcile', '=', True)]):
                # On ajout l'id du partner et l'id de la ligne associé
                if move_line.partner_id.id not in partner_list:
                    partner_list[move_line.partner_id.id] = [{'ml_id': move_line.id, 'debit': move_line.debit, 'credit': move_line.credit}]
                else:
                    partner_list[move_line.partner_id.id].append({'ml_id': move_line.id, 'debit': move_line.debit, 'credit': move_line.credit})
            for partner_id in partner_list:
                if len(partner_list[partner_id]) > 1:
                    total_credit = 0
                    total_debit = 0
                    list_ids = []
                    for line in partner_list[partner_id]:
                        total_credit += line['credit']
                        total_debit += line['debit']
                        list_ids.append(line['ml_id'])

                    if round(total_debit, 2) == round(total_credit, 2):
                        self.env['account.reconciliation.widget']._process_move_lines(list_ids, [])
