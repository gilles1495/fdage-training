# -*- coding: utf-8 -*-
#################################################################################
# Author      : Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# Copyright(c): 2015-Present Webkul Software Pvt. Ltd.
# All Rights Reserved.
#
#
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#
# You should have received a copy of the License along with this program.
# If not, see <https://store.webkul.com/license.html/>
#################################################################################
{
  "name"                 :  "Stock Force Assign",
  "summary"              :  """The module adds the feature to validate partial deliveries in Odoo. The user can force a full or partial delivery validation if the product stock is insufficient.""",
  "category"             :  "Operations/Inventory",
  "version"              :  "13.0.1.0.0",
  "author"               :  "Webkul Software Pvt. Ltd.",
  "license"              :  "Other proprietary",
  "website"              :  "https://store.webkul.com/Odoo-Stock-Force-Assign.html",
  "description"          :  """By installing this module, you will get the feature full or partial delivery validation if the product stock is insufficient.""",
  "live_test_url"        :  "http://odoodemo.webkul.com/?module=wk_force_assign",
  "depends"              :  ['stock'],
  "data"                 :  [
                              'wizard/partial_force_assign_views.xml',
                              'views/stock_picking_views.xml',
                            ],
  "images"               :  ['static/description/Banner.png'],
  "application"          :  True,
  "installable"          :  True,
  "auto_install"         :  False,
  "price"                :  39,
  "currency"             :  "USD",
  "pre_init_hook"        :  "pre_init_check",
}