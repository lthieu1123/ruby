# -*- coding: utf-8 -*-
from odoo import SUPERUSER_ID
from odoo import api, fields, models, exceptions
from odoo.tools.translate import _


import time
import datetime
import logging
import re
import ctypes

_logger = logging.getLogger(__name__)

class SetOrderAsb(models.AbstractModel):
    _name = "set.order.abs"
    _description = "Set Order Abstract"

    