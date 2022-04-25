from odoo import api, fields, models, modules, _


class Partner(models.Model):
    _inherit = 'res.partner'
    _rec_name = 'display_name'

    ape = fields.Char(string=u'APE')
    fax = fields.Char(string=u'Fax')
    phone2 = fields.Char(string=u'Téléphone 2')
    last_piece = fields.Date(string=u'Dernière pièce')
    credit_demande = fields.Boolean(string=u'Crédit Demande')
    credit_accorde = fields.Boolean(string=u'Crédit Accordé')

    vendor_code = fields.Char(string=u'Identification commercial')

    rank_user_vallibre_one = fields.Integer(string=u'Rang Utilisateur VALLIBRE1')
    rank_user_vallibre_two = fields.Integer(string=u'Rang Utilisateur VALLIBRE2')

    etablishement_id = fields.Many2one('etablishements', string=u'Etablissement')

    # Questions
    relance_reglement = fields.Char(string=u'Relance réglement')
    etat_risque = fields.Char(string=u'Etat risque')

    ref_aux = fields.Char(string=u'Ref Auxiliaire')

    ref_is_mandatory = fields.Boolean(string=u'Bon d\'engagement obligatoire')

    is_delivery_carrier = fields.Boolean(string=u'Transporteur', default=False, help="Cocher cette case si ce partenaire est un transporteur. Il pourra alors être sélectionné comme transporteur sur l'expédition")
    delivery_carrier_edi = fields.Selection(string=u'Générer fichier BL', selection=[('DPD', 'DPD')], help="Indiquer, si nécessaire, le type de BL à générer pour ce transporteur.")

    @api.onchange('is_delivery_carrier')
    def onchange_is_delivery_carrier(self):
        if not self.is_delivery_carrier:
            self.delivery_carrier_edi = None

    @api.model
    def _get_default_address_format(self):
        return "%(street)s\n%(street2)s\n%(zip)s\t%(city)s\n%(country_name)s"

    def get_company_followup_name(self):
        # Test si le vendeur est dans l'équipe de vente Repères
        return True if self.user_id and self.user_id.sale_team_id and self.user_id.sale_team_id.id == self.env.ref('faal_tempo.crm_sale_5').id else False

    @api.depends('is_company', 'name', 'parent_id.display_name', 'type', 'company_name', 'title', 'title.name', 'street', 'street2', 'zip', 'city', 'ref', 'customer_rank')
    def _compute_display_name(self):
        for partner in self:
            if partner.is_company and partner.ref:
                partner.display_name = '[' + partner.ref + '] ' + partner.name
            elif partner.parent_id and partner.type == 'contact' and partner.title and partner.title.name:
                partner.display_name = partner.parent_id.name + ', ' + partner.title.name + ' ' + partner.name
            elif partner.parent_id and partner.type != 'contact':
                address = []
                if partner.street:
                    address.append(partner.street)
                if partner.street2:
                    address.append(partner.street2)
                if partner.zip:
                    address.append(partner.zip)
                if partner.city:
                    address.append(partner.city)
                partner.display_name = partner.parent_id.name + ', ' + ' '.join(address)
            else:
                parent_name = ''
                if partner.parent_id and partner.parent_id.name:
                    parent_name = partner.parent_id.name + ', '
                partner.display_name = parent_name + partner.name

    def _get_name(self):
        return self.display_name

    def recompute_display_name(self):
        for record in self.env['res.partner'].search([('active', 'in', [False, True]), ('name', 'like', '%@@@')], limit=10000):
            # Forcer le recalcule du champ display_name
            record.write({'name': record.name.strip('@')})
