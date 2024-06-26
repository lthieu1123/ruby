# -*- coding: utf-8 -*-

# Import libs
import os
import pandas as pd
import datetime, pytz
import base64
import io
import logging
import mimetypes
import traceback
import platform
import re

from odoo import api, models, fields, exceptions
from odoo.tools.translate import _
from odoo.addons import decimal_precision as dp
from ..commons.ruby_constant import *

QUERY_STRING = 'select id from sale_order_management order by id desc limit 1'

#FEE NAME
SHIP_FEE_BY_CUS = 'Shipping Fee (Paid By Customer)'
ITEM_PRICE = 'Item Price Credit'
SHIP_FEE_BY_SELLER = 'Shipping Fee Paid by Seller'
SHIP_FEE_VOUCHER_LAZADA = 'Shipping Fee Voucher (by Lazada)'
PROMOTION_CHARGES_VOUCHER = 'Promotional Charges Vouchers'
ADJ_PAYMENT_FEE = 'Adjustments Payment Fee'
PAYMENT_FEE = 'Payment Fee'
SPON_PRODUCT_FEE = 'Sponsored Product Fee'
REVERSAL_SHIP_FEE = 'Reversal shipping Fee (Paid by Customer)'
REVERSAL_ITEM_PRICE = 'Reversal Item Price'
ADJ_SHIP_FEE = 'Adjustments Shipping Fee'
SHIP_FEE_CLAIM = 'Shipping Fee Claims'
SHIP_FEE_SUBSIDY = 'Auto. Shipping fee subsidy (by Lazada)'


#KEY HEADER
ODER_ITEM_NO = 'Order Item No.'
TRANSACTION_DATE = 'Transaction Date'
FEE_NAME = 'Fee Name'
AMOUNT = 'Amount'

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

_logger = logging.getLogger(__name__)

class SaleOrderManagment(models.Model):
    _name = 'sale.order.management'
    _description = 'Sale Order Management'
    _rec_name = 'tracking_code'
    _order = 'updated_at asc'

    order_item_id = fields.Char('Order Item Id',required=True, index=True)
    order_type = fields.Char('Order Type')
    order_flag = fields.Char('Order Flag')
    lazada_id = fields.Char('Lazada Id',index=True)
    seller_sku = fields.Char('Seller SKU',index=True)
    lazada_sku = fields.Char('Lazada SKU',index=True)
    created_at = fields.Datetime('Created at',index=True)
    updated_at = fields.Datetime('Updated at')
    order_number = fields.Char('Order Number', index=True)
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
    tracking_code = fields.Char('Tracking Code',index=True)
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
                                ('pending','Đang chờ'),
                                ('delivered','Đã giao'),
                                ('returned','Hàng trả'),
                                ('done','Đã nhận tiền')
                            ],string='Trạng Thái Đơn Hàng',default='pending',index=True)
    shop_id = fields.Many2one('sale.order.management.shop','Shop Name',)
    transaction_date = fields.Date('Transaction Date',index=True)
    package_number = fields.Char('Package Number')
    new_update_time = fields.Float('New Update',index=True,)
    deliver_date = fields.Datetime('Ngày Giao Hàng',index=True)
    return_date = fields.Datetime('Ngày Trả Hàng',index=True)
    notes = fields.Char('Ghi Chú')
    convert_to_utc = fields.Boolean('converto utc')

    #New fields excel:
    guarantee = fields.Char('guarantee')
    delivery_type = fields.Char('Delivery Type')
    ware_house = fields.Char('Warehouse')
    rts_sla = fields.Char('rtsSla')
    tts_sla = fields.Char('ttsSla')
    invoice_number = fields.Char('Invoice Number')
    reason_user = fields.Char('Reason User')
    

    @api.model
    def create(self,vals):
        res = super().create(vals)
        #update external id
        if self._context.get('is_import', False):
            res['created_at'] = res['created_at'] - datetime.timedelta(hours=DELTA_TIME) if res['created_at'] else False
            res['updated_at'] = res['updated_at'] - datetime.timedelta(hours=DELTA_TIME) if res['updated_at'] else False
            res['convert_to_utc'] = True
        
        #update external id
        # _datetime = datetime.datetime.now()
        # model_name = self._name
        # self.env['ir.model.data'].sudo().create({
        #     'noupdate': True,
        #     'name': '{}_{}'.format(model_name,res.id),
        #     'date_init': _datetime,
        #     'date_update': _datetime,
        #     'module': 'ruby',
        #     'model': model_name,
        #     'res_id': res.id
        # })
    
    @api.multi
    def unlink(self):
        model_name = self._name
        for rec in self:
            externalID = '{}_{}'.format(model_name, rec.id)
            ir_model_data = self.env['ir.model.data'].sudo().search([
                ('name','=',externalID)
            ])
            if len(ir_model_data):
                ir_model_data.unlink()
        return super().unlink()

    @api.multi
    def btn_process_csv(self):
        self._cr.execute('SAVEPOINT import')
        # _import_directory = 'c:/tool/newlazada/newssg'
        # _import_directory = '/mnt/c/tool/newssg'
        _directory = self.env['lazada.directory'].search([
            ('name','=','update')
        ])
        if not _directory.id:
            self._cr.execute('ROLLBACK TO SAVEPOINT import')
            self.pool.reset_changes()
            raise exceptions.ValidationError('Không tìm thấy thư mục đã cài đặt trước. Vui lòng vào "Đường dẫn thư mục" để cài đặt đường dẫn')
        _import_directory = _directory.directory

        try:
            import_directory_file = os.listdir(_import_directory)
        except Exception as err:
            self._cr.execute('ROLLBACK TO SAVEPOINT import')
            traceback.print_exc()
            raise exceptions.ValidationError(_('Không tìm thấy tập tin trong thư mục "{}"').format(_import_directory))
        msg = []
        update_time = round(datetime.datetime.now().timestamp(),2)
        #Checking shop code before run
        view_id = self.env.ref('ruby.ecc_contract_announce_view_form_cal_amount').id
        for entry in import_directory_file:
            if not self._validate_mimetype(entry,csv=True):
                self._cr.execute('ROLLBACK TO SAVEPOINT import')
                self.pool.reset_changes()
                return {
                    'messages': [{
                        'type': 'Error',
                        'message': [(_('"{}" Không đúng định dạng là file CSV').format(entry))],
                        'view_id': view_id
                    }]
                }
            shop_code = entry.split('.')[0]
            if re.search(OPENED_FILED_REGEX, shop_code):
                continue
            shop_id = self.env['sale.order.management.shop'].search([
                ('code','=',shop_code)
            ])
            if not len(shop_id):
                self._cr.execute('ROLLBACK TO SAVEPOINT import')
                self.pool.reset_changes()
                return {
                    'messages': [{
                        'type': 'Error',
                        'message': [(_('Không tìm thấy shop có mã là: "[{}]"').format(shop_code))],
                        'view_id': view_id
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
            try:
                result = pd.read_csv(directory,sep=';',encoding='utf8')
            except:
                result = pd.read_csv(directory,sep=',',encoding='utf8')
            del_count = skip_count = index = 0
            _err = None
            #browse data from dataframe pandas
            del_count, skip_count, index, _err = self._handle_process_data(excel=False,shop_id=shop_id,update_time=update_time,result=result)
            # for index, row in result.iterrows():
            #     #If tracking code is blank, move to next row
            #     if row['Tracking Code'] == 'nan':
            #         continue

            #     #Checking existed item in database, if existed -> unlink
            #     existed_item = self.search([
            #         ('order_item_id','=',row['Order Item Id']),
            #     ])
            #     if existed_item.id:
            #         if existed_item.state == 'pending':
            #             existed_item.unlink()
            #             del_count +=1
            #         else:
            #             skip_count+=1
            #             continue

            #     #Adding shop_id in vals before add vals from csv
            #     vals = {
            #         'shop_id': shop_id.id,
            #         'new_update_time': update_time
            #     }
            #     #Get data from csv row and add it to dict
            #     for key in _li_key:
            #         _header = header.get(key)
            #         _data = row[key]
            #         if key == 'Tracking Code' and str(_data) != 'nan':
            #             _data = str(_data).upper()
            #         vals.update({
            #             _header :  _data if str(_data) != 'nan' else None
            #         })
            #     #Create new data
            #     try:
            #         self.with_context({'is_import': True}).create(vals)
            #     except Exception as err:
            #         return {
            #             'messages': [{
            #                 'type': 'Error',
            #                 'message': [(_('Cannot create data as error: {}').format(str(err)))],
            #                 'view_id': view_id
            #             }]
            #         }
            if _err:
                self._cr.execute('ROLLBACK TO SAVEPOINT import')
                self.pool.reset_changes()
                return _err
            values = {
                'shop': shop_id.name,
                'create':index+1-skip_count,
                'del':del_count
            }
            msg.append(values)
        self._cr.execute('RELEASE SAVEPOINT import')
        #Return mess when done
        return {
            'messages': [{
                'type': 'Completed',
                'message': msg,
                'view_id': view_id
            }]
        }

    @api.model
    def btn_process_sale_done(self):
        # _sale_done_director = 'c:/tool/newlazada/taichinh'
        _directory = self.env['lazada.directory'].search([
            ('name','=','reconcile')
        ])
        _li_shop = []
        if not _directory.id:
            raise exceptions.ValidationError('Không tìm thấy thư mục đã cài đặt trước. Vui lòng vào "Đường dẫn thư mục" để cài đặt đường dẫn')
        _sale_done_director = _directory.directory
        
        try:
            sale_director_file = os.listdir(_sale_done_director)
        except Exception as err:
            traceback.print_exc()
            raise exceptions.ValidationError(_('Không tìm thấy đường dẫn thư mục "{}"').format(_sale_done_director))
        
        if not len(sale_director_file):
            raise exceptions.ValidationError(_('Không tìm thấy tập tin trong đường dẫn thư mục "{}"').format(_sale_done_director))

        #Checking shop code before run
        for entry in sale_director_file:
            shop_code = entry.split('.')[0]
            if re.search(OPENED_FILED_REGEX, shop_code):
                continue
            shop_id = self.env['sale.order.management.shop'].search([
                ('code','=',shop_code)
            ])
            if not len(shop_id):
                raise exceptions.ValidationError(_('Không tìm thấy shop có mã là: "[{}]"').format(shop_code))
            _li_shop.append(shop_id.id)

        #Return wizard to calculate reconcile
        context = self.env.context.copy()
        context['default_res_model'] = 'sale.order.management'
        context['default_shop_id'] = _li_shop
        context['sale_director_file'] = sale_director_file
        context['sale_done_director'] = _sale_done_director
        return {
                'name': 'Đối Soát Đơn Hàng',
                'view_type': 'form',
                'view_mode': 'form',
                'view_id': False,
                'res_model': 'set.reconcile.date',
                'target': 'new',
                'type': 'ir.actions.act_window',
                'context': context
            }

    def _create_table(self,table_data):
        header_table = ""
        data = ""
        for table in table_data:
            header_table += '<th>{}</th>'.format(table)
            data += '<td>{}</td>'.format(table_data[table])
        table = '<table class="o_list_view table table-sm table-hover table-striped o_list_view_ungrouped"><tr>'+header_table+'</tr><tr>'+data+'</tr></table>'
        return table

    @api.model
    def btn_cal_fee(self, file_name, fiel_data):
        self._cr.execute('SAVEPOINT import')
        # _sale_done_director = 'c:/tool/taichinh'
        # sale_director_file = os.listdir(_sale_done_director)
        #Checking shop code before run
        shop_code = file_name.split('.')[0]
        shop_id = self.env['sale.order.management.shop'].search([
            ('code','=',shop_code)
        ])
        if not len(shop_id):
            raise exceptions.ValidationError(_('Không tìm thấy shop có mã là: "[{}]"').format(shop_code))
        
        data_file = base64.b64decode(fiel_data)
        csv_filelike = io.BytesIO(data_file)
        # try:
        #     result = pd.read_csv(csv_filelike,sep=',',encoding='utf8', usecols=['Fee Name','Amount', 'Order No.', 'Order Item Status'], dtype={'Order No.': str,})
        # except:
        #     result = pd.read_csv(csv_filelike,sep=';',encoding='utf8', usecols=['Fee Name','Amount', 'Order No.', 'Order Item Status'], dtype={'Order No.': str,})
        result = pd.read_excel(csv_filelike,dtype={ORDER_NO: str,})
        lazada_formula_ids = self.env['lazada.formula'].search([])
        data = {}
        # data_csv = {}
        for item in lazada_formula_ids:
            data[item.name] = 0.0
                            
        for index, row in result.iterrows():
            if row['Order Item Status'] == 'Pending':
                continue
            fee_name = row[FEE_NAME]
            amount = abs(float(row[AMOUNT]))
            # if fee_name == SHIP_FEE_BY_CUS or fee_name == SHIP_FEE_BY_SELLER:
            #     order_number = row['Order No.']
            #     if data_csv.get(order_number, False):
            #         data_csv[order_number][fee_name] = round(data_csv[order_number][fee_name] + amount,2)
            #     else:
            #         data_csv.update({
            #             order_number: {
            #                 SHIP_FEE_BY_CUS: 0.0,
            #                 SHIP_FEE_BY_SELLER: 0.0,
            #             }
            #         })
            #         data_csv[order_number][fee_name] = amount
            if fee_name in data:
                data[fee_name] = round(data[fee_name] + amount,2)
            else:
                continue
        
        total = 0.0
        for item in lazada_formula_ids:
            if item.operator == 'add':
                total = round(total + data[item.name],2)
            elif item.operator == 'subtract':
                total = round(total - data[item.name],2)

        data.update({
            'Total': total  
        })

        # _li_key = []
        # for order_number in data_csv:
        #     sum_total = data_csv[order_number][SHIP_FEE_BY_CUS] + data_csv[order_number][SHIP_FEE_BY_SELLER]
        #     if sum_total==0:
        #         _li_key.append(order_number)
        # for key in _li_key:
        #     del data_csv[key]

        table = self._create_table(data)
        context = self.env.context.copy()
        context['default_message'] = table
        context['default_cal_fee'] = True
        # res = self.env['shop.announce'].create({
        #     'name': table,
        #     'csv_file': self._create_csv_file(data_csv),
        #     'csv_name': 'phi_van_chuyen.csv',
        #     'has_csv': True if len(data_csv) else False,
        #     'is_cal_fee': True
        # })
        
        return {
            'name': 'Đối Soát Tài Chính',
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': self.env.ref('ruby.ecc_contract_announce_view_form_cal_amount').id,
            'res_model': 'shop.announce',
            # 'res_id': res.id,
            'target': 'new',
            'context': context,
            'type': 'ir.actions.act_window',
        }
        
        
    @api.multi
    def btn_new_update(self):
        self._cr.execute(QUERY_STRING)
        result = self.env.cr.fetchall()
        update_time = False
        if len(result):
            _id = result[0][0]
            obj = self.browse(int(_id))
            update_time = obj.new_update_time

        return {
            'name': 'Cập Nhật Mới',
            'view_type': 'form',
            'view_mode': 'tree,graph,pivot',
            'view_id': False,
            'res_model': self._name,
            'target': 'current',
            'domain': [('new_update_time','=',update_time)],
            'search_view_id': self.env.ref('ruby.sale_order_managment_view_search').id,
            'type': 'ir.actions.act_window',
        }

    @api.model
    def _remove_blank_tracking_code(self):
        return self.search([
            ('tracking_code','=',False)
        ]).unlink()    
    
    @api.multi
    def btn_find_duplicate_records(self):
        query = """ select som.order_item_id
                from sale_order_management som 
                group by som.order_item_id
                having count(*) >1"""
        self._cr.execute(query)
        result = self.env.cr.fetchall()
        order_item_dup = [a[0] for a in result]
        context = self.env.context.copy()
        context['group_by'] = 'order_item_id'
        return {
            'name': 'Sản phẩm trùng',
            'view_type': 'form',
            'view_mode': 'tree',
            'view_id': False,
            'res_model': self._name,
            'target': 'current',
            'domain': [('order_item_id','=',order_item_dup)],
            'context': context,
            'search_view_id': self.env.ref('ruby.sale_order_managment_view_search').id,
            'type': 'ir.actions.act_window',
        }
    
    @api.model
    def _update_time_to_utc(self):
        _logger.info('==============================================')
        _logger.info('UPDATE TIME TO UTC')
        res_ids = self.search([])
        for rec in res_ids:
            rec.write({
                'created_at': rec.created_at - datetime.timedelta(hours=DELTA_TIME),
                'updated_at': rec.updated_at - datetime.timedelta(hours=DELTA_TIME),
                'convert_to_utc': True
            })
        _logger.info('COMPLEDTED UPDATE TIME TO UTC')
        _logger.info('==============================================')
    

    @api.multi
    def btn_process_excel(self):
        self._cr.execute('SAVEPOINT import')
        _directory = self.env['lazada.directory'].search([
            ('name','=','update')
        ])
        if not _directory.id:
            self._cr.execute('ROLLBACK TO SAVEPOINT import')
            self.pool.reset_changes()
            raise exceptions.ValidationError('Không tìm thấy thư mục đã cài đặt trước. Vui lòng vào "Đường dẫn thư mục" để cài đặt đường dẫn')
        _import_directory = _directory.directory
        try:
            import_directory_file = os.listdir(_import_directory)
        except Exception as err:
            self._cr.execute('ROLLBACK TO SAVEPOINT import')
            self.pool.reset_changes()
            traceback.print_exc()
            raise exceptions.ValidationError(_('Không tìm thấy thư mục "{}"').format(_import_directory))
        msg = []
        update_time = round(datetime.datetime.now().timestamp(),2)

        #Checking shop code before run
        view_id = self.env.ref('ruby.ecc_contract_announce_view_form_cal_amount').id
        for entry in import_directory_file:
            if not self._validate_mimetype(entry):
                self._cr.execute('ROLLBACK TO SAVEPOINT import')
                self.pool.reset_changes()
                return {
                    'messages': [{
                        'type': 'Error',
                        'message': [(_('"{}" Không đúng định dạng là file Excel').format(entry))],
                        'view_id': view_id
                    }]
                }
            shop_code = entry.split('.')[0]
            if re.search(OPENED_FILED_REGEX, shop_code):
                continue
            shop_id = self.env['sale.order.management.shop'].search([
                ('code','=',shop_code)
            ])
            if not len(shop_id):
                self._cr.execute('ROLLBACK TO SAVEPOINT import')
                self.pool.reset_changes()
                return {
                    'messages': [{
                        'type': 'Error',
                        'message': [(_('Không tìm thấy shop có mã là: "[{}]"').format(shop_code))],
                        'view_id': view_id
                    }]
                }
        
        for entry in import_directory_file:
            shop_code = entry.split('.')[0]
            shop_id = self.env['sale.order.management.shop'].search([
                ('code','=',shop_code)
            ])
            directory = "{}/{}".format(_import_directory,entry)
            #Reading excel file
            result = pd.read_excel(directory,dtype={'Mã vận đơn': str,'Mã Kiện Hàng': str,'Mã đơn hàng': str})
            del_count = skip_count = index = 0
            _err = None
            del_count, skip_count, index, _err = self._handle_process_data(excel=True,shop_id=shop_id,update_time=update_time,result=result)
            if _err:
                self._cr.execute('ROLLBACK TO SAVEPOINT import')
                self.pool.reset_changes()
                return _err
            values = {
                'shop': shop_id.name,
                'create':index+1-skip_count,
                'del':del_count
            }
            msg.append(values)
        self._cr.execute('RELEASE SAVEPOINT import')
        #Return mess when done
        return {
            'messages': [{
                'type': 'Completed',
                'message': msg,
                'view_id': view_id
            }]
        }
    
    def _validate_mimetype(self,file,csv=False):
        system = platform.system()
        mimetype = mimetypes.guess_type(file)[0]
            
        if csv:
            if system == WINDOWS and mimetype != CSV_MIMETYPE:
                _regex = r"\.csv$"
                _match = re.search(_regex,file)
                return True if _match else False
            return mimetype == CSV_MIMETYPE
        else:
            return mimetype in [EXCEL_XLS_MIMETYPE,EXCEL_XLSX_MIMETYPE]

    def _handle_process_data(self,excel=False,shop_id=None,update_time=None,result=None):
        tracking_code = TRACKING_CODE
        order_item_id = ORDER_ITEM_ID
        _header = LZD_HEADER
        _del_count = 0
        _skip_count = 0
        if excel:
            tracking_code = TRACKING_CODE_EX
            order_item_id = ORDER_ITEM_ID_EX
            _header = LZD_HEADER_EXCEL
        if result is None:
            raise exceptions.ValidationError("Không tìm thấy được dữ liệu")
        for index, row in result.iterrows():
            #If tracking code is blank, move to next row
            if row[tracking_code] == 'nan':
                continue
            
            #Checking existed item in database, if existed -> unlink
            existed_item = self.search([
                ('order_item_id','=',row[order_item_id]),
            ])
            if existed_item.id:
                if existed_item.state == 'pending':
                    existed_item.unlink()
                    _del_count +=1
                else:
                    _skip_count+=1
                    continue

            #Adding shop_id in vals before add vals from csv
            vals = {
                'shop_id': shop_id.id,
                'new_update_time': update_time
            }
            #Get data from csv row and add it to dict
            for k,v in _header.items():
                try:
                    _data = row[k]
                except Exception as err:
                    _logger.warning('Không tìm thấy cột có header là: [{}]'.format(k))
                    _data = None
                if k == tracking_code and str(_data) != 'nan':
                    _data = str(_data).upper()
                vals.update({
                    v :  _data if str(_data) != 'nan' else None
                })
            #Create new data
            try:
                self.with_context({'is_import': True}).create(vals)
            except Exception as err:
                traceback.print_exc()
                return 0, 0, 0, {
                    'messages': [{
                        'type': 'Error',
                        'message': [(_('Cannot create data as error: {}').format(str(err)))],
                        'view_id': self.env.ref('ruby.ecc_contract_announce_view_form_cal_amount').id
                    }]
                }
        return _del_count,_skip_count,index,None
        
