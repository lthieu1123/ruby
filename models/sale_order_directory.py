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


class LazadaDirectory(models.Model):
    _name = 'lazada.directory'
    _description = 'Lazada Directory'

    name = fields.Selection(string='Loại thư mục', selection=[('update','Cập nhật mới'),('reconcile','Đối soát')], required=True)
    directory = fields.Char('Đường dẫn thư mục')

class ShopeeDirectory(models.Model):
    _name = 'shopee.directory'
    _description = 'Shopee Directory'

    name = fields.Selection(string='Loại thư mục', selection=[('update','Cập nhật mới'),('reconcile','Đối soát')], required=True)
    directory = fields.Char('Đường dẫn thư mục')