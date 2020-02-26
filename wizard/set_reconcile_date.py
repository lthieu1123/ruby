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

    date_start = fields.Date('From')
    date_end = fields.Date('To')

    @api.multi
    def btn_reconcile(self):
        so_mgt = self.env['sale.order.management']
        start_datetime = datetime.datetime.combine(self.date_start,datetime.time.min)
        end_datetime = datetime.datetime.combine(self.date_end,datetime.time.min)
        #Veiry date_start < date_end
        if self.date_start > self.date_end:
            raise exceptions.ValidationError(_('End date must be equal or greate than Start date'))
        #Verify date end data will be import first
        count = so_mgt.search_count([
            ('created_at','>=',end_datetime)
        ])
        if not (count):
            raise exceptions.ValidationError(_('Imported data is not reached to end date {}').format(str(self.date_end)))
        #Find all import data from start date to end date
        rec_ids = so_mgt.search([
            ('created_at','>=',start_datetime),
            ('created_at','<=',end_datetime),
            ('state','=','delivered')
        ])
        return {
            'name': _('Reconcile'),
            'view_type': 'form',
            'view_mode': 'tree',
            'view_id': False,
            'res_model': 'sale.order.management',
            'context': {},
            'domain': [('id','in',rec_ids.ids)],
            'target': 'main',
            'type': 'ir.actions.act_window',
        }