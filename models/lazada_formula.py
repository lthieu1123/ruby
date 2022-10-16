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


class LazadaFormula(models.Model):
    _name = 'lazada.formula'
    _description = 'Lazada Formula'

    name = fields.Char('Tên trường', required=True)
    operator = fields.Selection(string='Toán tử', selection=[('add','+'),('subtract','-')])

    _sql_constraints = [('unique_name', 'unique(name)', _('Tên trường đã tồn tại'))]