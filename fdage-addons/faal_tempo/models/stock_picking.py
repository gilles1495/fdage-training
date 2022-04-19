import base64

from odoo import fields, models ,api
from odoo.exceptions import UserError
from odoo.tools import float_is_zero
from .utils import Utils


class StockPickingInherit(models.Model):
    _inherit = 'stock.picking'

    nb_colis = fields.Selection([('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'), ('5', '5')], string=u'Nombre de colis')
    delivery_partner_id = fields.Many2one('res.partner', string=u'Transporteur', domain=[('is_delivery_carrier', '=', True)])
    colis_1_kg = fields.Float(string=u'Poids colis 1 (kg)')
    colis_2_kg = fields.Float(string=u'Poids colis 2 (kg)')
    colis_3_kg = fields.Float(string=u'Poids colis 3 (kg)')
    colis_4_kg = fields.Float(string=u'Poids colis 4 (kg)')
    colis_5_kg = fields.Float(string=u'Poids colis 5 (kg)')
    code_picking_type_value = fields.Char(string=u'Code', related='picking_type_id.sequence_code')


    order = fields.Many2one('sale.order', string='order', compute='_compute_order', store=True)
    order_contact = fields.Many2one('res.partner', string=u'Contact', related='order.contact_id')


    @api.depends('origin')
    def _compute_order(self):
        for record in self:
            order = self.env['sale.order'].search([('name', '=', record.origin)], limit=1)
            if order:
                record.order = order[0]
            else:
                record.order = False

    def search_adress(self, item, search):
        return Utils.search_adress(self, item, search)

    def get_adress(self, adress_type, search=False, is_delivery=False):
        return Utils.get_adress(self, adress_type, search, is_delivery)

    def get_partner_part(self, partname):
        self.ensure_one()
        if not self.partner_id:
            return ''
        if partname == 'name':
            value = (self.partner_id.name or '')
        elif partname == 'street':
            value = ((self.partner_id.street or '') + ' ' + (self.partner_id.street2 or '')).strip()
        elif partname == 'zip':
            value = ((self.partner_id.zip or '') + ' ' + (self.partner_id.city or '')).strip()
        else:
            value = ''
        return value

    def get_ref_expedition(self):
        value = ''
        if self.sale_id:
            value = self.sale_id.ref_swing_id
        return value

    def search_line_from_so(self):
        return True if self.sale_id else False

    def get_delivery_report_lines(self):
        return self.get_picking_report_lines(done=True)

    def get_picking_report_lines(self, done=False):
        """ Retourne les lignes du BL avec ref, name et qty

            Pour les articles composants un kits c'est le kit qui retourné avec la quantité de kit complet
            que l'on peut faire.
        """

        def get_qty(obj):
            if done:
                return obj.quantity_done or 0.0
            elif obj.state == 'done':
                return obj.product_qty or 0.0
            else:
                return obj.reserved_availability or 0.0

        items = []
        if self.sale_id:
            # Parcourir les lignes de la commande
            for order_line in self.sale_id.order_line:

                if not order_line.product_id:
                    # Il s'agit d'une note par exemple, l'ignorer
                    continue

                quantity = 0.0
                # Est-ce que le produit est un kit ?
                #  bom = self.env['mrp.bom']._bom_find(order_line.product_id, bom_type='phantom')  # noqa
                bom = self.env["mrp.bom"]._bom_find(order_line.product_id)[order_line.product_id]
                if bom and bom.type == 'phantom':
                    # Oui, calculer la quantité de kit complet à partir des quantités du BL des composantes
                    ratios_qty = []
                    boms, bom_sub_lines = bom.explode(order_line.product_id, 1)
                    for bom_line, bom_line_data in bom_sub_lines:
                        # Ignorer les composantes sans quantité
                        if bom_line.product_id.type != 'product' or float_is_zero(bom_line_data['qty'], precision_rounding=bom_line.product_uom_id.rounding):
                            continue
                        qty_per_kit = bom_line_data['qty'] / bom_line_data['original_qty']
                        # Récupérer la quantité du BL pour cet article
                        qty = 0.0
                        for item in self.move_ids_without_package.filtered(lambda line: line.sale_line_id.id == order_line.id and line.product_id == bom_line.product_id):
                            qty += get_qty(item)
                        ratios_qty.append(qty / qty_per_kit)  # Calculer le ratio de chaque composant

                    # Le plus petit ratio correspond au nombre de kits complets qu'il est possible de faire avec les quantités du BL
                    if ratios_qty:
                        quantity = min(ratios_qty) // 1
                else:
                    # L'article n'est pas un kit, prendre la quantité de BL
                    for item in self.move_ids_without_package.filtered(lambda line: line.sale_line_id.id == order_line.id):
                        quantity += get_qty(item)

                # Les lignes avec une quantité à 0 ne seront pas imprimer sur le BL
                if quantity > 0.0:
                    items.append({'ref': order_line.product_id.default_code, 'name': order_line.name, 'qty': quantity})
        else:
            # Pas de commande associée, prendre les lignes du BL
            for picking_line in self.move_ids_without_package:
                quantity = get_qty(picking_line)
                if quantity > 0.0:
                    items.append({
                        'ref': picking_line.product_id.default_code,
                        'name': picking_line.product_id.name,
                        'qty': quantity
                    })

        return items

    def get_information_value(self, record, search):
        return_value = ''

        if search == 'description':
            return_value = record.name
            if record.product_id and record.product_id.default_code and '[' + record.product_id.default_code + ']' in record.product_id.display_name:
                return_value = record.name.replace('[' + record.product_id.default_code + ']', '')
        if search == 'ref' and record.product_id:
            return_value = record.product_id.code
        if search == 'qte':
            return_value = int(record.product_qty)

        return return_value

    # def get_description_so(self, record, search):
    #     return self.get_information_value(record, search)

    def get_description_picking(self, record, search):
        return_value = ''
        for line in self.sale_id.order_line:
            if record.product_id in line.product_id:
                return_value = self.get_information_value(line, search)
        if not return_value:
            for line in self.sale_id.order_line:
                # Si dans la commande un article est un article avec une nomenclature on test si on ne peut pas récupérer la valeur dans le sale order
                if line.product_id.bom_ids and line.product_id.bom_ids.bom_line_ids:
                    for bom_line in line.product_id.bom_ids.bom_line_ids:
                        if bom_line.product_id.code == record.product_id.default_code:
                            return_value = self.get_information_value(line, search)
        if not return_value:
            # Si il n'y à pas de vente associté au bon de livraison on retourne des informations.
            if search == 'description':
                return_value = record.description_picking
            if search == 'ref' and record.product_id:
                return_value = record.product_id.code
            if search == 'qte':
                return_value = int(record.product_uom_qty)

        return return_value

    def get_invoice_info(self):
        return_value = ''
        so_record = self.env['sale.order'].search([('name', '=', self.origin)])
        if so_record:
            if so_record.display_name:
                return_value += so_record.display_name
            if so_record.date_order:
                return_value += ' du ' + so_record.date_order.strftime('%d/%m/%Y')
            if so_record.ref_swing_id:
                return_value += ' ' + so_record.ref_swing_id

        return return_value

    def _get_report_filename_pdp(self):
        self.ensure_one()
        return 'BL_%s' % self.name

    @staticmethod
    def set_final_space_or_start(value, add_to_start=True, number_char=0, char=' '):
        str_value = str(value or '')
        if number_char == 0:
            return str_value
        if add_to_start:
            return str_value.rjust(number_char, char)[:number_char]
        else:
            return str_value.ljust(number_char, char)[:number_char]

    def _get_content_pdp(self):
        value = '$VERSION=110\r\n'
        for record in self:
            i = 0
            while i < int(record.nb_colis or '0'):
                i += 1
                if i == 2:
                    pods = record.colis_2_kg
                elif i == 3:
                    pods = record.colis_3_kg
                elif i == 4:
                    pods = record.colis_4_kg
                elif i == 5:
                    pods = record.colis_5_kg
                else:
                    pods = record.colis_1_kg

                # Référence client N°1
                value += record.set_final_space_or_start('%s' % record.name, False, 35)
                # Add filler 2
                value += record.set_final_space_or_start('', add_to_start=False, number_char=2)
                # Poids en décagramme
                float_number = False
                if pods and len(str(pods).split('.')) > 1:
                    float_number = len(str(pods).split('.')[1])

                pods_value_str = str(pods).replace('.', '')
                if float_number == 1:
                    pods_value_str = pods_value_str + '0'
                if float_number > 2:
                    delet_char = abs(2 - float_number)
                    pods_value_str = pods_value_str[:-delet_char]

                pods_value_str = record.set_final_space_or_start(pods_value_str, number_char=8, char='0')
                value += pods_value_str
                # Add filler 15
                value += record.set_final_space_or_start('', add_to_start=False, number_char=15)
                #  Information client

                #  Nom destinataire
                value += record.set_final_space_or_start((record.partner_id.name or ''), add_to_start=False, number_char=35)
                # Complément d’adresse 1 ou prénom destinataire
                value += record.set_final_space_or_start((record.partner_id.street or ''), add_to_start=False, number_char=35)
                # Complément d’adresse 2
                value += record.set_final_space_or_start((record.partner_id.street2 or ''), add_to_start=False, number_char=35)
                # Complément d’adresse 3
                value += record.set_final_space_or_start('', add_to_start=False, number_char=35)
                # Complément d’adresse 4
                value += record.set_final_space_or_start('', add_to_start=False, number_char=35)
                # Complément d’adresse 5
                value += record.set_final_space_or_start('', add_to_start=False, number_char=35)
                # Code postal
                value += record.set_final_space_or_start((record.partner_id.zip or ''), add_to_start=False, number_char=10)
                # Ville
                value += record.set_final_space_or_start((record.partner_id.city or ''), add_to_start=False, number_char=35)
                # Filler
                value += record.set_final_space_or_start('', add_to_start=False, number_char=10)
                # Rue
                value += record.set_final_space_or_start((record.partner_id.street or ''), add_to_start=False, number_char=35)
                # Filler
                value += record.set_final_space_or_start('', add_to_start=False, number_char=10)
                # Code Pays destinataire
                value += record.set_final_space_or_start('', add_to_start=False, number_char=3)
                # Téléphone
                value += record.set_final_space_or_start((record.partner_id.phone or ''), add_to_start=False, number_char=20)
                # Filler
                value += record.set_final_space_or_start('', add_to_start=False, number_char=25)
                # Nom expéditeur FEDE. AVEUGLES GRAND EST
                value += record.set_final_space_or_start('FEDE. AVEUGLES GRAND EST', add_to_start=False, number_char=35)
                # Complément d’adresse 1
                value += record.set_final_space_or_start('27 RUE DE LA PREMIERE ARMEE', add_to_start=False, number_char=35)
                # Filler
                value += record.set_final_space_or_start('', add_to_start=False, number_char=35)
                # Filler
                value += record.set_final_space_or_start('', add_to_start=False, number_char=35)
                # Filler
                value += record.set_final_space_or_start('', add_to_start=False, number_char=35)
                # Filler
                value += record.set_final_space_or_start('', add_to_start=False, number_char=35)
                # Code postal
                value += record.set_final_space_or_start('67000', add_to_start=False, number_char=10)
                # Ville
                value += record.set_final_space_or_start('STRASBOURG', add_to_start=False, number_char=35)
                # Filler
                value += record.set_final_space_or_start('', add_to_start=False, number_char=10)
                # Rue
                value += record.set_final_space_or_start('27 RUE DE LA PREMIERE ARMEE', add_to_start=False, number_char=35)
                # Filler
                value += record.set_final_space_or_start('', add_to_start=False, number_char=10)
                # Code Pays
                value += record.set_final_space_or_start('FR', add_to_start=False, number_char=3)
                # Tel
                value += record.set_final_space_or_start('03.90.22.11.55', add_to_start=False, number_char=20)
                # Filler
                value += record.set_final_space_or_start('', add_to_start=False, number_char=10)
                # Commentaire 1
                value += record.set_final_space_or_start('', add_to_start=False, number_char=35)
                # Commentaire 2
                value += record.set_final_space_or_start('', add_to_start=False, number_char=35)
                # Commentaire 3
                value += record.set_final_space_or_start('', add_to_start=False, number_char=35)
                # Commentaire 4
                value += record.set_final_space_or_start('', add_to_start=False, number_char=35)
                # Date d'expédition 08/10/2020
                date_value = ''
                if record.sale_id and record.sale_id.date_order:
                    date_value = record.sale_id.date_order.strftime('%d/%m/%Y')
                value += record.set_final_space_or_start((date_value or ''), add_to_start=False, number_char=10)
                # N° de compte chargeur DPD
                value += record.set_final_space_or_start('00000264', add_to_start=False, number_char=8)
                # Code à barres
                value += record.set_final_space_or_start('', add_to_start=False, number_char=35)
                # N° de commande
                value += record.set_final_space_or_start((record.origin or ''), add_to_start=False, number_char=35)
                # Filler
                value += record.set_final_space_or_start('', add_to_start=False, number_char=29)
                # Montant de la valeur déclarée
                amount = '0'
                if record.sale_id:
                    amount = str(record.sale_id.amount_total)
                value += record.set_final_space_or_start((amount or ''), number_char=9, char='0')
                # Filler
                value += record.set_final_space_or_start('', add_to_start=False, number_char=8)
                # Référence Client 2
                value += record.set_final_space_or_start((record.partner_id.ref or ''), add_to_start=False, number_char=35)
                # Filler
                value += record.set_final_space_or_start('', add_to_start=False, number_char=1)
                # Numéro de consolidation
                value += record.set_final_space_or_start(('%s' % record.name or ''), add_to_start=False, number_char=35)
                # Filler
                value += record.set_final_space_or_start('', add_to_start=False, number_char=10)
                # E-mail expéditeur
                value += record.set_final_space_or_start('contact@aveugles-pole-travail.fr', add_to_start=False, number_char=80)
                # GSM expéditeur
                value += record.set_final_space_or_start('', add_to_start=False, number_char=35)
                # E-mail destinataire
                email_dest = ''
                # if record.sale_id and record.sale_id.partner_id:
                #     email_dest = record.sale_id.partner_id.email
                value += record.set_final_space_or_start((email_dest or ''), add_to_start=False, number_char=80)
                # GSM destinataire
                tel_dest = ''
                # if record.sale_id and record.sale_id.partner_id:
                #     tel_dest = record.sale_id.partner_id.phone
                value += record.set_final_space_or_start((tel_dest or ''), add_to_start=False, number_char=35)
                # Filler
                value += record.set_final_space_or_start('', add_to_start=False, number_char=96)
                # Identifiant point relais
                value += record.set_final_space_or_start('', add_to_start=False, number_char=8)
                # Filler
                value += record.set_final_space_or_start('', add_to_start=False, number_char=113)
                # Consolidation / type
                value += record.set_final_space_or_start('', add_to_start=False, number_char=2)
                # Consolidation / attribut
                value += record.set_final_space_or_start('', add_to_start=False, number_char=2)
                # Filler
                value += record.set_final_space_or_start('', add_to_start=False, number_char=1)
                # Predict
                value += record.set_final_space_or_start('', add_to_start=False, number_char=1)
                # Nom du contact
                value += record.set_final_space_or_start('', add_to_start=False, number_char=35)
                # DigiCode1
                value += record.set_final_space_or_start('', add_to_start=False, number_char=10)
                # DigiCode2
                value += record.set_final_space_or_start('', add_to_start=False, number_char=10)
                # Intercom
                value += record.set_final_space_or_start('', add_to_start=False, number_char=10)
                # Fin enregistrement
                value += '\r\n'

        return value

    def button_validate(self):
        self.ensure_one()
        # Ajout d'une condition sur le type d'opération
        if self.picking_type_code and self.picking_type_code == 'outgoing':
            if not self.delivery_partner_id:
                raise UserError('Vous n\'avez pas spécifié le tranporteur')
            if not self.nb_colis:
                raise UserError('Vous n\'avez pas spécifié le nombre de colis')

        res = super(StockPickingInherit, self).button_validate()
        # Ajout de ir attachment à l'objet quand on clique sur valider si l'action est de type outgoing
        if self.picking_type_code and self.picking_type_code == 'outgoing':
            if self.delivery_partner_id and self.delivery_partner_id.is_delivery_carrier and self.delivery_partner_id.delivery_carrier_edi == 'DPD':
                dpd_file, _ = self.env.ref('faal_tempo.BL_file_export')._render_qweb_text(self.id)
                b64_dpd_file = base64.b64encode(dpd_file)
                self.env['ir.attachment'].create({
                    'name': 'BL_%s' % self.name + '.txt',
                    'type': 'binary',
                    'datas': b64_dpd_file,
                    'store_fname': 'BL_%s' % self.name,
                    'res_model': self._name,
                    'res_id': self.id,
                    'mimetype': 'text/plain'
                })
            # Ajout du bon de livraison
            Utils.generate_attachement(self, 'stock.action_report_delivery', 'Bon de livraison - %s - %s' % (self.partner_id.name or '', self.name))
            # Ajout des étiquettes
            Utils.generate_attachement(self, 'faal_tempo.faal_tempo_bon_dexpedition', 'Étiquettes d\'expédition')
        return res



