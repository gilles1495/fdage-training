import logging

from odoo import api, fields, models
from odoo.exceptions import ValidationError
from .utils import Utils

_logger = logging.getLogger(__name__)


WALLET_PERIOD_START_DAY = 21


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.model
    def read_group(self, domain, fields, groupby, offset=0, limit=None, orderby=False, lazy=True):
        res = super(SaleOrder, self).read_group(domain, fields, groupby, offset=offset, limit=limit, orderby=orderby, lazy=lazy)
        if 'total_ht_without_port' in fields and 'total_port_value' in fields:
            for line in res:
                if '__domain' in line:
                    lines = self.search(line['__domain'])
                    total_port_value = 0.0
                    total_ht_without_port_value = 0.0
                    for record in lines:
                        total_ht_without_port_value += record.total_ht_without_port
                        total_port_value += record.total_port_value

                    line['total_port_value'] = total_port_value
                    line['total_ht_without_port'] = total_ht_without_port_value
        return res

    partner_id = fields.Many2one(
        'res.partner',
        string="Customer",
        readonly=True,
        states={
            'draft': [('readonly', False)],
            'sent': [('readonly', False)],
        },
        required=True,
        change_default=True,
        index=True,
        tracking=1,
        domain="['|', ('type', '=', 'contact'), ('type', '=', None)]",
    )
    partner_invoice_id = fields.Many2one(
        'res.partner',
        string="Invoice Address",
        readonly=True,
        required=True,
        states={
            'draft': [('readonly', False)],
            'sent': [('readonly', False)],
            'sale': [('readonly', False)],
        },
        domain="['&', ('parent_id', '=', partner_id), ('type', '=', 'invoice')]",
    )
    partner_shipping_id = fields.Many2one(
        'res.partner',
        string="Delivery Address",
        readonly=True,
        required=True,
        states={
            'draft': [('readonly', False)],
            'sent': [('readonly', False)],
            'sale': [('readonly', False)],
        },
        domain="['&', ('parent_id', '=', partner_id), ('type', '=', 'delivery')]",
    )

    ref_swing_id = fields.Char(string=u'Référence de la plateforme swing')
    ep_number_swing = fields.Char(string=u'Référence de la plateforme swing pour le champ EP_NUMERO', index=True)
    swing_import_error = fields.Boolean(default=False, string=u'Erreur pendant l\'import swing')
    total_port_value = fields.Monetary(string=u'Frais de port', compute='_get_port_value')
    total_ht_without_port = fields.Monetary(string=u'Total hors frais de port', compute='_get_port_value')
    wallet_date = fields.Datetime(string=u'Date du portefeuille')
    wallet_period = fields.Char(string=u'Portefeuille', compute='_get_wallet_period', store=True)
    partner_id_city = fields.Char(string=u'Ville', compute='_get_partner_id_city')
    partner_id_zip = fields.Char(string=u'Code postal', compute='_get_partner_id_city')
    partner_id_code = fields.Char(string=u'Code', compute='_get_partner_id_city')
    note_swing = fields.Char(string=u'Commentaire')
    sale_order_name_ref = fields.Char(string=u'Nom du vendeur', compute='_get_vendor_name')
    new_order = fields.Boolean(string=u'Nouvelle commande', default=False)
    repere_delay = fields.Char(string=u'Délais estimatif', default="3 à 4 semaines à réception de la commande.")
    repere_more_information = fields.Char(string=u'Complément d\'informations', default="livraison sur chantier. Adresse à confirmer par vos soins.")
    repere_note = fields.Text(string=u'Conditions de commande', default="acompte de 30% de la somme totale TTC exigé dès 5000 € HT ; acompte de 50% de la somme totale TTC exigé dès 20 000 € HT ;règlement comptant en cas de 1ère commande.")
    urgent = fields.Boolean(string="Urgent", default=False)
    all_lines_amount_within_10_pc_of_list_price = fields.Boolean(
        string="Montant de toutes les lignes à ±10% du prix liste",
        help="Si le montant de toutes les lignes est compris entre +10% et -10% du prix liste",
        compute='_get_all_lines_amount_within_10_pc_of_list_price',
    )
    ref = fields.Char(string='Référence Facture Proforma', copy=False)
    contact_id = fields.Many2one('res.partner', string="Contact", domain="['&', ('parent_id', '=', partner_id), ('type', '=', 'contact')]",)

    @api.depends('wallet_date')
    def _get_wallet_period(self):
        for record in self:
            if record.wallet_date:
                dt = fields.Datetime.from_string(record.wallet_date)
                dt = fields.Datetime.context_timestamp(record, timestamp=dt)
                year = dt.year
                month = dt.month
                if dt.day >= WALLET_PERIOD_START_DAY:
                    month += 1
                if month > 12:
                    month = 1
                    year += 1
                record.wallet_period = 'P%02d-%04d' % (month, year)
            else:
                record.wallet_period = None

    def get_sub_price(self, amount):
        return Utils.get_sub_price(amount)

    @api.depends('order_line')
    def _get_port_value(self):
        for item in self:
            item.total_port_value = ''
            item.total_ht_without_port = item.amount_untaxed
            if item.order_line:
                total_port_value = 0.0
                total_reduce = 0.0
                for sale_line in item.order_line:
                    if 'Frais de port' in sale_line.display_name:
                        total_port_value += sale_line.price_reduce
                        total_reduce += sale_line.price_reduce

                item.total_ht_without_port = item.amount_untaxed - total_reduce
                item.total_port_value = total_port_value

    @api.depends('partner_id')
    def _get_partner_id_city(self):
        for item in self:
            if item.partner_id:
                item.partner_id_city = item.partner_id.city
                item.partner_id_zip = item.partner_id.zip
                item.partner_id_code = item.partner_id.ref

    @api.depends('user_id')
    def _get_vendor_name(self):
        for item in self:
            if item.user_id:
                item.sale_order_name_ref = item.user_id.partner_id.ref

    @api.depends('order_line')
    def _get_all_lines_amount_within_10_pc_of_list_price(self):
        for item in self:
            item.all_lines_amount_within_10_pc_of_list_price = all([
                el.amount_within_10_pc_of_list_price
                for el in item.order_line
            ])

    def generate_note(self, model_name, res_id, record_name, body):
        subtype_id = self.env['mail.message.subtype'].search([('name', '=', 'Note'), ('internal', '=', True)])
        self.env['mail.message'].create({
            'res_id': res_id,
            'model': model_name,
            'record_name': record_name,
            'message_type': 'comment',
            'subtype_id': subtype_id.id,
            'body': body
        })

    def search_adress(self, item, search):
        return Utils.search_adress(self, item, search)

    def get_adress(self, adress_type, search=False, is_delivery=False):
        return Utils.get_adress(self, adress_type, search, is_delivery)

    def search_in_table_reference(self, request, search_table=''):
        records_information = []
        self._cr.execute(request)
        records = self._cr.dictfetchall()
        for record in records:
            information = {'id': record['id']}
            if search_table and search_table in ['etablishements', 'crm_team', 'product_pricelist']:
                information['code'] = record['code']
            if search_table and search_table == 'res_partner':
                information['ref'] = record['ref']
            if search_table and search_table == 'res_users':
                information['partner_id'] = record['partner_id']

            records_information.append(information)
        return records_information

    def action_confirm(self):
        result = super(SaleOrder, self).action_confirm()
        if self.partner_id and self.partner_id.ref_is_mandatory and not self.client_order_ref:
            raise ValidationError('Attention vous devez renseigner la Référence client pour pouvoir valider ce devis.')
        return result

