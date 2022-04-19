import csv
import logging
import os
import shutil
import time
from datetime import datetime

import pytz

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

    @api.model
    def _export_csv_files(self):
        # Etablishement information
        etablishement = self.search_in_table_reference("SELECT id,code FROM etablishements", 'etablishements')
        # Sale team information
        sale_teams = self.search_in_table_reference("SELECT id,code FROM crm_team", 'crm_team')

        # Export des commercials
        self._cr.execute("SELECT res_partner.ref,res_partner.etablishement_id,res_partner.rank_user_vallibre_one,res_partner.rank_user_vallibre_two,res_partner.active,res_partner.email,res_partner.phone,res_users.nom,res_users.prenom,res_users.sale_team_id FROM res_users "
                         "LEFT JOIN res_partner ON res_users.partner_id = res_partner.id "
                         "WHERE res_users.login != 'admin' and res_partner.is_company=False AND res_partner.ref IS NOT NULL")
        records = self._cr.dictfetchall()

        #Export des binders
        self._cr.execute("SELECT code,name from binders")
        binders = self._cr.dictfetchall()

        # Commerciaux
        filepath = os.path.join(os.path.dirname(os.path.dirname(__file__))+'/data/Export_Swing/', 'representant.csv')
        with open(filepath, 'w', newline='') as csvfile:
            fieldnames = ['gcl_commercial', 'gcl_libelle', 'gcl_prenom', 'gcl_etablissement', 'gcl_zonecom', 'vallibre_1', 'vallibre_2', 'Fermé', 'gcl_email', 'zcc_telephone']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter=';')
            writer.writeheader()
            for record in records:
                # Recherche dans la liste des établissement celle qui à pour id celle du record.
                etablishement_info = next((item for item in etablishement if item['id'] == record['etablishement_id']), False)
                sale_teams_info = next((item for item in sale_teams if item['id'] == record['sale_team_id']), False)
                rows_values = {'gcl_commercial': record['ref'],
                               'gcl_libelle': record['nom'],
                               'gcl_prenom': record['prenom'],
                               'vallibre_1': record['rank_user_vallibre_one'],
                               'vallibre_2': record['rank_user_vallibre_two'],
                               'Fermé': '0' if record['active'] else '1',
                               'gcl_email': record['email'],
                               'zcc_telephone': record['phone']
                               }
                if etablishement_info:
                    rows_values['gcl_etablissement'] = etablishement_info['code']
                else:
                    rows_values['gcl_etablissement'] = ''

                if sale_teams_info :
                    rows_values['gcl_zonecom'] = sale_teams_info['code']
                else:
                    rows_values['gcl_zonecom'] = ''
                writer.writerow(rows_values)

            for binder in binders:
                if binder['code'] and binder['code'].startswith('XTER'):
                    etablishement = '001'
                    zone_com = '001'
                    binder_val_rank_one = 3
                    binder_val_rank_two = 41
                    is_active = '0'
                elif binder['code'] and binder['code'].startswith('XVTS'):
                    etablishement = '002'
                    zone_com = '002'
                    binder_val_rank_one = 1
                    binder_val_rank_two = 11
                    is_active = '0'
                elif binder['code'] and binder['code'].startswith('XVTD'):
                    etablishement = '002'
                    zone_com = '004'
                    binder_val_rank_one = 1
                    binder_val_rank_two = 21
                    is_active = '0'
                else:
                    etablishement = ''
                    zone_com = ''
                    binder_val_rank_one = ''
                    binder_val_rank_two = ''
                    is_active = ''

                writer.writerow({'gcl_commercial': binder['code'],
                                 'gcl_libelle': binder['name'],
                                 'gcl_prenom': '',
                                 'gcl_etablissement': etablishement,
                                 'gcl_zonecom': zone_com,
                                 'vallibre_1': binder_val_rank_one,
                                 'vallibre_2': binder_val_rank_two,
                                 'Fermé': is_active,
                                 'gcl_email': '',
                                 'zcc_telephone': ''
                                 })

        # Prix articles
        product_pricelist = self.search_in_table_reference("SELECT id,code FROM product_pricelist", 'product_pricelist')

        filepath = os.path.join(os.path.dirname(os.path.dirname(__file__)) + '/data/Export_Swing/', 'tarif.csv')
        self._cr.execute(
            "SELECT product_template.default_code,product_pricelist_item.pricelist_id, product_pricelist_item.fixed_price,product_template.list_price FROM product_template "
            "LEFT JOIN product_pricelist_item ON product_template.id = product_pricelist_item.product_tmpl_id ")
        records = self._cr.dictfetchall()
        default_date_start = '01/01/2018 00:00'
        default_date_end = '31/12/2099 00:00'
        with open(filepath, 'w', newline='') as csvfile:
            fieldnames = ['yts_codearticle', 'yts_tariftiers', 'yts_datedebut', 'yts_datefin', 'yts_prixnet']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter=';')
            writer.writeheader()
            for record in records:
                product_pricelist_info = {'code': ''}
                if record['pricelist_id']:
                    product_pricelist_info = next((item for item in product_pricelist if item['id'] == record['pricelist_id']), False)
                    if not product_pricelist_info:
                        product_pricelist_info = {'code': ''}

                if record['fixed_price']:
                    writer.writerow({'yts_codearticle': record['default_code'],
                                     'yts_tariftiers': product_pricelist_info['code'],
                                     'yts_datedebut': default_date_start,
                                     'yts_datefin': default_date_end,
                                     'yts_prixnet': str(record['fixed_price'] or 0).replace('.', ','),
                                     })
        # # Catégorie de produits
        filepath = os.path.join(os.path.dirname(os.path.dirname(__file__)) + '/data/Export_Swing/', 'famart.csv')
        self._cr.execute("SELECT c1.name, c1.code FROM product_category c1 "
                         "LEFT JOIN product_category c2 ON c2.id = c1.parent_id "
                         "WHERE COALESCE(c1.code, '') NOT IN ('', '10', '12', '90', '91', '99', '100', 'MP') AND (COALESCE(c2.code, '') not in ('0', 'MP'))")
        records = self._cr.dictfetchall()
        with open(filepath, 'w', newline='') as csvfile:
            fieldnames = ['cc_code', 'cc_libelle']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter=';')
            writer.writeheader()
            for record in records:
                writer.writerow({'cc_code': record['code'],
                                 'cc_libelle': record['name'],
                                 })
        # #Produits
        filepath = os.path.join(os.path.dirname(os.path.dirname(__file__)) + '/data/Export_Swing/', 'article.csv')
        self._cr.execute("SELECT p.default_code, p.name, CASE WHEN COALESCE(c2.code, '') = '0' THEN '0' ELSE c1.code END as code, p.active FROM product_template p "
                         "LEFT JOIN product_category c1 ON p.categ_id = c1.id "
                         "LEFT JOIN product_category c2 ON c1.parent_id = c2.id "
                         "WHERE COALESCE(c1.code, '') NOT IN ('', '10', '12', '90', '91', '99', '100', 'MP') AND COALESCE(c2.code, '') NOT IN ('MP')")
        records = self._cr.dictfetchall()
        with open(filepath, 'w', newline='') as csvfile:
            fieldnames = ['ga_codearticle', 'ga_libelle', 'ga_familleniv1', 'Fermé']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter=';')
            writer.writeheader()
            for record in records:
                writer.writerow({'ga_codearticle': record['default_code'],
                                 'ga_libelle': record['name'],
                                 'ga_familleniv1': record['code'],
                                 'Fermé': '0' if record['active'] else '1'
                                 })
        # # Facture
        filepath = os.path.join(os.path.dirname(os.path.dirname(__file__)) + '/data/Export_Swing/', 'histoentete.csv')
        self._cr.execute("SELECT account_move.name,account_move.invoice_date,p1.ref as ref_tiers,p2.ref as ref_representant,account_move.amount_untaxed,account_move.amount_total FROM account_move "
                         "LEFT JOIN crm_team ON account_move.team_id = crm_team.id "
                         "LEFT JOIN res_partner p1 ON p1.id = account_move.commercial_partner_id "
                         "LEFT JOIN res_users u1 ON u1.id = account_move.invoice_user_id "
                         "LEFT JOIN res_partner p2 ON p2.id = u1.partner_id "
                         "WHERE crm_team.code in ('001','002', '004') AND account_move.move_type='out_invoice'")
        records = self._cr.dictfetchall()

        with open(filepath, 'w', newline='') as csvfile:
            fieldnames = ['gp_naturepieceg', 'gp_souche', 'gp_numero', 'gp_datepiece', 'gp_tiers', 'gp_representant', 'gp_totalht', 'gp_totalttc']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter=';')
            writer.writeheader()
            for record in records:
                date_order = ''
                if record['invoice_date']:
                    date_order = record['invoice_date'].strftime('%d/%m/%Y')

                writer.writerow({'gp_naturepieceg': 'FAC',
                                 'gp_souche': '',
                                 'gp_numero': record['name'],
                                 'gp_datepiece': date_order,
                                 'gp_tiers': record['ref_tiers'],
                                 'gp_representant': record['ref_representant'],
                                 'gp_totalht': str(round(record['amount_untaxed'] or 0, 2)).replace('.', ','),
                                 'gp_totalttc': str(round(record['amount_total'] or 0, 2)).replace('.', ','),
                                 })
        # Lignes de Facture
        filepath = os.path.join(os.path.dirname(os.path.dirname(__file__)) + '/data/Export_Swing/', 'histoligne.csv')
        self._cr.execute("SELECT account_move_line.move_name,account_move_line.date,p1.ref as ref_tiers,p2.ref as ref_representant, "
                         "account_move_line.product_id,product_template.default_code, account_move_line.price_unit, "
                         "account_move_line.price_subtotal,account_move_line.quantity,account_move_line.discount,account_move_line.price_total, "
                         "CASE WHEN account_tax.amount_type = 'percent' THEN COALESCE(account_move_line.price_unit,0) * (1 + COALESCE(account_tax.amount) / 100) ELSE COALESCE(account_move_line.price_unit,0) + COALESCE(account_tax.amount, 0) END AS price_unit_ttc FROM account_move_line "
                         "LEFT JOIN account_move ON account_move.id = account_move_line.move_id "
                         "LEFT JOIN crm_team ON account_move.team_id = crm_team.id "
                         "LEFT JOIN product_product ON product_product.id = account_move_line.product_id "
                         "LEFT JOIN product_template ON product_template.id = product_product.product_tmpl_id "
                         "LEFT JOIN account_move_line_account_tax_rel ON account_move_line_account_tax_rel.account_move_line_id = account_move_line.id "
                         "LEFT JOIN account_tax ON account_tax.id = account_move_line_account_tax_rel.account_tax_id "
                         "LEFT JOIN res_partner p1 ON p1.id = account_move.commercial_partner_id "
                         "LEFT JOIN res_users u1 ON u1.id = account_move.invoice_user_id "
                         "LEFT JOIN res_partner p2 ON p2.id = u1.partner_id "
                         "WHERE account_move_line.product_id > 0 and crm_team.code in ('001','002', '004') AND account_move.move_type='out_invoice' "
                         "ORDER BY account_move_line.move_id")
        records = self._cr.dictfetchall()

        with open(filepath, 'w', newline='') as csvfile:
            fieldnames = ['gl_naturepieceg', 'gl_souche', 'gl_numero', 'gl_numligne', 'gl_datepiece', 'gl_tiers', 'gl_representant', 'gl_codearticle', 'gl_puht', 'gl_puttc', 'gl_qtefact', 'gl_remiseligne', 'gl_montantht', 'gl_montantttc']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter=';')
            writer.writeheader()
            cpt = 0
            saved_record_name = ''
            for record in records:
                if saved_record_name == record['move_name']:
                    cpt += 1
                else:
                    saved_record_name = record['move_name']
                    cpt = 1

                date_order = ''
                if record['date']:
                    date_order = record['date'].strftime('%d/%m/%Y')

                writer.writerow({'gl_naturepieceg': 'FAC',
                                 'gl_souche': '',
                                 'gl_numero': record['move_name'],
                                 'gl_numligne': cpt,
                                 'gl_datepiece': date_order,
                                 'gl_tiers': record['ref_tiers'],
                                 'gl_representant': record['ref_representant'],
                                 'gl_codearticle': record['default_code'],
                                 'gl_puht': str(round(record['price_unit'] or 0, 2)).replace('.', ','),
                                 'gl_puttc': str(round(record['price_unit_ttc'] or 0, 2)).replace('.', ','),
                                 'gl_qtefact': str(record['quantity'] or 0).replace('.', ','),
                                 'gl_remiseligne': str(round(record['discount'] or 0, 2)).replace('.', ','),
                                 'gl_montantht': str(round(record['price_subtotal'] or 0, 2)).replace('.', ','),
                                 'gl_montantttc': str(round(record['price_total'] or 0, 2)).replace('.', ',')
                                 })
        # Clients
        filepath = os.path.join(os.path.dirname(os.path.dirname(__file__)) + '/data/Export_Swing/', 'client.csv')
        self._cr.execute("SELECT p1.id as res_partner_id,p1.name,p1.siret,p1.ref,p1.street,p1.street2,p1.zip,p1.city,p1.phone,p1.phone2,p1.fax,p1.email,p1.etat_risque,p1.active,p1.country_id,res_country.code as res_country_code,crm_team.code as team_code, COALESCE(b.code, p2.ref) as representant,p1.purchase_warn,p1.etat_risque FROM res_partner p1 "
                         "LEFT JOIN res_country ON res_country.id = p1.country_id "
                         "LEFT JOIN crm_team ON crm_team.id = p1.team_id "
                         "LEFT JOIN res_users u ON u.id = p1.user_id "
                         "LEFT JOIN res_partner p2 ON p2.id = u.partner_id "
                         "LEFT JOIN binders b ON b.id = p1.binder_id "
                         "WHERE p1.is_company = True AND p1.customer_rank > 0")

        records = self._cr.dictfetchall()
        with open(filepath, 'w', newline='') as csvfile:
            fieldnames = ['t_tiers', 't_libelle', 't_adresse1', 't_adresse2', 't_adresse3', 't_codepostal', 't_ville', 't_telephone', 't_telephone2', 't_telex', 't_fax', 't_email', 't_siret', 't_commentaire', 't_zonecom', 't_representant', 't_etatrisque', 'Fermé', 'pays']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter=';')
            writer.writeheader()
            for record in records:
                if record['purchase_warn'] == 'no-message':
                    record['purchase_warn'] = ''

                writer.writerow({
                    't_tiers': record['ref'],
                    't_libelle': record['name'],
                    't_adresse1': record['street'],
                    't_adresse2': record['street2'],
                    't_adresse3': '',
                    't_codepostal': record['zip'],
                    't_ville': record['city'],
                    't_telephone': record['phone'],
                    't_telephone2': record['phone2'],
                    't_telex': '',
                    't_fax': record['fax'],
                    't_email': record['email'],
                    't_siret': record['siret'],
                    't_commentaire': record['purchase_warn'],
                    't_zonecom': record['team_code'],
                    't_representant': record['representant'],
                    't_etatrisque': record['etat_risque'],
                    'Fermé': 0 if record['active'] else 1,
                    'pays': record['res_country_code'],
                })

        # Adresses de clients
        filepath = os.path.join(os.path.dirname(os.path.dirname(__file__)) + '/data/Export_Swing/', 'adresse.csv')
        with open(filepath, 'w', newline='') as csvfile:

            # Write header
            fieldnames = ['adr_num', 't_tiers', 't_libelle', 't_adresse1', 't_adresse2', 't_adresse3', 't_codepostal', 't_ville', 't_telephone', 'adr_livr', 'adr_fact', 'adr_livrdef', 'adr_factdef']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter=';')
            writer.writeheader()

            # Extract customers addresses only
            self._cr.execute("""SELECT c.id as customer_id, c.ref, p.name, p.street, p.street2, p.zip, p.city, p.phone, p.type
            FROM res_partner p
            LEFT JOIN res_partner c ON c.id = p.parent_id
            WHERE c.customer_rank > 0 AND p.type <> 'contact' 
            ORDER BY c.id, p.id""")
            addresses = self._cr.dictfetchall()
            previous_customer_id = -1
            address_counter = 1
            for address in addresses:
                # Reset counter for every customer
                if previous_customer_id != address['customer_id']:
                    address_counter = 1
                    previous_customer_id = address['customer_id']

                # Write data row
                writer.writerow({
                    'adr_num': address_counter,
                    't_tiers': address['ref'],
                    't_libelle': address['name'],
                    't_adresse1': address['street'],
                    't_adresse2': address['street2'],
                    't_codepostal': address['zip'],
                    't_ville': address['city'],
                    't_telephone': address['phone'],
                    'adr_livr': 1 if address['type'] == 'delivery' else 0,
                    'adr_fact': 1 if address['type'] == 'invoice' else 0,
                    'adr_livrdef': 0,
                    'adr_factdef': 0,
                })

                # Next counter
                address_counter += 1

    def action_confirm(self):
        result = super(SaleOrder, self).action_confirm()
        if self.partner_id and self.partner_id.ref_is_mandatory and not self.client_order_ref:
            raise ValidationError('Attention vous devez renseigner la Référence client pour pouvoir valider ce devis.')
        return result

    @api.model
    def _import_csv_files(self):
        start_time = time.time()
        date_str = datetime.now(tz=pytz.timezone('Europe/Paris'))


        date_error_start = '0' + str(date_str.day) if date_str.day < 9 else str(date_str.day)
        date_error_start += '/' + str(date_str.month) + '/' + str(date_str.year) + ' ' + str(date_str.hour) + ' : ' + str(date_str.minute)
        filename = '0' + str(date_str.day) if date_str.day <= 9 else str(date_str.day)
        filename += '_' + str(date_str.month) + '_' + str(date_str.year) + '.log'

        path = os.path.dirname(os.path.dirname(__file__)) + '/data/Commandes_Swing/'
        saved_path = os.path.dirname(os.path.dirname(__file__)) + '/data/Commandes_Swing/passed/'
        # Génération nom de fichier de log
        for file in os.listdir(path):
            # Import fichier de pièces
            if file.lower().startswith('epiecesv3'):
                name = file.replace('epiecesv3_', '')
                filename = name.replace('.csv', '') + '.log'

        filepath = os.path.join(os.path.dirname(os.path.dirname(__file__))+'/error_swing/', filename)
        fichier = open(filepath, "a")
        i = 0
        for file in os.listdir(path):
            # Import fichier de pièces
            if file.lower().startswith('epiecesv3'):
                fullpath = path + file
                full_saved_path = saved_path + file
                with open(fullpath, encoding='ISO-8859-1') as f:
                    csv_reader = csv.reader(f, delimiter=';')
                    line_count = 0
                    for row in csv_reader:
                        if line_count > 0:

                            error_in_line_file = False
                            res_partner = self.env['res.partner'].search([('ref', '=', row[8]), ('customer_rank', '>', 0)])
                            if len(res_partner) > 1:
                                # LOG DOUBLE RES PARTNER
                                _logger.warning('Date : %s  Fichier : %s double res partner trouvé avec comme ref %s ligne %s' % (date_error_start, file, row[8], line_count))
                                fichier.write('Date : %s  Fichier : %s double res partner trouvé avec comme ref %s ligne %s \n' % (date_error_start, file, row[8], line_count))
                                res_partner = res_partner[0]
                            if not res_partner:
                                error_in_line_file = True
                                _logger.error('Date : %s  Fichier : %s pas de correspondance pour le res partner suivant %s ligne %s' % (date_error_start, file, row[8], line_count))
                                fichier.write('Date : %s  Fichier : %s pas de correspondance pour le res partner suivant %s ligne %s \n' % (date_error_start, file, row[8], line_count))

                            payment_term_id = self.env['account.payment.term'].search([('code', '=', row[9])])
                            # On retrouve le vendeur
                            saylor_id = self.env['res.users'].search([('ref', '=', row[21])])
                            # ON va chercher le res user associé
                            if saylor_id:
                                if len(saylor_id) > 1:
                                    _logger.warning('Date : %s  Fichier : %s double vendeur trouvé avec comme ref : %s ligne %s' % (date_error_start, file, row[21], line_count))
                                    fichier.write('Date : %s  Fichier : %s double vendeur trouvé avec comme ref : %s ligne %s \n' % (date_error_start, file, row[21], line_count))

                                    saylor_id = saylor_id[0]

                            if not saylor_id:
                                _logger.error('Date : %s  Fichier : %s pas de correspondance pour le vendeur : %s ligne %s' % (date_error_start, file, row[21], line_count))
                                fichier.write('Date : %s  Fichier : %s pas de correspondance pour le vendeur : %s ligne %s \n' % (date_error_start, file, row[21], line_count))
                            # Recherche de devis déjà existant avec une valeur similaire
                            if row[3] and self.env['sale.order'].search([('ep_number_swing', '=', row[3])]):
                                error_in_line_file = True
                                _logger.error('Date : %s  Fichier : %s il éxiste déjà un devis avec comme référence : %s ligne %s' % (date_error_start, file, row[3], line_count))
                                fichier.write('Date : %s  Fichier : %s il éxiste déjà un devis avec comme référence : %s ligne %s \n' % (date_error_start, file, row[3], line_count))

                            if not error_in_line_file:
                                swing_ref = row[12]
                                commitment_date = datetime.strftime(datetime.strptime(row[11], "%d/%m/%Y"), '%Y-%m-%d') if row[11] else False

                                sale_record_values = {
                                    'date_order': datetime.strftime(datetime.strptime(row[5], "%d/%m/%Y"), '%Y-%m-%d'),
                                    'wallet_date': datetime.strftime(datetime.strptime(row[5], "%d/%m/%Y"), '%Y-%m-%d'),
                                    'partner_id': res_partner.id,
                                    'note_swing': row[17],
                                    'ref_swing_id': swing_ref,
                                    'ep_number_swing': row[3],
                                    'commitment_date': commitment_date,
                                    'urgent': str(row[18]).lstrip('0') == '1',
                                }
                                if saylor_id:
                                    sale_record_values['user_id'] = saylor_id.id
                                    if saylor_id.sale_team_id and saylor_id.sale_team_id.id:
                                        sale_record_values['team_id'] = saylor_id.sale_team_id.id
                                if payment_term_id:
                                    sale_record_values['payment_term_id'] = payment_term_id.id

                                new_test = self.env['sale.order'].with_context(mail_notrack=True, mail_create_nolog=True).create(sale_record_values)
                        line_count += 1

                shutil.move(fullpath, full_saved_path)
            i += 1

        for file in os.listdir(path):
            # Import fichier de lignes
            if file.lower().startswith('elignesv3'):
                fullpath = path + file
                full_saved_path = saved_path + file
                with open(fullpath, encoding='ISO-8859-1') as f:
                    csv_reader = csv.reader(f, delimiter=';')
                    line_count = 0
                    for row in csv_reader:
                        if line_count > 0:
                            error_in_line_file = False
                            ep_number_swing = row[2]
                            sale_order = self.env['sale.order'].search([('ep_number_swing', '=', ep_number_swing)])
                            if not sale_order:
                                error_in_line_file = True
                                fichier.write('Date : %s  Fichier : %s pas de correspondance pour le sale order avec comme numéro de référence : %s ligne %s \n' % (date_error_start, file, ep_number_swing, line_count))
                                _logger.error('Date : %s  Fichier : %s pas de correspondance pour le sale order avec comme numéro de référence : %s ligne %s' % (date_error_start, file, ep_number_swing, line_count))

                            product_id = self.env['product.product'].search([('default_code', '=', row[4]), ('active', '=', True)])
                            if not product_id:
                                error_in_line_file = True
                                error_message = 'Produit %s inconnu' % row[4]
                                self.generate_note('sale.order', sale_order.id, sale_order.name, error_message)

                                fichier.write('Date : %s  Fichier : %s pas de correspondance pour le produit avec comme numéro de référence : %s ligne %s \n' % (date_error_start, file, row[4], line_count))
                                _logger.error('Date : %s  Fichier : %s pas de correspondance pour le produit avec comme numéro de référence : %s ligne %s ' % (date_error_start, file, row[4], line_count))

                            if not error_in_line_file:
                                sale_order_line_values = {
                                    'order_id': sale_order.id,
                                    'product_uom_qty': row[6],
                                    'name': row[7],
                                    'product_id': product_id.id,
                                    'price_unit': row[9],
                                    'order_partner_id': sale_order.partner_id.id,
                                    'discount': row[10],
                                }
                                self.env['sale.order.line'].with_context(mail_notrack=True, mail_create_nolog=True).create(sale_order_line_values)

                            if sale_order and error_in_line_file:
                                sale_order.write({"swing_import_error": True})

                        line_count += 1

                shutil.move(fullpath, full_saved_path)

        for file in os.listdir(path):
            # Import fichier de lignes
            if file.lower().startswith('epiedportv3'):
                fullpath = path + file
                full_saved_path = saved_path + file
                with open(fullpath, encoding='ISO-8859-1') as f:
                    csv_reader = csv.reader(f, delimiter=';')
                    line_count = 0
                    for row in csv_reader:
                        if line_count > 0:
                            error_in_line_file = False
                            ep_number_swing = row[2]
                            sale_order = self.env['sale.order'].search([('ep_number_swing', '=', ep_number_swing)])
                            if not sale_order:
                                error_in_line_file = True
                                fichier.write('Date : %s  Fichier : %s pas de correspondance pour le sale order avec comme numéro de référence : %s ligne %s \n' % (date_error_start, file, ep_number_swing, line_count))
                                _logger.error('Date : %s  Fichier : %s pas de correspondance pour le sale order avec comme numéro de référence : %s ligne %s' % (date_error_start, file, ep_number_swing, line_count))

                            delivery_record = self.env['delivery.carrier'].search([('code', '=', row[4])])
                            if not delivery_record:
                                error_in_line_file = True
                                if sale_order:
                                    error_message = 'Frais de port %s inconnu' % row[4]
                                    self.generate_note('sale.order', sale_order.id, sale_order.name, error_message)
                                fichier.write('Date : %s  Fichier : %s pas de correspondance pour le frais de port avec comme numéro de référence : %s ligne %s\n' % (date_error_start, file, row[4], line_count))
                                _logger.error('Date : %s  Fichier : %s pas de correspondance pour le frais de port avec comme numéro de référence : %s ligne %s' % (date_error_start, file, row[4], line_count))
                            else:
                                delivery_values = delivery_record.rate_shipment(sale_order)
                                if delivery_values.get('success'):
                                    delivery_price = delivery_values['price']
                                else:
                                    error_in_line_file = True
                                    error_message = 'Impossible d\'appliquer les frais d\'expédition'
                                    if sale_order:
                                        self.generate_note('sale.order', sale_order.id, sale_order.name, error_message)
                                    error_msg = 'Date : %s  Fichier : %s %s pour le numéro de référence : %s' % (date_error_start, file, error_message, ep_number_swing)
                                    fichier.write(error_msg + ' \n')
                                    _logger.error(error_msg)

                            if not error_in_line_file:
                                sale_order.set_delivery_line(delivery_record, delivery_price)

                            if sale_order and error_in_line_file:
                                sale_order.write({"swing_import_error": True})

                        line_count += 1

                shutil.move(fullpath, full_saved_path)

        for file in os.listdir(path):
            # On déplace les fichiers restant
            if file.lower().startswith('epie') or file.lower().startswith('eli'):
                fullpath = path + file
                full_saved_path = saved_path + file
                _logger.info('Date : %s  Fichier : %s déplacé dans le dossier passed sans action \n' % (date_error_start, file))

                shutil.move(fullpath, full_saved_path)

        _logger.warning('Temps pour enregistrer les données SWING %s' % (time.time() - start_time))
        fichier.close()
