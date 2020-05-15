# -*- coding: utf-8 -*-
from odoo import SUPERUSER_ID
from odoo import api, fields, models, exceptions
from odoo.tools.translate import _


import time
import datetime
import logging
import re
import ctypes
import json
import base64


class TikiSendoWarning(models.TransientModel):
    _name = 'tiki.sendo.warning'
    _descriptin = 'Tiki Sendo Warning'

    def tiki_warning(self):
        raise exceptions.ValidationError('Tiki vẫn chưa được triển khai')
        # return {
        #     'warning': {
        #         'title': 'Lỗi',
        #         'message': 'Tiki Vẫn chưa được triển khai'
        #     }
        # }


    def sendo_warning(self):
        raise exceptions.ValidationError('Sendo vẫn chưa được triển khai')