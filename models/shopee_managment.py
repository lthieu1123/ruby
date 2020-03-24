# -*- coding: utf-8 -*-

# Import libs
import os
import pandas as pd
import datetime
import base64
import io
import logging

from odoo import api, models, fields, exceptions
from odoo.tools.translate import _
from odoo.addons import decimal_precision as dp
from ..commons.ruby_constant import *

class ShopeeManagment(models.Model):
    _name = "shopee.management"
    _description = "Shopee Management"

    