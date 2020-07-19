# -*- coding: utf-8 -*-

# Import libs
from odoo import api, models, fields
from odoo.tools.translate import _
from odoo.addons import decimal_precision as dp

class ShopeeAvgPrice(models.Model):
    _name = 'shopee.price.avg.report'
    _inherit = ['base.report']
    _description = 'Báo cáo giá trung bình sản phẩm shopee'
    _auto = False

    # Allow override model fields
    row = fields.Date(string='Ngày giao')
    measure = fields.Float('# số lượng', required=True,)
    # unit_price = fields.Float('Giá trung bình', required=True, digits=dp.get_precision('Vietnam Dong Digit'))
    price_avg = fields.Float('Giá trung bình', required=True, group_operator='avg')
    price_total = fields.Float('Giá Tổng',)
    sku_san_pham = fields.Char('SKU sản phẩm',)
    ten_san_pham = fields.Char('Tên sản phẩm')


    # --------------------------------------- functions -------------------------------------------------

    def _select(self, sql = ''):
        """ SQL to select fields
            @param {SQL} Query
        """
        sql = [
            """
                select
                    min(sm.id) as id,
                    sm.deliver_date as row,
                    sum(sm.so_luong) as measure,
                    sum(sm.gia_goc * sm.so_luong)::decimal(16,2) as price_total,
                    (sum(sm.gia_goc * sm.so_luong)/sum(sm.so_luong))::decimal(16,2) as price_avg,
                    sm.sku_san_pham as sku_san_pham,
                    sm.ten_san_pham as ten_san_pham
            """
        ]
        return super()._select(sql)

    def _where(self, sql = ''):
        """ SQL to filter fields
            @param {SQL} Query
        """
        sql = [ 
            """
                where sm.state = 'delivered'
            """
        ]
        return super()._select(sql)

    def _group_by(self, sql = ''):
        """ SQL to group fields
            @param {SQL} Query
        """
        sql = [
            """
                group by
                    sm.sku_san_pham,
                    sm.deliver_date,
                    sm.so_luong,
                    sm.ten_san_pham,
                    sm.sku_san_pham
            """
        ]
        return super()._select(sql)

    def _from(self, sql = ''):
        """ SQL to group fields
            @param {SQL} Query
        """
        sql = ['from shopee_management sm']
        return super()._select(sql)

    def _join(self, sql = ''):
        """ SQL to group fields
            @param {SQL} Query
        """
        sql = [
            """
            """
        ]
        return super()._join(sql)

    @api.model_cr
    def init(self):
        self.execute_query_to_create_view()