# -*- coding: utf-8 -*-

from enum import Enum
from odoo import SUPERUSER_ID
from odoo import api, fields, models, exceptions
from odoo.addons import decimal_precision as dp
from odoo.tools.translate import _
from ..commons.ruby_constant import *

import time
import datetime
import logging
import re
import ctypes
import base64
import io
import json
import pandas as pd

regex = r';Item (\\d+);'

_logger = logging.getLogger(__name__)

class LzaOriginPrice(models.TransientModel):
    _name = 'lza.origin.price'
    _description = 'Lazada origin price'

    sum_report_id = fields.Many2One('lzd.sum.price.report.wizard','lza sum price report',ondelete='cascade')
    order_item_id = fields.Char('Order Item No.')
    seller_sku = fields.Char('Seller SKU')
    origin_price = fields.Float('Origin Price')

class LzaSumPriceReport(models.TransientModel):
    _name = 'lzd.sum.price.report.wizard'
    _description = 'Lazada Sum Price Report'

    name = fields.Char('Name', defualt="Báo Cáo Tổng Chi Phí")
    date_start = fields.Datetime('Từ ngày')
    date_end = fields.Datetime('Đến ngày')
    file_data = fields.Binary(string='File')
    file_name = fields.Char('File Name')
    excel_file = fields.Binary(string='Báo Cáo Tổng Chi Phí Hàng Hóa')
    excel_name = fields.Char('CSV File Name', default='bao_cao_chi_phi.csv')
    has_file = fields.Boolean('Has CSV',)
    state = fields.Selection(selection=[('begin','Begin'),('end','End')],string='State', default='begin')
    origin_price = fields.One2many('lza.origin.price','sum_report_id','Origin Price Item')
    
    @api.multi
    def btn_reconcile(self):
        context = self.env.context.copy()
        data_file = base64.b64decode(self.file_data)
        csv_filelike = io.BytesIO(data_file)
        result = pd.read_csv(csv_filelike,sep=',',encoding='utf-8', usecols=[FEE_NAME, AMOUNT, ORDER_NO, ORDER_STATUS,ODER_ITEM_NO, SELLER_SKU,COMMENT], dtype={ORDER_NO: str,ODER_ITEM_NO:str})
        _now = datetime.datetime.timestamp(datetime.datetime.now())
        order_number = []
        order_item_number = []
        fee_name = []
        amount = []
        _dict_item = {}
        for index, row in result.iterrows():
            fee_name = row[FEE_NAME].strip()
            amount = row[AMOUNT]
            order_item_number = row[ODER_ITEM_NO]
            if fee_name == MARKETING_SOLUTION_SOCIAL_MEDIA_ADVERTISING:
                comment = row[MARKETING_SOLUTION_SOCIAL_MEDIA_ADVERTISING]
                mo = re.search(regex,comment)
                if mo:
                    order_item_number = mo.group(1)
            order_number.append(row[ORDER_NO])
            order_item_number.append(order_item_number)
            fee_name.append(fee_name)
            amount.append(amount)
            _dict_item.update({
                str(order_item_number): SELLER_SKU
            })
        _list_item = list(dict.fromkeys(order_item_number))
        for _item in _list_item:
            self.env['lza.origin.price'].create({
                'sum_report_id': self.id,
                'order_item_id': _item,
                'seller_sku': _dict_item.get(str(_item))
            })
        context.update({
            'order_number': order_number,
            'order_item_number': order_item_number,
            'fee_name': fee_name,
            'amount': amount,
            '_list_item': _list_item,
        })
        view_id = self.env.ref()
        return {
            'name': 'Báo Cáo Chi Phí Sản Phẩm',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            # 'view_id': False,
            'res_model': self._name,
            'res_id': self.id,
            'views': [(view_id.id, 'form')],
            'target': 'main',
        }
    

    @api.multi
    def btn_apply(self):
        self.ensure_one()
        
            
