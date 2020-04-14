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
import io
import base64
import pandas as pd

_logger = logging.getLogger(__name__)

SHIP_FEE_BY_CUS = 'Shipping Fee (Paid By Customer)'
SHIP_FEE_BY_SELLER = 'Shipping Fee Paid by Seller'

class ShopAnnounce(models.TransientModel):
    _name = 'shop.announce'
    _description = 'Shop announce'

    def _get_default_message(self):
        return self.env.context.get('default_message', False)

    def _get_default_cal_fee(self):
        return self.env.context.get('default_cal_fee', False)

    def _get_default_has_csv(self):
        return self.env.context.get('has_data_csv', False)

    name = fields.Text('name', default=_get_default_message)
    file_data = fields.Binary(string='File')
    file_name = fields.Char('File Name')
    # csv_file = fields.Binary(string='Chênh lệch phí vận chuyển')
    # csv_name = fields.Char('CSV File Name', default='phi_van_chuyen.csv')
    # has_csv = fields.Boolean('Has CSV', default=_get_default_has_csv)
    is_cal_fee = fields.Boolean('Is Cal Fee', default=_get_default_cal_fee)

    @api.multi
    def btn_accept(self):
        return self.env['sale.order.management'].btn_cal_fee(self.file_name, self.file_data)

    @api.multi
    def btn_ok(self):
        context = self.env.context
        res_model = context.get('res_model')
        return {
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': False,
            'res_model': res_model,
            'context': context,
            'target': 'main',
            'type': 'ir.actions.act_window',
        }

    @api.multi
    def btn_new_update(self):
        context = self.env.context
        default_model = context.get('default_model')
        vals =  self.env[default_model].btn_new_update()
        vals.update({
            'target': 'main',
        })
        return vals

class SetOrderAsb(models.AbstractModel):
    _name = "set.order.abs"
    _description = "Set Order Abstract"

    name = fields.Char('name', default="Delivery Order", readonly=1)
    tracking_code_ids = fields.Char(string='Tracking Code')
    tracking_code_count = fields.Integer(
        'Number of Tracking Code', readonly=True, default=0)
    # tracking_code_show = fields.Many2many(comodel_name='sale.order.management', string='Tracking Code',)
    delta = fields.Integer(string='Delta')
    tracking_code_not_found = fields.Integer(
        'Number of Tracking Code Not Found', readonly=True, default=0)
    note = fields.Text('Notes',)
    json_field = fields.Text('Json data')
    existed_tracking_code = fields.Text('Existed Tracking Code')
    input_type = fields.Selection(string='Kiểu Nhập', selection=[(
        'one', 'Nhập từng đơn'), ('many', 'Nhập nhiều đơn')], default='one')
    input_data = fields.Text(
        'Input codes', placeholder='Các Tracking Code cách nhau bằng dấu phẩy (",") hoặc dấu chấm phẩy (";")')
    code_not_found = fields.Text('Code not found')
    code_used = fields.Text('Code used')

    def _create_table(self, table_data):
        header_table = ""
        data = ""
        for table in table_data:
            header_table += '<th>{}</th>'.format(table)
            data += '<td style="font-size: 300%;">{}</td>'.format(
                table_data[table])
        table = '<table class="o_list_view table table-sm table-hover table-striped o_list_view_ungrouped"><tr>' + \
            header_table+'</tr><tr>'+data+'</tr></table>'
        return table

    @api.model
    def find_order(self, args):
        tracking_id = None
        result = {}
        if self._name == 'set.order.to.delivered':
            tracking_id = self.env['sale.order.management'].search([
                ('tracking_code', '=', args.get('order_number')),
                ('state', '=', 'pending')
            ])
            if not len(tracking_id):
                existed = self.env['sale.order.management'].search([
                    ('tracking_code', '=', args.get('order_number')),
                    ('state', '=', 'delivered')
                ])
                if len(existed):
                    result.update({'result': 'existed'})
                else:
                    result.update({'result': False})
            else:
                result.update({'result': True})

        if self._name == 'set.order.to.returned':
            tracking_id = self.env['sale.order.management'].search([
                ('tracking_code', '=', args.get('order_number')),
                ('state', '=', 'delivered')
            ])
            if not len(tracking_id):
                existed = self.env['sale.order.management'].search([
                    ('tracking_code', '=', args.get('order_number')),
                    ('state', '=', 'returned')
                ])
                if len(existed):
                    result.update({'result': 'existed'})
                else:
                    result.update({'result': False})
            else:
                result.update({'result': True})
        return result


class SetOrderToDelivered(models.TransientModel):
    _name = 'set.order.to.delivered'
    _inherit = ['set.order.abs']
    _description = 'Set Order To Delivered'

    tracking_code_show = fields.Many2many(
        comodel_name='sale.order.management', string='Tracking Code',)
    existed_tracking_data = fields.Many2many('sale.order.management', 'sale_order_to_delivered_relation',
                                             'sale_order_management_id', 'set_order_delivered_id', 'Existed Tracking Data')

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
            order_number = current_data.mapped(lambda r: r.order_number)
            _li_order_number = list(dict.fromkeys(order_number))
            if len(_li_diff):
                recs = self.env['sale.order.management'].browse(_li_diff)
                for rec in recs:
                    shop_name = rec.shop_id.name
                    if rec.order_number not in _li_order_number:
                        _data.update({
                            shop_name: _data.get(shop_name) - 1
                        })
                        count -= 1
                self.json_field = json.dumps(_data)
                self.note = self._create_table(_data)
                self.tracking_code_count = count
                self.existed_tracking_data = current_data
        self.existed_tracking_code = self.tracking_code_show.mapped(
            lambda r: r.tracking_code)

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
                tracking_ids = self.env['sale.order.management'].search([
                    ('tracking_code', '=', code)
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
                        _object = self.env['sale.order.management'].browse(
                            _list_show_ids)
                        order_number = _object.mapped(lambda r: r.order_number)
                        delta = list(dict.fromkeys(order_number))
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
                tracking_id = self.env['sale.order.management'].search([
                    ('tracking_code', '=', rec.tracking_code_ids),
                    ('state', '=', 'pending')
                ])
                tracking_ids = tracking_id.ids
                tracking_show_ids = rec.tracking_code_show.ids
                _list_show_ids = [
                    i for i in tracking_ids if i not in tracking_show_ids]
                if len(_list_show_ids):
                    sale_object = self.env['sale.order.management'].browse(
                        _list_show_ids)
                    rec.tracking_code_show = sale_object + rec.tracking_code_show
                    order_number = sale_object.mapped(lambda r: r.order_number)
                    delta = list(dict.fromkeys(order_number))
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
            order_number = self.tracking_code_show.mapped(
                lambda r: r.order_number)
            count = len(list(dict.fromkeys(order_number)))
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


class SetOrderToReturned(models.TransientModel):
    _name = 'set.order.to.returned'
    _inherit = ['set.order.abs']
    _description = 'Set Order To Returned'

    tracking_code_show = fields.Many2many(
        comodel_name='sale.order.management', string='Tracking Code',)
    existed_tracking_data = fields.Many2many('sale.order.management', 'sale_order_to_returned_relation',
                                             'sale_order_management_id', 'set_order_returned_id', 'Existed Tracking Data')

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
                tracking_ids = self.env['sale.order.management'].search([
                    ('tracking_code', '=', code)
                ])
                if not len(tracking_ids):
                    code_not_found += code+"\r\n"
                else:
                    if tracking_ids[0].state == 'pending' or tracking_ids[0].state == 'done':
                        code_not_found += code+"\r\n"
                    elif tracking_ids[0].state == 'returned':
                        code_used += code+"\r\n"
                    else:
                        tracking_ids_id = tracking_ids.ids
                        tracking_show_ids = self.tracking_code_show.ids
                        _list_show_ids = [
                            i for i in tracking_ids_id if i not in tracking_show_ids]
                        _object = self.env['sale.order.management'].browse(
                            _list_show_ids)
                        order_number = _object.mapped(lambda r: r.order_number)
                        delta = list(dict.fromkeys(order_number))
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
            order_number = current_data.mapped(lambda r: r.order_number)
            _li_order_number = list(dict.fromkeys(order_number))
            if len(_li_diff):
                recs = self.env['sale.order.management'].browse(_li_diff)
                for rec in recs:
                    shop_name = rec.shop_id.name
                    if rec.order_number not in _li_order_number:
                        _data.update({
                            shop_name: _data.get(shop_name) - 1
                        })
                        count -= 1
                self.json_field = json.dumps(_data)
                self.note = self._create_table(_data)
                self.tracking_code_count = count
                self.existed_tracking_data = current_data
        self.existed_tracking_code = self.tracking_code_show.mapped(
            lambda r: r.tracking_code)

    @api.onchange('tracking_code_ids')
    @api.multi
    def _show_tracking_code(self):
        for rec in self:
            str_json = rec.json_field
            _data = json.loads(str_json) if str_json else {}
            if rec.tracking_code_ids:
                tracking_id = self.env['sale.order.management'].search([
                    ('tracking_code', '=', rec.tracking_code_ids),
                    ('state', '=', 'delivered')
                ])
                tracking_ids = tracking_id.ids
                tracking_show_ids = rec.tracking_code_show.ids
                _list_show_ids = [
                    i for i in tracking_ids if i not in tracking_show_ids]
                if len(_list_show_ids):
                    sale_object = self.env['sale.order.management'].browse(
                        _list_show_ids)
                    rec.tracking_code_show = sale_object +  rec.tracking_code_show
                    order_number = sale_object.mapped(lambda r: r.order_number)
                    delta = list(dict.fromkeys(order_number))
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
            order_number = self.tracking_code_show.mapped(
                lambda r: r.order_number)
            count = len(list(dict.fromkeys(order_number)))
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
