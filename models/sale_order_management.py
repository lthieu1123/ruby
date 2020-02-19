# -*- coding: utf-8 -*-

# Import libs
import os
import pandas as pd

from odoo import api, models, fields, exceptions
from odoo.tools.translate import _
from ..commons.ruby_constant import *

_li_key = ['Order Item Id','Order Type','Order Flag','Lazada Id','Seller SKU',\
            'Lazada SKU','Created at','Updated at','Order Number','Invoice Required',\
                'Customer Name','Customer Email','National Registration Number','Shipping Name',\
                'Shipping Address','Shipping Address2','Shipping Address3','Shipping Address4',\
                'Shipping Address5','Shipping Phone Number','Shipping Phone Number2',\
                'Shipping City','Shipping Postcode','Shipping Country','Shipping Region',\
                'Billing Name','Billing Address','Billing Address2','Billing Address3',\
                'Billing Address4','Billing Address5','Billing Phone Number','Billing Phone Number2',\
                'Billing City','Billing Postcode','Billing Country','Tax Code','Branch Number','Tax Invoice requested',\
                'Payment Method','Paid Price','Unit Price','Shipping Fee','Wallet Credits','Item Name','Variation',\
                'CD Shipping Provider','Shipping Provider','Shipment Type Name','Shipping Provider Type','CD Tracking Code',\
                'Tracking Code','Tracking URL','Shipping Provider (first mile)','Tracking Code (first mile)',\
                'Tracking URL (first mile)','Promised shipping time','Premium','Status','Cancel / Return Initiator',\
                'Reason','Reason Detail','Editor','Bundle ID','Bundle Discount','Refund Amount']

class SaleOrderManagmentShop(models.Model):
    _name = 'sale.order.management.shop'
    _description = 'Sale Order Management Shop'

    name = fields.Char('Shop name', required=True)
    code = fields.Char('Shop Code', required=True)

    # SQL Contraints
    _sql_constraints = [('unique_tracking', 'unique(code)',
                         _('Code must be unique'))]

class SaleOrderManagment(models.Model):
    _name = 'sale.order.management'
    _description = 'Sale Order Management'
    _rec_name = 'tracking_code'
    _order = 'updated_at asc'

    order_item_id = fields.Char('Order Item Id',required=True)
    order_type = fields.Char('Order Type')
    order_flag = fields.Char('Order Flag')
    lazada_id = fields.Char('Lazada Id')
    seller_sku = fields.Char('Seller SKU')
    lazada_sku = fields.Char('Lazada SKU')
    created_at = fields.Datetime('Created at')
    updated_at = fields.Datetime('Updated at')
    order_number = fields.Char('Order Number')
    invoice_required = fields.Char('Invoice Required')
    customer_name = fields.Char('Customer Name')
    customer_email = fields.Char('Customer Email')
    national_registration_number = fields.Char('National Registration Number')
    shipping_name = fields.Char('Shipping Name')
    shipping_address = fields.Text('Shipping Address')
    shipping_address2 = fields.Text('Shipping Address2')
    shipping_address3 = fields.Text('Shipping Address3')
    shipping_address4 = fields.Text('Shipping Address4')
    shipping_address5 = fields.Text('Shipping Address5')
    shipping_phone_number = fields.Char('Shipping Phone Number')
    shipping_phone_number2 = fields.Char('Shipping Phone Number2')
    shipping_city = fields.Char('Shipping City')
    shipping_postcode = fields.Char('Shipping Postcode')
    shipping_country = fields.Char('Shipping Country')
    shipping_region = fields.Char('Shipping Region')
    billing_name = fields.Char('Billing Name')
    billing_address = fields.Char('Billing Address')
    billing_address2 = fields.Char('Billing Address2')
    billing_address3 = fields.Char('Billing Address3')
    billing_address4 = fields.Char('Billing Address4')
    billing_address5 = fields.Char('Billing Address5')
    billing_phone_number = fields.Char('Billing Phone Number')
    billing_phone_number2 = fields.Char('Billing Phone Number2')
    billing_city = fields.Char('Billing City')
    billing_postcode = fields.Char('Billing Postcode')
    billing_country = fields.Char('Billing Country')
    tax_code = fields.Char('Tax Code')
    branch_number = fields.Char('Branch Number')
    tax_invoice_requested = fields.Boolean('Tax Invoice requested')
    payment_method = fields.Char('Payment Method')
    paid_price = fields.Float('Paid Price')
    unit_price = fields.Float('Unit Price')
    shipping_fee = fields.Float('Shipping Fee')
    wallet_credits = fields.Float('Wallet Credits')
    item_name = fields.Char('Item Name')
    variation = fields.Char('Variation')
    cd_shipping_provider = fields.Char('CD Shipping Provider')
    shipping_provider = fields.Char('Shipping Provider')
    shipment_type_name = fields.Char('Shipment Type Name')
    shipping_provider_type = fields.Char('Shipping Provider Type')
    cd_tracking_code = fields.Char('CD Tracking Code')
    tracking_code = fields.Char('Tracking Code')
    tracking_url = fields.Char('Tracking URL')
    shipping_provider_first_mile = fields.Char('Shipping Provider (first mile)')
    tracking_code_first_mile = fields.Char('Tracking Code (first mile)')
    tracking_url_first_mile = fields.Char('Tracking URL (first mile)')
    promised_shipping_time = fields.Char('Promised shipping time')
    premium = fields.Char('Premium')
    status = fields.Char('Status')
    cancel_return_initiator = fields.Char('Cancel / Return Initiator')
    reason = fields.Char('Reason')
    reason_detail = fields.Char('Reason Detail')
    editor = fields.Char('Editor')
    bundle_id = fields.Char('Bundle ID')
    bundle_discount = fields.Char('Bundle Discount')
    refund_amount = fields.Float('Refund Amount')
    state = fields.Selection(selection=[
                                ('pending','Pending'),
                                ('delivered','Delivered'),
                                ('returned','Returned'),
                                ('done','Done')
                            ],string='State',default='pending')
    shop_id = fields.Many2one('sale.order.management.shop','Shop Name',)

    @api.multi
    def btn_process_csv(self):
        self._cr.execute('SAVEPOINT import')
        _import_directory = '/mnt/d/readcsv/import'
        _accounting_director = '/mnt/d/readcsv/accouting'
        import_directory_file = os.listdir(_import_directory)
        msg = ""
        #Checking shop code before run
        for entry in import_directory_file:
            shop_code = entry.split('.')[0]
            shop_id = self.env['sale.order.management.shop'].search([
                ('code','=',shop_code)
            ])
            if not len(shop_id):
                return {
                    'messages': [{
                        'type': 'Error',
                        'message': (_('Cannot find shop with shop code is: "[{}]"').format(shop_code)),
                    }]
                }
        
        #Adding data from csv to database
        for entry in import_directory_file:
            shop_code = entry.split('.')[0]
            shop_id = self.env['sale.order.management.shop'].search([
                ('code','=',shop_code)
            ])
            directory = "{}/{}".format(_import_directory,entry)
            #Reading csv file
            result = pd.read_csv(directory,sep=';',encoding='utf8')
            del_count = 0
            #browse data from dataframe pandas
            for index, row in result.iterrows():
                #Checking existed item in database, if existed -> unlink
                existed_item = self.search([
                    ('order_item_id','=',row['Order Item Id'])
                ])
                if existed_item.id:
                    existed_item.unlink()
                    del_count +=1
                #Adding shop_id in vals before add vals from csv
                vals = {
                    'shop_id': shop_id.id
                }
                #Get data from csv row and add it to dict
                for key in _li_key:
                    _header = header.get(key)
                    _data = row[key]
                    vals.update({
                        _header :  _data if str(_data) != 'nan' else None
                    })
                #Create new data
                try:
                    self.create(vals)
                except Exception as err:
                    return {
                        'messages': [{
                            'type': 'Error',
                            'message': (_('Cannot create data as error: {}').format(str(err))),
                        }]
                    }
            msg += (_('Shop: {} - Create: {} - Delete: {}\n')).format(shop_id.name,index+1,del_count)
        self._cr.execute('RELEASE SAVEPOINT import')
        #Return mess when done
        return {
            'messages': [{
                'type': 'Completed',
                'message': msg,
            }]
        }
            
                
                

                
                

