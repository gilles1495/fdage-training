from odoo import api, fields, models, modules


class ProductsCategoryInherit(models.Model):
    _inherit = 'product.category'

    code = fields.Char(string='Code')


class ProductProductInherit(models.Model):
    _inherit = 'product.product'

    def get_product_multiline_description_sale(self):
        """ Compute a multiline description of this product, in the context of sales
                (do not use for purchases or other display reasons that don't intend to use "description_sale").
            It will often be used as the default description of a sale order line referencing this product.
        """
        name = self.name
        if self.description_sale:
            name += '\n' + self.description_sale

        return name