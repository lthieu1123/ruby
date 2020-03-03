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

_logger = logging.getLogger(__name__)

class ShopAnnounce(models.TransientModel):
    _name = 'shop.announce'
    _description = 'Shop announce'

    def _get_default_message(self):
        return self.env.context.get('default_message', False)

    name = fields.Text('name', default=_get_default_message)
    
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

class SetOrderAsb(models.AbstractModel):
    _name = "set.order.abs"
    _description = "Set Order Abstract"

    name = fields.Char('name',default="Delivery Order", readonly=1)
    tracking_code_ids = fields.Char(string='Tracking Code')
    tracking_code_count = fields.Integer('Number of Tracking Code', readonly=True, default=0)
    # tracking_code_show = fields.Many2many(comodel_name='sale.order.management', string='Tracking Code',)
    delta = fields.Integer(string='Delta')
    tracking_code_not_found = fields.Integer('Number of Tracking Code Not Found', readonly=True, default=0)
    note = fields.Text('Notes',)
    json_field = fields.Text('Json data')

    def _create_table(self,table_data):
        header_table = ""
        data = ""
        for table in table_data:
            header_table += '<th>{}</th>'.format(table)
            data += '<td style="font-size: 300%;">{}</td>'.format(table_data[table])
        table = '<table class="o_list_view table table-sm table-hover table-striped o_list_view_ungrouped"><tr>'+header_table+'</tr><tr>'+data+'</tr></table>'
        return table

    @api.model
    def find_order(self,args):
        tracking_id = None
        result = {}
        if self._name == 'set.order.to.delivered':
            tracking_id = self.env['sale.order.management'].search([
                ('tracking_code','=',args.get('order_number')),
                ('state','=','pending')
            ])
            if not len(tracking_id):
                existed = self.env['sale.order.management'].search([
                    ('tracking_code','=',args.get('order_number')),
                    ('state','=','delivered')
                ])
                if len(existed):
                    result.update({'result': 'existed'})
                else:
                    result.update({'result': False})
            else:
                result.update({'result': True})

        if self._name == 'set.order.to.returned':
            tracking_id = self.env['sale.order.management'].search([
                ('tracking_code','=',args.get('order_number')),
                ('state','=','delivered')
            ])
            if not len(tracking_id):
                existed = self.env['sale.order.management'].search([
                    ('tracking_code','=',args.get('order_number')),
                    ('state','=','returned')
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

    tracking_code_show = fields.Many2many(comodel_name='sale.order.management', string='Tracking Code',)

    @api.onchange('tracking_code_ids')
    @api.multi
    def _show_tracking_code(self):
        for rec in self:
            str_json = rec.json_field
            _data = json.loads(str_json) if str_json else {}
            if rec.tracking_code_ids:
                tracking_id = self.env['sale.order.management'].search([
                    ('tracking_code','=',rec.tracking_code_ids),
                    ('state','=','pending')
                ])
                tracking_ids = tracking_id.ids
                tracking_show_ids = rec.tracking_code_show.ids
                _list_show_ids = [i for i in tracking_ids if i not in tracking_show_ids]
                if len(_list_show_ids):
                    sale_object = self.env['sale.order.management'].browse(_list_show_ids)
                    rec.tracking_code_show = rec.tracking_code_show + sale_object
                    order_number = sale_object.mapped(lambda r: r.order_number)
                    delta = list(dict.fromkeys(order_number))
                    rec.delta = len(delta)
                    rec.tracking_code_count = rec.tracking_code_count + len(delta)
                    shop_name = tracking_id[0].shop_id.name
                    new_delta = len(delta)
                    if _data.get(shop_name,False):
                        new_delta = _data.get(shop_name) + new_delta
                    _data.update({
                        shop_name: new_delta
                    })
                    rec.json_field = json.dumps(_data)
                    rec.note = self._create_table(_data)
                else:
                    rec.tracking_code_not_found += 1
            #Remove tracking_code_ids
            rec.tracking_code_ids = False
                

    @api.multi
    def btn_apply(self):
        self.ensure_one()
        res = self.tracking_code_show.write({'state': 'delivered'})
        context = self.env.context.copy()
        if res:
            order_number = self.tracking_code_show.mapped(lambda r: r.order_number)
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

    tracking_code_show = fields.Many2many(comodel_name='sale.order.management', string='Tracking Code',)

    @api.onchange('tracking_code_ids')
    @api.multi
    def _show_tracking_code(self):
        for rec in self:
            str_json = rec.json_field
            _data = json.loads(str_json) if str_json else {}
            if rec.tracking_code_ids:
                tracking_id = self.env['sale.order.management'].search([
                    ('tracking_code','=',rec.tracking_code_ids),
                    ('state','=','delivered')
                ])
                tracking_ids = tracking_id.ids
                tracking_show_ids = rec.tracking_code_show.ids
                _list_show_ids = [i for i in tracking_ids if i not in tracking_show_ids]
                if len(_list_show_ids):
                    sale_object = self.env['sale.order.management'].browse(_list_show_ids)
                    rec.tracking_code_show = rec.tracking_code_show + sale_object
                    order_number = sale_object.mapped(lambda r: r.order_number)
                    delta = list(dict.fromkeys(order_number))
                    rec.delta = len(delta)
                    rec.tracking_code_count = rec.tracking_code_count + len(delta)
                    shop_name = tracking_id[0].shop_id.name
                    new_delta = len(delta)
                    if _data.get(shop_name,False):
                        new_delta = _data.get(shop_name) + new_delta
                    _data.update({
                        shop_name: new_delta
                    })
                    rec.json_field = json.dumps(_data)
                    rec.note = self._create_table(_data)
                else:
                    rec.tracking_code_not_found += 1
            #Remove tracking_code_ids
            rec.tracking_code_ids = False

    @api.multi
    def btn_apply(self):
        self.ensure_one()
        res = self.tracking_code_show.write({'state': 'returned'})
        context = self.env.context.copy()
        if res:
            order_number = self.tracking_code_show.mapped(lambda r: r.order_number)
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