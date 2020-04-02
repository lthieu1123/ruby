# -*- coding: utf-8 -*-

from odoo import SUPERUSER_ID
from odoo import api, fields, models, exceptions
from odoo.tools.translate import _


import time
import datetime
import logging
import re
import ctypes

_logger = logging.getLogger(__name__)

class ShopAnnounce(models.TransientModel):
    _name = 'set.reconcile.date'
    _description = 'Set Reconcile Date'

    def _get_default_res_model(self):
        return self.env.context.get('default_res_model',False)

    date_start = fields.Date('Từ ngày')
    date_end = fields.Date('Đến ngày')
    res_model = fields.Char('res_model', default=_get_default_res_model)

    @api.multi
    def btn_reconcile(self):
        so_mgt = self.env['sale.order.management']
        start_datetime = datetime.datetime.combine(self.date_start,datetime.time.min)
        end_datetime = datetime.datetime.combine(self.date_end,datetime.time.min)
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
            ('state','=','delivered')
        ])
        return {
            'name': _('Đối Soát Đơn Hàng'),
            'view_type': 'form',
            'view_mode': 'tree',
            'view_id': False,
            'res_model': 'sale.order.management',
            'context': {},
            'domain': [('id','in',rec_ids.ids)],
            'target': 'main',
            'type': 'ir.actions.act_window',
        }

    @api.multi
    def btn_reconcile_shopee(self):
        self.ensure_one()
        so_mgt = self.env['shopee.management']
        start_datetime = datetime.datetime.combine(self.date_start,datetime.time.min)
        end_datetime = datetime.datetime.combine(self.date_end,datetime.time.min)
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
            ('state','=','delivered')
        ])
        return {
            'name': _('Đối Soát Đơn Hàng'),
            'view_type': 'form',
            'view_mode': 'tree',
            'view_id': False,
            'res_model': 'shopee.management',
            'context': {},
            'domain': [('id','in',rec_ids.ids)],
            'target': 'main',
            'type': 'ir.actions.act_window',
        }