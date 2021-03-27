# -*- coding: utf-8 -*-

from enum import Enum
from odoo import SUPERUSER_ID
from odoo import api, fields, models, exceptions
from odoo.addons import decimal_precision as dp
from odoo.tools.translate import _

import time
import datetime
import logging
import re
import ctypes
import json

_logger = logging.getLogger(__name__)

_li_existed_fields = ['order_item_id', 'order_number', 'payment_fee', 'shipping_fee_paid_by_customer', 'item_price_credit', 'promotional_charges_vouchers', 'shipping_fee_voucher_by_lazada', 'shipping_fee_paid_by_seller', 'promotional_charges_flexi_combo', 'marketing_solution_social_media_adv',
                      'reversal_item_price', 'reversal_shipping_fee_by_customer', 'reversal_promotional_charges_flexi_combo', 'reversal_shipping_fee_voucher_lazada', 'reversal_promotional_charges_vouchers', 'lazada_bouns', 'lazada_bouns_lzd_co_fund', 'sponsored_discoverty_top_up']

class LazadaSumAmoutReport(models.Model):
    _name = 'lazada.sum.amount.report'
    _description = 'Lazada Sum Amount Report'
    _rec_name = 'order_item_id'

    order_item_id = fields.Char('Order Item Id', required=True, index=True)
    order_number = fields.Char('Order Number', index=True)
    created_at = fields.Datetime('Created at', index=True)
    payment_fee = fields.Float(
        string='Payment Fee', digits=dp.get_precision('Product Price'), default=0.0)
    shipping_fee_paid_by_customer = fields.Float(
        string='Shipping Fee (Paid By Customer)', digits=dp.get_precision('Product Price'), default=0.0)
    item_price_credit = fields.Float(
        string='Item Price Credit', digits=dp.get_precision('Product Price'), default=0.0)
    promotional_charges_vouchers = fields.Float(
        string='Promotional Charges Vouchers', digits=dp.get_precision('Product Price'), default=0.0)
    shipping_fee_voucher_by_lazada = fields.Float(
        string='Shipping Fee Voucher (by Lazada)', digits=dp.get_precision('Product Price'), default=0.0)
    shipping_fee_paid_by_seller = fields.Float(
        string='Shipping Fee Paid by Seller', digits=dp.get_precision('Product Price'), default=0.0)
    promotional_charges_flexi_combo = fields.Float(
        string='Promotional Charges Flexi-Combo', digits=dp.get_precision('Product Price'), default=0.0)
    marketing_solution_social_media_adv = fields.Float(
        string='Marketing solution /social media advertising', digits=dp.get_precision('Product Price'), default=0.0)
    reversal_item_price = fields.Float(
        string='Reversal Item Price', digits=dp.get_precision('Product Price'), default=0.0)
    reversal_shipping_fee_by_customer = fields.Float(
        string='Reversal shipping Fee (Paid by Customer)', digits=dp.get_precision('Product Price'), default=0.0)
    reversal_promotional_charges_flexi_combo = fields.Float(
        string='Reversal Promotional Charges Flexi-Combo', digits=dp.get_precision('Product Price'), default=0.0)
    reversal_shipping_fee_voucher_lazada = fields.Float(
        string='Reversal Shipping Fee Voucher (by Lazada)', digits=dp.get_precision('Product Price'), default=0.0)
    reversal_promotional_charges_vouchers = fields.Float(
        string='Reversal Promotional Charges Vouchers', digits=dp.get_precision('Product Price'), default=0.0)
    lazada_bouns = fields.Float(
        string='Lazada Bonus', digits=dp.get_precision('Product Price'), default=0.0)
    lazada_bouns_lzd_co_fund = fields.Float(
        string='Lazada Bonus - LZD co-fund', digits=dp.get_precision('Product Price'), default=0.0)
    sponsored_discoverty_top_up = fields.Float(
        string='Sponsored Discovery - Top up', digits=dp.get_precision('Product Price'), default=0.0)

    @api.model
    def find_and_add_new_field(self,field_name = None):
        if field_name is None:
            raise exceptions.ValidationError('Không tìm thấy tên của fields.')
        _name = 'x_'+re.sub(r'\W+','',field_name).lower()
        res_model_id = self.env['ir.model'].search('model','=',self._name)
        _field_id = self.env['ir.model.fields'].search([
            ('name','=',_name),
            ('model_id','=',res_model_id.id)
        ])
        if not _field_id.id:
            _field_id = _field_id.create({'name': _name, 'field_description': field_name,
                              'ttype': 'float', 'store': True, 'copied': True, 'state': 'manual', 'model_id': res_model_id.id})
            self.update_field(name=_name,description=field_name)
        return True
    
    @api.model
    def create(self,vals):
        res = super().create(vals)
        item_id = self.env['sale.order.management'].search([
            ('order_item_id','=',res.order_item_id),
            ('order_number','=',res.order_number)
        ])
        if item_id.id:
            res['created_at'] = item_id.created_at
        return res
        
    
