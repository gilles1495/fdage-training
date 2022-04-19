# -*- coding: utf-8 -*-
from odoo import api, models, _
from ..models.utils import Utils


class ParticularReport(models.AbstractModel):
    _name = 'report.faal_tempo.faal_purchase_order_repere_report_template'
    _description = 'Modèle de rapport pour les purchases order'

    def _get_report_values(self, docids, data=None):
        Utils.check_is_repere_partner(self, docids)

        docs = self.env['purchase.order'].browse(docids)
        return {
            'doc_ids': docs.ids,
            'doc_model': 'purchase.order',
            'docs': docs,
        }
