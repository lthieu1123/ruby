# -*- coding: utf-8 -*-

# Import libs
import os
import pandas as pd
import datetime
import base64
import io
import logging

from odoo import api, models, fields, exceptions
from odoo.tools.translate import _
from odoo.addons import decimal_precision as dp
from ..commons.ruby_constant import *


_li_key = ['Mã đơn hàng','Forder ID','Ngày đặt hàng','Tình trạng đơn hàng','Nhận xét từ Người mua',\
            'Mã vận đơn','Lựa chọn vận chuyển','Phương thức giao hàng','Loại đơn hàng','Ngày giao hàng dự kiến',\
            'Ngày gửi hàng','Thời gian giao hàng','Tình trạng Trả hàng / Hoàn tiền','SKU sản phẩm','Tên sản phẩm',\
            'Cân nặng sản phẩm','Tổng cân nặng','Cân nặng sản phẩm.1','SKU phân loại hàng','Tên phân loại hàng','Giá gốc',\
            'Người bán tự giảm','Được Shopee trợ giá','Được người bán trợ giá','Giá ưu đãi','Số lượng','Product Subtotal',\
            'Tiền đơn hàng (VND)','Mã giảm giá của Shop','Hoàn Xu','Shopee Voucher','Chỉ tiêu combo khuyến mãi','Giảm giá từ combo Shopee',\
            'Giảm giá từ Combo của Shop','Shopee Xu được hoàn','Số tiền được giảm khi thanh toán bằng thẻ Ghi nợ','Phí vận chuyển (dự kiến)',\
            'Phí vận chuyển mà người mua trả','Tổng số tiền','Thời gian hoàn thành đơn hàng','Thời gian đơn hàng được thanh toán',\
            'Phương thức thanh toán','Phí cố định','Phí Dịch Vụ','Phí giao dịch','Tiền ký quỹ','Username (Buyer)','Tên Người nhận',\
            'Số điện thoại','Tỉnh/Thành phố','TP / Quận / Huyện','District','Địa chỉ nhận hàng','Quốc gia','Ghi chú',]

class ShopeeManagment(models.Model):
    _name = "shopee.management"
    _description = "Shopee Management"
    _rec_name = "ma_van_don"

    ma_don_hang = fields.Char('Mã đơn hàng', index=True)
    forder_id = fields.Char('Forder ID')
    ngay_dat_hang = fields.Datetime('Ngày đặt hàng')
    tinh_trang_don_hang = fields.Text('Tình trạng đơn hàng')
    nhan_xet_tu_nguoi_mua = fields.Text('Nhận xét từ Người mua')
    ma_van_don = fields.Char('Mã vận đơn', index=True)
    lua_chon_van_chuyen = fields.Char('Lựa chọn vận chuyển')
    phuong_thuc_giao_hang = fields.Char('Phương thức giao hàng')
    loai_don_hang = fields.Char('Loại đơn hàng')
    ngay_giao_hang_du_kien = fields.Datetime('Ngày giao hàng dự kiến')
    ngay_gui_hang = fields.Datetime('Ngày gửi hàng')
    thoi_gian_giao_hang = fields.Datetime('Thời gian giao hàng')
    tinh_trang_tra_hang_hoan_tien = fields.Char('Tình trạng Trả hàng / Hoàn tiền')
    sku_san_pham = fields.Char('SKU sản phẩm')
    ten_san_pham = fields.Char('Tên sản phẩm')
    can_nang_san_pham_1 = fields.Float('Cân nặng sản phẩm')
    tong_can_nang = fields.Float('Tổng cân nặng')
    can_nang_san_pham_2 = fields.Float('Cân nặng sản phẩm')
    sku_phan_loai_hang = fields.Char('SKU phân loại hàng')
    ten_phan_loai_hang = fields.Char('Tên phân loại hàng')
    gia_goc = fields.Float('Giá gốc')
    nguoi_ban_tu_giam = fields.Float('Người bán tự giảm')
    duoc_shopee_tro_gia = fields.Float('Được Shopee trợ giá')
    duoc_nguoi_ban_tro_gia = fields.Float('Được người bán trợ giá')
    gia_uu_dai = fields.Float('Giá ưu đãi')
    so_luong = fields.Integer('Số lượng')
    product_subtotal = fields.Float('Product Subtotal')
    tien_don_hang = fields.Float('Tiền đơn hàng (VND)')
    ma_giam_gia_cua_shop = fields.Float('Mã giảm giá của Shop')
    hoan_xu = fields.Float('Hoàn Xu')
    shopee_voucher = fields.Float('Shopee Voucher')
    chi_tieu_combo_khuyen_mai = fields.Char('Chỉ tiêu combo khuyến mãi')
    giam_gia_tu_combo_shopee = fields.Float('Giảm giá từ combo Shopee')
    giam_gia_tu_combo_cua_shop = fields.Float('Giảm giá từ Combo của Shop')
    shopee_xu_duoc_hoan = fields.Float('Shopee Xu được hoàn')
    so_tien_duoc_giam_khi_thanh_bang_the_ghi_no = fields.Float('Số tiền được giảm khi thanh toán bằng thẻ Ghi nợ')
    phi_van_chuyen = fields.Float('Phí vận chuyển (dự kiến)')
    phi_van_chuyen_ma_nguoi_mua_tra = fields.Float('Phí vận chuyển mà người mua trả')
    tong_so_tien = fields.Float('Tổng số tiền')
    thoi_gian_hoan_thang_don_hang = fields.Datetime('Thời gian hoàn thành đơn hàng')
    thoi_gian_don_hang_duoc_thanh_toan = fields.Datetime('Thời gian đơn hàng được thanh toán')
    phuong_thuc_thanh_toan = fields.Char('Phương thức thanh toán')
    phi_co_dinh = fields.Float('Phí cố định')
    phi_dich_vu = fields.Float('Phí Dịch Vụ')
    phi_giao_dich = fields.Float('Phí giao dịch')
    tien_ky_quy = fields.Float('Tiền ký quỹ')
    username = fields.Char('Username (Buyer)')
    ten_nguoi_nhan = fields.Char('Tên Người nhận')
    so_dien_thoai = fields.Char('Số điện thoại')
    tinh_thanh_pho = fields.Char('Tỉnh/Thành phố')
    tp_quan_huyen = fields.Char('TP / Quận / Huyện')
    district = fields.Char('District')
    dia_chi_nhan_hang = fields.Text('Địa chỉ nhận hàng')
    quoc_gia = fields.Char('Quốc gia')
    ghi_chu = fields.Text('Ghi chú')

    state = fields.Selection(selection=[
                                ('pending','Pending'),
                                ('delivered','Delivered'),
                                ('returned','Returned'),
                                ('done','Done')
                            ],string='Trạng Thái Đơn Hàng',default='pending',index=True)
    shop_id = fields.Many2one('sale.order.management.shopee.shop','Shop Name',)
    transaction_date = fields.Date('Transaction Date',index=True)
    package_number = fields.Char('Package Number')
    new_update_time = fields.Float('New Update',index=True,)
    deliver_date = fields.Date('Ngày Giao Hàng',index=True)
    return_date = fields.Date('Ngày Trả Hàng',index=True)
    
    @api.model
    def create(self,vals):
        res = super().create(vals)
        #update external id
        _datetime = datetime.datetime.now()
        model_name = self._name
        self.env['ir.model.data'].sudo().create({
            'noupdate': True,
            'name': '{}_{}'.format(model_name,res.id),
            'date_init': _datetime,
            'date_update': _datetime,
            'module': 'ruby',
            'model': model_name,
            'res_id': res.id
        })
    
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
    def btn_process_excel(self):
        self._cr.execute('SAVEPOINT import')
        # _import_directory = 'c:/shopee/newssg'
        _import_directory = '/mnt/c/shopee/newssg'
        try:
            import_directory_file = os.listdir(_import_directory)
        except Exception as err:
            raise exceptions.ValidationError(_('Không tìm thấy thư mục "{}"').format(_import_directory))
        msg = []
        update_time = round(datetime.datetime.now().timestamp(),2)
        #Checking shop code before run
        view_id = self.env.ref('ruby.ecc_contract_announce_view_form_cal_amount').id
        for entry in import_directory_file:
            shop_code = entry.split('.')[0]
            shop_id = self.env['sale.order.management.shopee.shop'].search([
                ('code','=',shop_code)
            ])
            if not len(shop_id):
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
            shop_id = self.env['sale.order.management.shopee.shop'].search([
                ('code','=',shop_code)
            ])
            directory = "{}/{}".format(_import_directory,entry)
            #Reading csv file
            result = pd.read_excel(directory)
            del_count = 0
            create_count = 0
            #browse data from dataframe pandas
            for index, row in result.iterrows():
                #Checking existed item in database, if existed -> unlink
                if str(row['Mã vận đơn']) == 'nan':
                    continue
                existed_item = self.search([
                    ('ma_van_don','=',row['Mã vận đơn']),
                    ('new_update_time','!=',update_time)
                ])
                if len(existed_item):
                    if existed_item[0].state == 'pending':
                        existed_item.unlink()
                        del_count += len(existed_item)
                    else:
                        continue

                #Adding shop_id in vals before add vals from csv
                vals = {
                    'shop_id': shop_id.id,
                    'new_update_time': update_time
                }
                #Get data from csv row and add it to dict
                for key in _li_key:
                    _header = shopee_header.get(key)
                    _data = row[key]
                    vals.update({
                        _header :  _data if str(_data) != 'nan' else None
                    })
                #Create new data
                try:
                    self.create(vals)
                    create_count += 1
                except Exception as err:
                    return {
                        'messages': [{
                            'type': 'Error',
                            'message': [(_('Cannot create data as error: {}').format(str(err)))],
                            'view_id': view_id
                        }]
                    }
            values = {
                'shop': shop_id.name,
                'create':create_count,
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

    def _create_table(self,table_data):
        header_table = ""
        data = ""
        for table in table_data:
            header_table += '<th>{}</th>'.format(table)
            data += '<td>{}</td>'.format(table_data[table])
        table = '<table class="o_list_view table table-sm table-hover table-striped o_list_view_ungrouped"><tr>'+header_table+'</tr><tr>'+data+'</tr></table>'
        return table