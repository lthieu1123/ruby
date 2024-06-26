# -*- coding: utf-8 -*-
from odoo import SUPERUSER_ID
from odoo import api, fields, models, exceptions
from odoo.tools.translate import _
from ..commons.ruby_constant import *

import time
import datetime
import logging
import re
import ctypes
import json
import base64
import io
import pandas as pd
import math

_logger = logging.getLogger(__name__)

class LazadaReconcileFee(models.TransientModel):
    _name = 'lazada.reconcile.fee'
    _description = 'Lazada Reconcile Fee'

    name = fields.Text('name',default='Đối soát chi phí')
    date_start = fields.Datetime('Từ ngày')
    date_end = fields.Datetime('Đến ngày')
    price_support = fields.Float('Trợ Giá')
    price_over = fields.Float('Price Over')
    file_data = fields.Binary(string='File')
    file_name = fields.Char('File Name')
    csv_file = fields.Binary(string='Chênh lệch phí vận chuyển')
    csv_name = fields.Char('CSV File Name', default='doi_soat_van_chuyen.csv')
    has_csv = fields.Boolean('Has CSV',)
    state = fields.Selection(selection=[('begin','Begin'),('end','End')],string='State', default='begin')

    def _create_csv_file(self, data_csv):
        if len(data_csv):
            order_number = []
            fee_by_cus = []
            fee_by_seller = []
            fee_voucher = []
            fee_support = []
            delta_price = []
            for key in data_csv:
                order_number.append(key)
                fee_by_cus.append(data_csv[key][SHIP_FEE_BY_CUS])
                fee_by_seller.append(data_csv[key][SHIP_FEE_BY_SELLER])
                fee_voucher.append(data_csv[key][SHIP_FEE_VOUCHER_LAZADA])
                fee_support.append(data_csv[key]['tro_gia'])
                _support_price = data_csv[key][SHIP_FEE_BY_SELLER] - data_csv[key][SHIP_FEE_BY_CUS] - data_csv[key]['tro_gia'] - data_csv[key][SHIP_FEE_VOUCHER_LAZADA]
                delta_price.append(_support_price)
            df = pd.DataFrame({
                'Order No.': order_number,
                SHIP_FEE_BY_CUS: fee_by_cus,
                SHIP_FEE_BY_SELLER: fee_by_seller,
                SHIP_FEE_VOUCHER_LAZADA: fee_voucher,
                'Price Support': fee_support,
                'Chênh lệch': delta_price
            })
            df.to_csv('file_csv.csv',encoding='utf-8')
            _file = open('file_csv.csv','rb')
            _encode = base64.encodestring(_file.read())
            return _encode
        else:
            return False

    def _get_list_order_number_with_date(self):
        # date_start = datetime.datetime.combine(self.date_start,datetime.time.min)
        # date_end = datetime.datetime.combine(self.date_end,datetime.time.max)
        date_start = self.date_start
        date_end = self.date_end
        if self.date_start > self.date_end:
            raise exceptions.ValidationError('Ngày bắt đầu phải bé hơn hoặc bằng ngày kết thúc')
        _li_order_number = self.env['sale.order.management'].search([
            ('created_at','>=',date_start),
            ('created_at','<=',date_end),
            ('state','!=','pending')
        ]).mapped(lambda r: r.order_number)
        return _li_order_number

    def btn_reconcile(self):
        self.ensure_one()
        shop_code = self.file_name.split('.')[0]
        shop_id = self.env['sale.order.management.shop'].search([
            ('code','=',shop_code)
        ])
        if not len(shop_id):
            raise exceptions.ValidationError(_('Không tìm thấy shop có mã là: "[{}]"').format(shop_code))
        
        data_file = base64.b64decode(self.file_data)
        csv_filelike = io.BytesIO(data_file)
        try:
            #result = pd.read_csv(csv_filelike,sep=',',encoding='utf8', usecols=[FEE_NAME, AMOUNT, ORDER_NO, ORDER_STATUS], dtype={ORDER_NO: str,})
            result = pd.read_excel(csv_filelike,dtype={ORDER_NO: str,})
        except:
            #result = pd.read_csv(csv_filelike,sep=';',encoding='utf8', usecols=[FEE_NAME, AMOUNT, ORDER_NO, ORDER_STATUS], dtype={ORDER_NO: str,})
            result = pd.read_excel(csv_filelike,dtype={ORDER_NO: str,})
        data_csv = {}
        print('going to loop')
        for index, row in result.iterrows():
            if row[ORDER_STATUS] == 'Pending':
                continue

            order_number = row[ORDER_NO]
            _li_order_number = self._get_list_order_number_with_date()
            if order_number not in _li_order_number:
                continue

            fee_name = row[FEE_NAME]
            amount = abs(float(row[AMOUNT]))
            if fee_name == SHIP_FEE_BY_CUS or fee_name == SHIP_FEE_BY_SELLER or fee_name == ITEM_PRICE or fee_name == SHIP_FEE_VOUCHER_LAZADA:
                
                if data_csv.get(order_number, False):
                    data_csv[order_number][fee_name] = data_csv[order_number][fee_name] + amount
                else:
                    data_csv.update({
                        order_number: {
                            SHIP_FEE_BY_CUS: 0.0,
                            SHIP_FEE_BY_SELLER: 0.0,
                            ITEM_PRICE: 0.0,
                            SHIP_FEE_VOUCHER_LAZADA: 0.0,
                        }
                    })
                    data_csv[order_number][fee_name] = amount
        
        # Remove order_number in data_csv that has the same fee
        _li_key = []
        for order_number in data_csv:
            if data_csv[order_number][ITEM_PRICE] >= self.price_over:
                data_csv[order_number].update({'tro_gia': self.price_support})
                sum_total = data_csv[order_number][SHIP_FEE_BY_SELLER] - data_csv[order_number][SHIP_FEE_BY_CUS] - data_csv[order_number][SHIP_FEE_VOUCHER_LAZADA] - self.price_support
            else:
                data_csv[order_number].update({'tro_gia': 0.0})
                sum_total = data_csv[order_number][SHIP_FEE_BY_SELLER] - data_csv[order_number][SHIP_FEE_BY_CUS] - data_csv[order_number][SHIP_FEE_VOUCHER_LAZADA]
            if abs(sum_total) <= 1e-4:
                _li_key.append(order_number)
        for key in _li_key:
            del data_csv[key]
        
        csv_file = self._create_csv_file(data_csv)
        print('out loop to loop')
        vals = {
            'has_csv': False,
            'state': 'end',
        }
        if csv_file:
            vals.update({
                'has_csv': True,
                'csv_file': csv_file
            })
        print('Vals: ',vals)
        self.write(vals)
        return {
            'name': 'Đối Soát Chi Phí',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            # 'view_id': False,
            'res_model': self._name,
            'res_id': self.id,
            'views': [(False, 'form')],
            'target': 'new',
        }
          
