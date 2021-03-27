# -*- coding: utf-8 -*-

from odoo import SUPERUSER_ID
from odoo import api, fields, models, exceptions
from odoo.tools.translate import _

import pandas as pd
import time
import datetime
import logging
import re
import ctypes
import json

REGEX = "\d+\.(\w+)"

_logger = logging.getLogger(__name__)

ODER_ITEM_NO = 'Order Item No.'
TRANSACTION_DATE = 'Transaction Date'
FEE_NAME = 'Fee Name'
AMOUNT = 'Amount'
ITEM_PRICE = 'Item Price Credit'
#KEY HEADER

AMOUNT = 'Amount'
ORDER_NO = 'Order No.'
ORDER_STATUS = 'Order Item Status'

PAYMENT_FEE =  'Payment Fee'
SHIPPING_FEE_PAID_BY_CUSTOMER =  'Shipping Fee (Paid By Customer)'
ITEM_PRICE_CREDIT =  'Item Price Credit'
PROMOTIONAL_CHARGES_VOUCHERS =  'Promotional Charges Vouchers'
SHIPPING_FEE_VOUCHER_BY_LAZADA =  'Shipping Fee Voucher (by Lazada)'
SHIPPING_FEE_PAID_BY_SELLER =  'Shipping Fee Paid by Seller'
PROMOTIONAL_CHARGES_FLEXICOMBO =  'Promotional Charges Flexi-Combo'
MARKETING_SOLUTION_SOCIAL_MEDIA_ADVERTISING =  'Marketing solution /social media advertising'
REVERSAL_ITEM_PRICE =  'Reversal Item Price'
REVERSAL_SHIPPING_FEE_PAID_BY_CUSTOMER =  'Reversal shipping Fee (Paid by Customer)'
REVERSAL_PROMOTIONAL_CHARGES_FLEXICOMBO =  'Reversal Promotional Charges Flexi-Combo'
REVERSAL_SHIPPING_FEE_VOUCHER_BY_LAZADA =  'Reversal Shipping Fee Voucher (by Lazada)'
REVERSAL_PROMOTIONAL_CHARGES_VOUCHERS =  'Reversal Promotional Charges Vouchers'
LAZADA_BONUS =  'Lazada Bonus'
LAZADA_BONUS_LZD_COFUND =  'Lazada Bonus - LZD co-fund'
SPONSORED_DISCOVERY_TOP_UP =  'Sponsored Discovery - Top up'

_str_to_field = {
    PAYMENT_FEE: 'payment_fee',
    SHIPPING_FEE_PAID_BY_CUSTOMER: 'shipping_fee_paid_by_customer',
    ITEM_PRICE_CREDIT: 'item_price_credit',
    PROMOTIONAL_CHARGES_VOUCHERS: 'promotional_charges_vouchers',
    SHIPPING_FEE_VOUCHER_BY_LAZADA: 'shipping_fee_voucher_by_lazada',
    SHIPPING_FEE_PAID_BY_SELLER: 'shipping_fee_paid_by_seller',
    PROMOTIONAL_CHARGES_FLEXICOMBO: 'promotional_charges_flexi_combo',
    MARKETING_SOLUTION_SOCIAL_MEDIA_ADVERTISING: 'marketing_solution_social_media_adv',
    REVERSAL_ITEM_PRICE: 'reversal_item_price',
    REVERSAL_SHIPPING_FEE_PAID_BY_CUSTOMER: 'reversal_shipping_fee_by_customer',
    REVERSAL_PROMOTIONAL_CHARGES_FLEXICOMBO: 'reversal_promotional_charges_flexi_combo',
    REVERSAL_SHIPPING_FEE_VOUCHER_BY_LAZADA: 'reversal_shipping_fee_voucher_lazada',
    REVERSAL_PROMOTIONAL_CHARGES_VOUCHERS: 'reversal_promotional_charges_vouchers',
    LAZADA_BONUS: 'lazada_bouns',
    LAZADA_BONUS_LZD_COFUND: 'lazada_bouns_lzd_co_fund',
    SPONSORED_DISCOVERY_TOP_UP: 'sponsored_discoverty_top_up',
}


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
            result = pd.read_csv(directory,sep=',',encoding='utf8')
            
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
            result = pd.read_csv(directory,sep=',',encoding='utf8')
            create_data = {}
            for index, row in result.iterrows():
                order_no = row[ORDER_NO].strip()
                order_dict = create_data.get(order_no,False)
                if not order_dict:
                    order_dict = {}
                item_no = row[ODER_ITEM_NO].strip()
                item_dict = order_dict.get(item_no,False)
                if not item_dict:
                    item_dict = {
                        PAYMENT_FEE: 0.0,
                        SHIPPING_FEE_PAID_BY_CUSTOMER: 0.0,
                        ITEM_PRICE_CREDIT: 0.0,
                        PROMOTIONAL_CHARGES_VOUCHERS: 0.0,
                        SHIPPING_FEE_VOUCHER_BY_LAZADA: 0.0,
                        SHIPPING_FEE_PAID_BY_SELLER: 0.0,
                        PROMOTIONAL_CHARGES_FLEXICOMBO: 0.0,
                        MARKETING_SOLUTION_SOCIAL_MEDIA_ADVERTISING: 0.0,
                        REVERSAL_ITEM_PRICE: 0.0,
                        REVERSAL_SHIPPING_FEE_PAID_BY_CUSTOMER: 0.0,
                        REVERSAL_PROMOTIONAL_CHARGES_FLEXICOMBO: 0.0,
                        REVERSAL_SHIPPING_FEE_VOUCHER_BY_LAZADA: 0.0,
                        REVERSAL_PROMOTIONAL_CHARGES_VOUCHERS: 0.0,
                        LAZADA_BONUS: 0.0,
                        LAZADA_BONUS_LZD_COFUND: 0.0,
                        SPONSORED_DISCOVERY_TOP_UP: 0.0,
                    }
                fee_name = row[FEE_NAME].strip()
                _amount = item_dict.get(fee_name,0.0)
                item_dict.update({
                    fee_name: _amount + row[AMOUNT]
                })
                item_no.update({item_no: item_dict})
                create_data.update({order_no: order_dict})
                if fee_name != ITEM_PRICE:
                    continue
                order_id = int(row[ODER_ITEM_NO])
                rec = rec_ids.filtered(lambda r: r.order_item_id == str(order_id))
                if rec.id:
                    rec.update({
                        'transaction_date': pd.to_datetime(row[TRANSACTION_DATE]).date(),
                        'state': 'done'
                    })
            self._create_lzd_sum(data=create_data)
    
    def _create_lzd_sum(self,data=None):
        if data is None:
            return True
        for order_no,item_no in data.items():
            for k,v in item_no.items():
                _vals = {**{'order_number': order_no},**{'order_item_id': k},**v}
                _res = self.env['lazada.sum.amount.report'].create(_vals)
        return True

    @api.model
    def _reconcile_shopee_data(self, rec_ids, sale_director_file, _sale_done_director):
        for entry in sale_director_file:
            directory = "{}/{}".format(_sale_done_director,entry)
            match = re.search(REGEX,entry)
            if match:
                extension = match.group(1)
            if extension == "csv":
                result = pd.read_csv(directory,sep=',',encoding='utf8')
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