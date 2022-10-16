# -*- coding: utf-8 -*-

import base64
import codecs
import collections
import unicodedata

import chardet
import datetime
import io
import itertools
import logging
import psycopg2
import operator
import os
import re
import requests

from PIL import Image

from odoo import api, fields, models
from odoo.exceptions import AccessError
from odoo.tools.translate import _
from odoo.tools.mimetypes import guess_mimetype
from odoo.tools import config, DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, pycompat


class Import(models.TransientModel):
    _inherit = 'base_import.import'

    @api.multi
    def do(self, fields, columns, options, dryrun=False):
        import_result = super().do(fields, columns, options, dryrun)
        if not dryrun:
            result_ids = self.env[self.res_model].browse(import_result.get('ids'))
            file_name = self.file_name.split('.')[0]
            shop_id = self.env['sale.order.management.shop'].search([
                ('code','=',file_name)
            ])
            if not len(shop_id):
                result_ids.unlink()
                return {
                    'messages': [{
                        'type': 'error',
                        'message': pycompat.text_type(_('Cannot find shop with shop code is: "[{}]"').format(file_name)),
                        'record': False,
                    }]
                }
            result_ids.sudo().update({
                'shop_id': shop_id.id
            })     
        return import_result
    