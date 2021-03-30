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
import json
import pandas as pd

_logger = logging.getLogger(__name__)


class LazadaSumAmoutReport(models.Model):
    _name = 'lazada.sum.amount.report.wizard'
    _description = 'Lazada Sum Amount Report Wizard'

    name = fields.Text('name',default='Tổng chi phí hàng hóa')
    date_start = fields.Datetime('Từ ngày')
    date_end = fields.Datetime('Đến ngày')
    file_data = fields.Binary(string='File')
    file_name = fields.Char('File Name')
    csv_file = fields.Binary(string='Báo Cáo Tổng Chi Phí Hàng Hóa')
    csv_name = fields.Char('CSV File Name', default='bao_cao_chi_phi.csv')
    has_csv = fields.Boolean('Has CSV',)
    state = fields.Selection(selection=[('begin','Begin'),('end','End')],string='State', default='begin')


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
        self._calculate_lazada_price_product(rec_ids,sale_director_file,_sale_done_director)
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
    
    def _calculate_lazada_price_product(self, rec_ids, sale_director_file, _sale_done_director):
        create_data = {}
        for entry in sale_director_file:
            directory = "{}/{}".format(_sale_done_director,entry)
            result = pd.read_csv(directory,sep=',',encoding='utf8')
            for index, row in result.iterrows():
                fee_name = row[FEE_NAME].strip()
                if fee_name == MARKETING_SOLUTION_SOCIAL_MEDIA_ADVERTISING:
                    continue
                order_id = int(row[ODER_ITEM_NO])
                rec = rec_ids.filtered(lambda r: r.order_item_id == str(order_id))
                if not rec.id:
                    continue
                order_no = str(int(row[ORDER_NO]))
                order_dict = create_data.get(order_no,False)
                if not order_dict:
                    order_dict = {}
                item_dict = order_dict.get(order_id,False)
                if not item_dict:
                    item_dict = {
                        PAYMENT_FEE = 0.0,
                        SHIPPING_FEE_PAID_BY_CUSTOMER: 0.0,
                        ITEM_PRICE_CREDIT: 0.0,
                        PROMOTIONAL_CHARGES_VOUCHERS: 0.0,
                        SHIPPING_FEE_VOUCHER_BY_LAZADA: 0.0,
                        SHIPPING_FEE_PAID_BY_SELLER: 0.0,
                        PROMOTIONAL_CHARGES_FLEXICOMBO: 0.0,
                        REVERSAL_ITEM_PRICE: 0.0,
                        REVERSAL_SHIPPING_FEE_PAID_BY_CUSTOMER: 0.0,
                        REVERSAL_PROMOTIONAL_CHARGES_FLEXICOMBO: 0.0,
                        REVERSAL_SHIPPING_FEE_VOUCHER_BY_LAZADA: 0.0,
                        REVERSAL_PROMOTIONAL_CHARGES_VOUCHERS: 0.0,
                        LAZADA_BONUS: 0.0,
                        LAZADA_BONUS_LZD_COFUND: 0.0,
                        SPONSORED_DISCOVERY_TOP_UP: 0.0
                    }
                _amount = item_dict.get(fee_name,0.0)
                item_dict.update({
                    fee_name: _amount + row[AMOUNT],
                })
                order_dict.update({order_id: item_dict})
                create_data.update({order_no: order_dict})
        csv_data = self._create_lzd_sum(data=create_data)
        csv_file = self._create_csv_file(csv_data=csv_data)
        vals = {
            'has_csv': False,
        }
        if csv_file:
            vals.update({
                'has_csv': True,
                'state': 'end',
                'csv_file': csv_file
            })
        self.write(vals)
        return {
            'name': 'Báo Cáo Chi Phí Sản Phẩm',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            # 'view_id': False,
            'res_model': self._name,
            'res_id': self.id,
            'views': [(False, 'form')],
            'target': 'new',
        }

    def _create_lzd_sum(self,data=None):
        if data is None:
            return True
        csv_list = []
        for order_no,item_no in data.items():
            for k,v in item_no.items():
                _vals = {**{'order_number': order_no},**{'order_item_id': k},**v}
                csv_list.append(_vals)
        return csv_list
    
    def _create_csv_file(self,csv_data=None):
        if csv_data is None:
            return False
        
        order_no = order_item_no = payment_fee = shipping_fee_paid_by_customer = item_price_credit = promotional_charges_vouchers = shipping_fee_voucher_by_lazada = shipping_fee_paid_by_seller = promotional_charges_flexi_combo = reversal_item_price = reversal_shipping_fee_by_customer = reversal_promotional_charges_flexi_combo = reversal_shipping_fee_voucher_lazada = reversal_promotional_charges_vouchers = lazada_bouns = lazada_bouns_lzd_co_fund = sponsored_discoverty_top_up = []
        for item in csv_data:
            order_no.append(item[order_number])
            order_item_no.append(item[order_item_id])
            payment_fee.append(item[PAYMENT_FEE])
            shipping_fee_paid_by_customer.append(item[SHIPPING_FEE_PAID_BY_CUSTOMER])
            item_price_credit.append(item[ITEM_PRICE_CREDIT])
            promotional_charges_vouchers.append(item[PROMOTIONAL_CHARGES_VOUCHERS])
            shipping_fee_voucher_by_lazada.append(item[SHIPPING_FEE_VOUCHER_BY_LAZADA])
            shipping_fee_paid_by_seller.append(item[SHIPPING_FEE_PAID_BY_SELLER])
            promotional_charges_flexi_combo.append(item[PROMOTIONAL_CHARGES_FLEXICOMBO])
            reversal_item_price.append(item[REVERSAL_ITEM_PRICE])
            reversal_shipping_fee_by_customer.append(item[REVERSAL_SHIPPING_FEE_PAID_BY_CUSTOMER])
            reversal_promotional_charges_flexi_combo.append(item[REVERSAL_PROMOTIONAL_CHARGES_FLEXICOMBO])
            reversal_shipping_fee_voucher_lazada.append(item[REVERSAL_SHIPPING_FEE_VOUCHER_BY_LAZADA])
            reversal_promotional_charges_vouchers.append(item[REVERSAL_PROMOTIONAL_CHARGES_VOUCHERS])
            lazada_bouns.append(item[LAZADA_BONUS])
            lazada_bouns_lzd_co_fund.append(item[LAZADA_BONUS_LZD_COFUND])
            sponsored_discoverty_top_up.append(item[SPONSORED_DISCOVERY_TOP_UP])

        df = dp.DataFrame({
            ORDER_NO: order_no,
            ODER_ITEM_NO: order_item_no,
            PAYMENT_FEE: payment_fee,
            SHIPPING_FEE_PAID_BY_CUSTOMER: shipping_fee_paid_by_customer,
            ITEM_PRICE_CREDIT: item_price_credit,
            PROMOTIONAL_CHARGES_VOUCHERS: promotional_charges_vouchers,
            SHIPPING_FEE_VOUCHER_BY_LAZADA: shipping_fee_voucher_by_lazada,
            SHIPPING_FEE_PAID_BY_SELLER: shipping_fee_paid_by_seller,
            PROMOTIONAL_CHARGES_FLEXICOMBO: promotional_charges_flexi_combo,
            REVERSAL_ITEM_PRICE: reversal_item_price,
            REVERSAL_SHIPPING_FEE_PAID_BY_CUSTOMER: reversal_shipping_fee_by_customer,
            REVERSAL_PROMOTIONAL_CHARGES_FLEXICOMBO: reversal_promotional_charges_flexi_combo,
            REVERSAL_SHIPPING_FEE_VOUCHER_BY_LAZADA: reversal_shipping_fee_voucher_lazada,
            REVERSAL_PROMOTIONAL_CHARGES_VOUCHERS: reversal_promotional_charges_vouchers,
            LAZADA_BONUS: lazada_bouns,
            LAZADA_BONUS_LZD_COFUND: lazada_bouns_lzd_co_fund,
            SPONSORED_DISCOVERY_TOP_UP: sponsored_discoverty_top_up,
        })
        df.to_csv('file_csv_sum.csv',encoding='utf-8')
        _file = open('file_csv_sum.csv','rb')
        _encode = base64.encodestring(_file.read())
        return _encode

