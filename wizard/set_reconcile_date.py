# -*- coding: utf-8 -*-

from odoo import SUPERUSER_ID
from odoo import api, fields, models, exceptions
from odoo.tools.translate import _
from ..commons.ruby_constant import *

import pandas as pd
import time
import datetime
import logging
import re
import ctypes
import json

REGEX = "\d+\.(\w+)"

_logger = logging.getLogger(__name__)

class ShopAnnounce(models.TransientModel):
    _name = 'set.reconcile.date'
    _description = 'Set Reconcile Date'

    def _get_default_res_model(self):
        return self.env.context.get('default_res_model',False)

    date_start = fields.Datetime('Từ ngày')
    date_end = fields.Datetime('Đến ngày')
    res_model = fields.Char('res_model', default=_get_default_res_model)

    @api.model
    def _calculate_price_by_order_number(self, rec_ids, sale_director_file, _sale_done_director):
        for entry in sale_director_file:
            directory = "{}/{}".format(_sale_done_director,entry)
            try:
                result = pd.read_csv(directory,sep=',',encoding='utf8')
            except:
                result = pd.read_csv(directory,sep=';',encoding='utf8')
            
            for index, row in result.iterrows():
                fee_name = row[FEE_NAME].strip()
                if fee_name != ITEM_PRICE:
                    continue
                order_id = int(row[ODER_ITEM_NO])
                rec = rec_ids.filtered(lambda r: r.order_item_id == str(order_id))
                if rec.id:
                    rec.update({
                        'transaction_date': pd.to_datetime(row[TRANSACTION_DATE]).date(),
                        'state': 'done'
                    })

    @api.multi
    def btn_reconcile(self):
        so_mgt = self.env['sale.order.management']
        context = self.env.context.copy()
        _li_shop = context.get('default_shop_id')
        sale_director_file = context.get('sale_director_file')
        _sale_done_director = context.get('sale_done_director')
        # start_datetime = datetime.datetime.combine(self.date_start,datetime.time.min)
        # end_datetime = datetime.datetime.combine(self.date_end,datetime.time.max)
        start_datetime = self.date_start
        end_datetime = self.date_end
        #Veiry date_start < date_end
        if self.date_start > self.date_end:
            raise exceptions.ValidationError('Ngày bắt đầu phải bé hơn hoặc bằng ngày kết thúc')
        #Verify date end data will be import first
        count = so_mgt.search_count([
            ('created_at','>=',end_datetime)
        ])
        if not (count):
            raise exceptions.ValidationError(_('Không tìm thấy dữ liệu đến ngày kết thúc {}').format(str(self.date_end)))
        #Find all import data from start date to end date
        rec_ids = so_mgt.search([
            ('created_at','>=',start_datetime),
            ('created_at','<=',end_datetime),
            ('state','=','delivered'),
            ('shop_id','in',_li_shop)
        ])
        self._reconcile_lazada_data(rec_ids,sale_director_file,_sale_done_director)
        result = rec_ids.filtered(lambda r: r.state == 'delivered')
        return {
            'name': _('Đối Soát Đơn Hàng'),
            'view_type': 'form',
            'view_mode': 'tree',
            'view_id': False,
            'res_model': 'sale.order.management',
            'context': {},
            'domain': [('id','in',result.ids)],
            'target': 'main',
            'type': 'ir.actions.act_window',
        }

    @api.multi
    def btn_reconcile_shopee(self):
        self.ensure_one()
        so_mgt = self.env['shopee.management']
        context = self.env.context.copy()
        _li_shop = context.get('default_shop_id')
        sale_director_file = context.get('sale_director_file')
        _sale_done_director = context.get('sale_done_director')
        # start_datetime = datetime.datetime.combine(self.date_start,datetime.time.min)
        # end_datetime = datetime.datetime.combine(self.date_end,datetime.time.max)
        start_datetime = self.date_start
        end_datetime = self.date_end
        #Veiry date_start < date_end
        if self.date_start > self.date_end:
            raise exceptions.ValidationError('Ngày bắt đầu phải bé hơn hoặc bằng ngày kết thúc')
        count = so_mgt.search_count([
            ('ngay_dat_hang','>=',end_datetime)
        ])
        if not (count):
            raise exceptions.ValidationError(_('Không tìm thấy dữ liệu đến ngày kết thúc {}').format(str(self.date_end)))
        rec_ids = so_mgt.search([
            ('ngay_dat_hang','>=',start_datetime),
            ('ngay_dat_hang','<=',end_datetime),
            ('state','=','delivered'),
            ('shop_id','in',_li_shop)
        ])
        self._reconcile_shopee_data(rec_ids,sale_director_file,_sale_done_director)
        result = rec_ids.filtered(lambda r: r.state == 'delivered')
        return {
            'name': _('Đối Soát Đơn Hàng'),
            'view_type': 'form',
            'view_mode': 'tree',
            'view_id': False,
            'res_model': 'shopee.management',
            'context': {},
            'domain': [('id','in',result.ids)],
            'target': 'main',
            'type': 'ir.actions.act_window',
        }

    @api.model
    def _reconcile_lazada_data(self, rec_ids, sale_director_file, _sale_done_director):
        for entry in sale_director_file:
            directory = "{}/{}".format(_sale_done_director,entry)
            try:
                result = pd.read_csv(directory,sep=',',encoding='utf8')
            except:
                result = pd.read_csv(directory,sep=';',encoding='utf8')
            
            for index, row in result.iterrows():
                fee_name = row[FEE_NAME].strip()
                if fee_name != ITEM_PRICE:
                    continue
                order_id = int(row[ODER_ITEM_NO])
                rec = rec_ids.filtered(lambda r: r.order_item_id == str(order_id))
                if rec.id:
                    rec.update({
                        'transaction_date': pd.to_datetime(row[TRANSACTION_DATE]).date(),
                        'state': 'done'
                    })
    
    @api.model
    def _reconcile_shopee_data(self, rec_ids, sale_director_file, _sale_done_director):
        for entry in sale_director_file:
            directory = "{}/{}".format(_sale_done_director,entry)
            match = re.search(REGEX,entry)
            if match:
                extension = match.group(1)
            if extension == "csv":
                try:
                    result = pd.read_csv(directory,sep=',',encoding='utf8')
                except:
                    result = pd.read_csv(directory,sep=';',encoding='utf8')
            elif extension == "xlsx" or extension == "xls":
                result = pd.read_excel(directory,dtype={'Mã đơn hàng': str})
            else:
                raise exceptions.ValidationError('Định dạng file phải là: [cvs,xls,xlsx]')
            max_row = 10
            max_row = len(result) if max_row > len(result) else max_row
            header_index = 0
            column_index = 0
            for i in range(0,max_row):
                _li_data = list(result.loc[i])
                if 'Mã đơn hàng' in _li_data:
                    header_index = i
                    break
            _li_header = list(result.loc[header_index])
            for i in range(0,len(_li_header)):
                if 'Mã đơn hàng' == _li_header[i]:
                    column_index = i
                    break
            for i in range(column_index+1,len(result)):
                ma_don_hang = result.loc[i][column_index]
                item = self.env['shopee.management'].search([
                    ('ma_don_hang','=',ma_don_hang)
                ])
                item = rec_ids.filtered(lambda r: r.ma_don_hang == ma_don_hang)
                if len(item):
                    item.write({
                        'state': 'done'
                    })