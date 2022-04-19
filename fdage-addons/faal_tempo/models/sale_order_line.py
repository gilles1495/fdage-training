from odoo import api, fields, models
from odoo.tools import float_compare


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    list_price = fields.Float(
        string="Prix Liste",
        compute='_get_list_price',
    )

    amount_within_10_pc_of_list_price = fields.Boolean(
        string="Montant ±10% du prix liste",
        help="Si le montant est compris entre +10% et -10% du prix liste",
        compute='_get_amount_within_10_pc_of_list_price',
    )
    unit_price_discount = fields.Float(string=u'Prix unitaire avec remise', compute='_get_unit_price')

    def _get_unit_price(self):
        for item in self:
            if item.discount and item.price_unit:
                item.unit_price_discount = item.price_unit - ((item.discount/100) * item.price_unit )
            else:
                item.unit_price_discount = item.price_unit if item.price_unit else 0.0

    @staticmethod
    def _get_display_price_custom(item):
        """Copy of sale.order.line::_get_display_price() but without self"""
        product = item.product_id
        no_variant_attributes_price_extra = [
            ptav.price_extra for ptav in item.product_no_variant_attribute_value_ids.filtered(
                lambda ptav:
                    ptav.price_extra and
                    ptav not in product.product_template_attribute_value_ids
            )
        ]
        if no_variant_attributes_price_extra:
            product = product.with_context(
                no_variant_attributes_price_extra=tuple(no_variant_attributes_price_extra)
            )

        if item.order_id.pricelist_id.discount_policy == 'with_discount':
            return product.with_context(pricelist=item.order_id.pricelist_id.id, uom=item.product_uom.id).price
        product_context = dict(item.env.context, partner_id=item.order_id.partner_id.id, date=item.order_id.date_order, uom=item.product_uom.id)

        final_price, rule_id = item.order_id.pricelist_id.with_context(product_context).get_product_price_rule(product or item.product_id, item.product_uom_qty or 1.0, item.order_id.partner_id)
        base_price, currency = item.with_context(product_context)._get_real_price_currency(product, rule_id, item.product_uom_qty, item.product_uom, item.order_id.pricelist_id.id)
        if currency != item.order_id.pricelist_id.currency_id:
            base_price = currency._convert(
                base_price, item.order_id.pricelist_id.currency_id,
                item.order_id.company_id or item.env.company, item.order_id.date_order or fields.Date.today())

        return max(base_price, final_price)

    @api.depends('order_id', 'product_id', 'tax_id', 'company_id')
    def _get_list_price(self):
        for item in self:
            if all([item.order_id.pricelist_id,
                    item.order_id.partner_id,
                    item.product_id,
                    item.tax_id,
                    item.company_id]):
                item.list_price = self.env['account.tax']._fix_tax_included_price_company(
                    self._get_display_price_custom(item),
                    item.product_id.taxes_id,
                    self.tax_id,
                    self.company_id
                )
            else:
                item.list_price = None

    @api.depends('order_id', 'product_id', 'price_unit')
    def _get_amount_within_10_pc_of_list_price(self):
        precision = self.env['decimal.precision'].precision_get('Comparaison prix unitaire et prix liste')
        for item in self:
            list_price = item.list_price
            if not list_price:
                item.amount_within_10_pc_of_list_price = True
                continue
            line_amount = item.price_unit
            list_price_plus_10_pc = list_price * 1.1
            list_price_minus_10_pc = list_price * 0.9
            item.amount_within_10_pc_of_list_price = (
                float_compare(line_amount, list_price_plus_10_pc, precision_digits=precision) != 1  # not greater then
                and float_compare(line_amount, list_price_minus_10_pc, precision_digits=precision) != -1  # not lesser than
            )
