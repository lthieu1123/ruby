# -*- coding: utf-8 -*-
from odoo import SUPERUSER_ID
from odoo import api, fields, models, exceptions
from odoo.tools.translate import _


import time
import datetime
import logging
import re
import ctypes
import json
import base64

_logger = logging.getLogger(__name__)

class SetOrderAsb(models.AbstractModel):
    _name = "set.order.shopee.abs"
    _inherit = ['set.order.abs']
    _description = "Set Order Abstract"

    @api.model
    def find_order(self, args):
        tracking_id = None
        result = {}
        if self._name == 'set.order.to.delivered.shopee':
            tracking_id = self.env['shopee.management'].search([
                ('ma_van_don', '=', args.get('order_number')),
                ('state', '=', 'pending')
            ])
            if not len(tracking_id):
                existed = self.env['shopee.management'].search([
                    ('ma_van_don', '=', args.get('order_number')),
                    ('state', '=', 'delivered')
                ])
                if len(existed):
                    result.update({'result': 'existed'})
                else:
                    result.update({'result': False})
            else:
                result.update({'result': True})

        if self._name == 'set.order.to.returned.shopee':
            tracking_id = self.env['shopee.management'].search([
                ('ma_van_don', '=', args.get('order_number')),
                ('state', '=', 'delivered')
            ])
            if not len(tracking_id):
                existed = self.env['shopee.management'].search([
                    ('ma_van_don', '=', args.get('order_number')),
                    ('state', '=', 'returned')
                ])
                if len(existed):
                    result.update({'result': 'existed'})
                else:
                    result.update({'result': False})
            else:
                result.update({'result': True})
        return result

class SetOrderToDeliveredShopee(models.TransientModel):
    _name = 'set.order.to.delivered.shopee'
    _inherit = ['set.order.shopee.abs']
    _description = 'Set order to delivered shopee'

    tracking_code_show = fields.Many2many(
        comodel_name='shopee.management', string='Tracking Code',)
    existed_tracking_data = fields.Many2many('shopee.management', 'sale_order_to_delivered_shopee_relation',
                                             'sale_order_shopee_management_id', 'set_order_delivered_id', 'Existed Tracking Data')

    @api.onchange('tracking_code_show')
    def _onchange_tracking_code_show(self):
        str_json = self.json_field

        _data = json.loads(str_json) if str_json else {}
        existed_data = self.existed_tracking_data
        current_data = self.tracking_code_show
        if len(existed_data) <= len(current_data):
            self.existed_tracking_data = current_data
        else:
            count = self.tracking_code_count
            _li_diff = list(set(existed_data.ids) - set(current_data.ids))
            ma_van_don = current_data.mapped(lambda r: r.ma_van_don)
            _li_ma_van_don = list(dict.fromkeys(ma_van_don))
            if len(_li_diff):
                recs = self.env['shopee.management'].browse(_li_diff)
                for rec in recs:
                    shop_name = rec.shop_id.name
                    if rec.ma_van_don not in _li_ma_van_don:
                        _data.update({
                            shop_name: _data.get(shop_name) - 1
                        })
                        count -= 1
                self.json_field = json.dumps(_data)
                self.note = self._create_table(_data)
                self.tracking_code_count = count
                self.existed_tracking_data = current_data
        self.existed_tracking_code = self.tracking_code_show.mapped(
            lambda r: r.ma_van_don)

    @api.onchange('input_data')
    def _onchange_input_data(self):
        """This code for user input bunch of the tracking code
        """
        str_json = self.json_field
        code_not_found = self.code_not_found or ""
        code_used = self.code_used or ""
        _data = json.loads(str_json) if str_json else {}
        if self.input_data:
            _li_code_origin = re.split('[;,\s]', self.input_data)
            _li_code = [code.strip() for code in _li_code_origin]
            _li_code = list(dict.fromkeys(_li_code))

            for code in _li_code:
                tracking_ids = self.env['shopee.management'].search([
                    ('ma_van_don', '=', code)
                ])
                if not len(tracking_ids):
                    code_not_found += code+"\r\n"
                else:
                    if tracking_ids[0].state != 'pending':
                        code_used += code+"\r\n"
                    else:
                        tracking_ids_id = tracking_ids.ids
                        tracking_show_ids = self.tracking_code_show.ids
                        _list_show_ids = [
                            i for i in tracking_ids_id if i not in tracking_show_ids]
                        _object = self.env['shopee.management'].browse(
                            _list_show_ids)
                        ma_van_don = _object.mapped(lambda r: r.ma_van_don)
                        delta = list(dict.fromkeys(ma_van_don))
                        self.tracking_code_show = _object + self.tracking_code_show
                        new_delta = len(delta)
                        self.tracking_code_count = self.tracking_code_count + new_delta
                        shop_name = tracking_ids[0].shop_id.name
                        if _data.get(shop_name, False):
                            new_delta = _data.get(shop_name) + new_delta
                        _data.update({
                            shop_name: new_delta
                        })
                        self.json_field = json.dumps(_data)
                        self.note = self._create_table(_data)

        self.code_used = code_used
        self.code_not_found = code_not_found
        self.input_data = False

    @api.onchange('tracking_code_ids')
    @api.multi
    def _show_tracking_code(self):
        for rec in self:
            str_json = rec.json_field
            _data = json.loads(str_json) if str_json else {}
            if rec.tracking_code_ids:
                tracking_id = self.env['shopee.management'].search([
                    ('ma_van_don', '=', rec.tracking_code_ids),
                    ('state', '=', 'pending')
                ])
                tracking_ids = tracking_id.ids
                tracking_show_ids = rec.tracking_code_show.ids
                _list_show_ids = [
                    i for i in tracking_ids if i not in tracking_show_ids]
                if len(_list_show_ids):
                    sale_object = self.env['shopee.management'].browse(
                        _list_show_ids)
                    rec.tracking_code_show = sale_object + rec.tracking_code_show
                    ma_van_don = sale_object.mapped(lambda r: r.ma_van_don)
                    delta = list(dict.fromkeys(ma_van_don))
                    rec.delta = len(delta)
                    rec.tracking_code_count = rec.tracking_code_count + \
                        len(delta)
                    shop_name = tracking_id[0].shop_id.name
                    new_delta = len(delta)
                    if _data.get(shop_name, False):
                        new_delta = _data.get(shop_name) + new_delta
                    _data.update({
                        shop_name: new_delta
                    })
                    rec.json_field = json.dumps(_data)
                    rec.note = rec._create_table(_data)
                else:
                    rec.tracking_code_not_found += 1
            # Remove tracking_code_ids
            rec.tracking_code_ids = False

    @api.multi
    def btn_apply(self):
        self.ensure_one()
        today = datetime.datetime.now()
        res = self.tracking_code_show.write({
            'state': 'delivered',
            'deliver_date': today
        })
        context = self.env.context.copy()
        if res:
            ma_van_don = self.tracking_code_show.mapped(
                lambda r: r.ma_van_don)
            count = len(list(dict.fromkeys(ma_van_don)))
            mess = _('{} orders have been delivered').format(count)
            context['default_message'] = mess
            context['res_model'] = self._name
            act = {
                'name': 'Anounce',
                'view_type': 'form',
                'view_mode': 'form',
                'view_id': False,
                'res_model': 'shop.announce',
                'context': context,
                'target': 'new',
                'type': 'ir.actions.act_window',
            }
            return act


class SetOrderToReturnedShopp(models.TransientModel):
    _name = 'set.order.to.returned.shopee'
    _inherit = ['set.order.shopee.abs']
    _description = 'Set order to returned shopee'

    tracking_code_show = fields.Many2many(
        comodel_name='shopee.management', string='Tracking Code',)
    existed_tracking_data = fields.Many2many('shopee.management', 'sale_order_to_returned_shopee_relation',
                                             'sale_order_shopee_management_id', 'set_order_returned_id', 'Existed Tracking Data')

    @api.onchange('tracking_code_show')
    def _onchange_tracking_code_show(self):
        str_json = self.json_field

        _data = json.loads(str_json) if str_json else {}
        existed_data = self.existed_tracking_data
        current_data = self.tracking_code_show
        if len(existed_data) <= len(current_data):
            self.existed_tracking_data = current_data
        else:
            count = self.tracking_code_count
            _li_diff = list(set(existed_data.ids) - set(current_data.ids))
            ma_van_don = current_data.mapped(lambda r: r.ma_van_don)
            _li_ma_van_don = list(dict.fromkeys(ma_van_don))
            if len(_li_diff):
                recs = self.env['shopee.management'].browse(_li_diff)
                for rec in recs:
                    shop_name = rec.shop_id.name
                    if rec.ma_van_don not in _li_ma_van_don:
                        _data.update({
                            shop_name: _data.get(shop_name) - 1
                        })
                        count -= 1
                self.json_field = json.dumps(_data)
                self.note = self._create_table(_data)
                self.tracking_code_count = count
                self.existed_tracking_data = current_data
        self.existed_tracking_code = self.tracking_code_show.mapped(
            lambda r: r.ma_van_don)

    @api.onchange('input_data')
    def _onchange_input_data(self):
        """This code for user input bunch of the tracking code
        """
        str_json = self.json_field
        code_not_found = self.code_not_found or ""
        code_used = self.code_used or ""
        _data = json.loads(str_json) if str_json else {}
        if self.input_data:
            _li_code_origin = re.split('[;,\s]', self.input_data)
            _li_code = [code.strip() for code in _li_code_origin]
            _li_code = list(dict.fromkeys(_li_code))

            for code in _li_code:
                tracking_ids = self.env['shopee.management'].search([
                    ('ma_van_don', '=', code)
                ])
                if not len(tracking_ids):
                    code_not_found += code+"\r\n"
                else:
                    if tracking_ids[0].state != 'pending':
                        code_used += code+"\r\n"
                    else:
                        tracking_ids_id = tracking_ids.ids
                        tracking_show_ids = self.tracking_code_show.ids
                        _list_show_ids = [
                            i for i in tracking_ids_id if i not in tracking_show_ids]
                        _object = self.env['shopee.management'].browse(
                            _list_show_ids)
                        ma_van_don = _object.mapped(lambda r: r.ma_van_don)
                        delta = list(dict.fromkeys(ma_van_don))
                        self.tracking_code_show = _object + self.tracking_code_show
                        new_delta = len(delta)
                        self.tracking_code_count = self.tracking_code_count + new_delta
                        shop_name = tracking_ids[0].shop_id.name
                        if _data.get(shop_name, False):
                            new_delta = _data.get(shop_name) + new_delta
                        _data.update({
                            shop_name: new_delta
                        })
                        self.json_field = json.dumps(_data)
                        self.note = self._create_table(_data)

        self.code_used = code_used
        self.code_not_found = code_not_found
        self.input_data = False

    @api.onchange('tracking_code_ids')
    @api.multi
    def _show_tracking_code(self):
        for rec in self:
            str_json = rec.json_field
            _data = json.loads(str_json) if str_json else {}
            if rec.tracking_code_ids:
                tracking_id = self.env['shopee.management'].search([
                    ('ma_van_don', '=', rec.tracking_code_ids),
                    ('state', '=', 'delivered')
                ])
                tracking_ids = tracking_id.ids
                tracking_show_ids = rec.tracking_code_show.ids
                _list_show_ids = [
                    i for i in tracking_ids if i not in tracking_show_ids]
                if len(_list_show_ids):
                    sale_object = self.env['shopee.management'].browse(
                        _list_show_ids)
                    rec.tracking_code_show = sale_object + rec.tracking_code_show
                    ma_van_don = sale_object.mapped(lambda r: r.ma_van_don)
                    delta = list(dict.fromkeys(ma_van_don))
                    rec.delta = len(delta)
                    rec.tracking_code_count = rec.tracking_code_count + \
                        len(delta)
                    shop_name = tracking_id[0].shop_id.name
                    new_delta = len(delta)
                    if _data.get(shop_name, False):
                        new_delta = _data.get(shop_name) + new_delta
                    _data.update({
                        shop_name: new_delta
                    })
                    rec.json_field = json.dumps(_data)
                    rec.note = rec._create_table(_data)
                else:
                    rec.tracking_code_not_found += 1
            # Remove tracking_code_ids
            rec.tracking_code_ids = False

    @api.multi
    def btn_apply(self):
        self.ensure_one()
        today = datetime.datetime.now()
        res = self.tracking_code_show.write({
            'state': 'returned',
            'return_date': today
        })
        context = self.env.context.copy()
        if res:
            ma_van_don = self.tracking_code_show.mapped(
                lambda r: r.ma_van_don)
            count = len(list(dict.fromkeys(ma_van_don)))
            mess = _('{} orders have been returned').format(count)
            context['default_message'] = mess
            context['res_model'] = self._name
            act = {
                'name': 'Anounce',
                'view_type': 'form',
                'view_mode': 'form',
                'view_id': False,
                'res_model': 'shop.announce',
                'context': context,
                'target': 'new',
                'type': 'ir.actions.act_window',
            }
            return act