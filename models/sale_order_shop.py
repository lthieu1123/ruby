# -*- coding: utf-8 -*-

from enum import Enum
from odoo import SUPERUSER_ID
from odoo import api, fields, models, exceptions
from odoo.tools.translate import _

import time
import datetime
import logging
import re
import ctypes

_logger = logging.getLogger(__name__)

class SaleOrderManagmentShop(models.Model):
    _name = 'sale.order.management.shop'
    _description = 'Sale Order Management Shop'

    name = fields.Char('Shop name', required=True)
    code = fields.Char('Shop Code', required=True)

    # SQL Contraints
    _sql_constraints = [('unique_tracking', 'unique(code)',
                         _('Code must be unique'))]

class SaleOrderManagmentShopeeShop(models.Model):
    _name = 'sale.order.management.shopee.shop'
    _description = 'Sale Order Management Shopee Shop'

    name = fields.Char('Shop name', required=True)
    code = fields.Char('Shop Code', required=True)

    # SQL Contraints
    _sql_constraints = [('unique_tracking', 'unique(code)',
                         _('Code must be unique'))]