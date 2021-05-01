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
import numpy as np

regex = r';Item (\\d+);'

_logger = logging.getLogger(__name__)


class LzaOriginPrice(models.TransientModel):
    _name = 'lza.origin.price'
    _description = 'Lazada origin price'

    sum_report_id = fields.Many2one(
        'lzd.sum.price.report.wizard', 'lza sum price report', ondelete='cascade')
    seller_sku = fields.Char('Seller SKU')
    origin_price = fields.Float('Giá Gốc', required=True, default=0.0)


class LzaSumPriceReport(models.TransientModel):
    _name = 'lzd.sum.price.report.wizard'
    _description = 'Lazada Sum Price Report'

    name = fields.Char('Name', defualt="Báo Cáo Tổng Chi Phí")
    date_start = fields.Datetime('Từ ngày')
    date_end = fields.Datetime('Đến ngày')
    file_data = fields.Binary(string='File')
    file_name = fields.Char('File Name')
    excel_file = fields.Binary(string='Báo Cáo Tổng Chi Phí Hàng Hóa')
    excel_name = fields.Char('Excel File Name',)
    has_file = fields.Boolean('Has Excel')
    state = fields.Selection(selection=[(
        'begin', 'Begin'), ('proceed', 'Proceed'), ('end', 'End')], string='State', default='begin')
    origin_price_ids = fields.One2many(
        'lza.origin.price', 'sum_report_id', 'Origin Price Item')
    data = fields.Char('Data')

    def _return_action(self):
        context = self.env.context.copy()
        return {
            'name': 'Báo Cáo Chi Phí Sản Phẩm',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'context': context,
            'res_model': self._name,
            'res_id': self.id,
            'target': 'new',
        }

    @api.multi
    def btn_reconcile(self):
        context = self.env.context.copy()
        data_file = base64.b64decode(self.file_data)
        csv_filelike = io.BytesIO(data_file)
        result = pd.read_csv(csv_filelike, sep=',', encoding='utf-8', usecols=[
                             FEE_NAME, AMOUNT, ORDER_NO, ORDER_STATUS, ODER_ITEM_NO, SELLER_SKU, COMMENT], dtype={ORDER_NO: str})
        _now = datetime.datetime.timestamp(datetime.datetime.now())
        order_number = []
        seller_sku = []
        fee_name = []
        amount = []
        _dict_item = {}
        for i, r in result.iterrows():
            if r[ODER_ITEM_NO] == 'nan':
                continue
            _dict_item.update({
                str(r[ODER_ITEM_NO]): r[SELLER_SKU]
            })
        for index, row in result.iterrows():
            _fee_name = row[FEE_NAME].strip()
            _seller_sku = row[SELLER_SKU]
            if _fee_name == MARKETING_SOLUTION_SOCIAL_MEDIA_ADVERTISING:
                comment = row[COMMENT]
                mo = re.search(regex, comment)
                if mo:
                    order_item_number = mo.group(1)
                    _seller_sku = _dict_item.get(order_item_number)
            order_number.append(str(row[ORDER_NO]))
            seller_sku.append(_seller_sku)
            fee_name.append(_fee_name)
            amount.append(row[AMOUNT])
        _list_seller = list(dict.fromkeys(seller_sku))
        for _item in _list_seller:
            self.env['lza.origin.price'].create({
                'sum_report_id': self.id,
                'seller_sku': _item
            })
        # context.update({
        #     'order_number': order_number,
        #     'fee_name': fee_name,
        #     'seller_sku': seller_sku,
        #     'amount': amount,
        #     '_list_seller': _list_seller,
        # })
        _data = {
            'order_number': order_number,
            'fee_name': fee_name,
            'seller_sku': seller_sku,
            'amount': amount,
        }
        self.write({
            'state': 'proceed',
            'data': json.dumps(_data)
        })
        return {
            'name': 'Báo Cáo Chi Phí Sản Phẩm',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            # 'context': context,
            'res_model': self._name,
            'res_id': self.id,
            'target': 'new',
        }

    def _create_pivot_table(self, df=None):
        print("df: ",df)
        table = pd.pivot_table(df, values=[AMOUNT], index=[ORDER_NO, SELLER_SKU], columns=[
                               FEE_NAME], aggfunc=np.sum, margins=True)
        _tmp_sum_table = pd.concat([d.append(d.sum().rename((k, 'Total')))for k, d in table.groupby(
            level=0)]).append(table.sum().rename(('Grand', 'Total')))
        df_sum = pd.concat([d.assign(IS_GET_INCOME=d['Amount']['All'] > 0.00)
                            for k, d in _tmp_sum_table.groupby(level=0)])
        name = '{}.xlsx'.format(
            datetime.datetime.now().strftime("%d%m%y%H%M%S"))
        df_sum.to_excel(name)
        _file = open(name, 'rb')
        _encode = base64.encodestring(_file.read())
        self.write({
            'excel_file': _encode,
            'excel_name': 'bao_cao_chi_phi_{}'.format(name),
            'has_file': True,
            'state': 'end',
        })
        return self

    @api.multi
    def btn_apply(self):
        self.ensure_one()
        print('self.origin_price_ids.origin_price: ',self.origin_price_ids.mapped('origin_price'))
        _data = json.loads(self.data) if self.data else {}
        seller_sku = _data.get('seller_sku')
        order_number = _data.get('order_number')
        fee_name = _data.get('fee_name')
        amount = _data.get('amount')
        _len = range(len(seller_sku))
        for i in _len:
            _amount = self.origin_price_ids.filtered(
                lambda r: r.seller_sku == seller_sku[i])
            _order_number = order_number[i]
            _fee_name = 'X Giá Gốc'
            seller_sku.append(seller_sku[i])
            fee_name.append(_fee_name)
            order_number.append(_order_number)
            amount.append(_amount.origin_price)
        df = pd.DataFrame({
            ORDER_NO: order_number,
            AMOUNT: amount,
            SELLER_SKU: seller_sku,
            FEE_NAME: fee_name
        })
        _encode = self._create_pivot_table(df=df)
        return self._return_action()

    @api.multi
    def btn_bypass(self):
        self.ensure_one()
        _data = json.loads(self.data) if self.data else {}
        seller_sku = _data.get('seller_sku')
        order_number = _data.get('order_number')
        fee_name = _data.get('fee_name')
        amount = _data.get('amount')
        seller_sku.append(seller_sku[0])
        order_number.append(order_number[0])
        fee_name.append('X Giá Gốc')
        amount.append(0.0)
        df = pd.DataFrame({
            ORDER_NO: order_number,
            AMOUNT: amount,
            SELLER_SKU: seller_sku,
            FEE_NAME: fee_name
        })
        _encode = self._create_pivot_table(df=df)
        return self._return_action()
