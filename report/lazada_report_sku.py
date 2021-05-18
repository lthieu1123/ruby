# -*- coding: utf-8 -*-

# Import libs
from odoo import api, models, fields
from odoo.tools.translate import _
from odoo.addons import decimal_precision as dp

class RubyReportDelivered(models.Model):
    _name = 'sale.order.management.delivered.report'
    _inherit = ['base.report']
    _description = 'Bill and Value supplier report'
    _auto = False

    # Allow override model fields
    row = fields.Date(string='Ngày giao')
    measure = fields.Float('# số lượng', required=True,)
    # unit_price = fields.Float('Giá trung bình', required=True, digits=dp.get_precision('Vietnam Dong Digit'))
    unit_price = fields.Float('Giá trung bình', required=True, group_operator='avg')
    seller_sku = fields.Char('SKU sản phẩm',)


    # --------------------------------------- functions -------------------------------------------------

    def _select(self, sql = ''):
        """ SQL to select fields
            @param {SQL} Query
        """
        sql = [
            """
                select row_number() OVER () as id,
                count(*) as measure,
                (sm.deliver_date at time zone 'utc' at time zone 'Asia/Ho_Chi_Minh')::date as row,
                sm.unit_price as unit_price,
                sm.seller_sku as seller_sku,
                sm.id as _id
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
                    sm.deliver_date,
                    sm.seller_sku,
                    sm.id
            """
        ]
        return super()._select(sql)

    def _from(self, sql = ''):
        """ SQL to group fields
            @param {SQL} Query
        """
        sql = ['from sale_order_management sm']
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

class RubyReportReturned(models.Model):
    _name = 'sale.order.management.returned.report'
    _inherit = ['base.report']
    _description = 'Bill and Value supplier report'
    _auto = False

    # Allow override model fields
    row = fields.Date(string='Ngày trả')
    measure = fields.Float('# số lượng', required=True)
    unit_price = fields.Float('Giá trung bình', required=True, group_operator='avg')
    seller_sku = fields.Char('SKU sản phẩm',)

    # --------------------------------------- functions -------------------------------------------------

    def _select(self, sql = ''):
        """ SQL to select fields
            @param {SQL} Query
        """
        sql = [
            """
                select row_number() OVER () as id,
                count(*) as measure,
                (sm.return_date at time zone 'utc' at time zone 'Asia/Ho_Chi_Minh')::date as row,
                sm.unit_price as unit_price,
                sm.seller_sku as seller_sku,
                sm.id as _id
            """
        ]
        return super()._select(sql)

    def _where(self, sql = ''):
        """ SQL to filter fields
            @param {SQL} Query
        """
        sql = [ 
            """
                where sm.state = 'returned'
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
                    sm.return_date,
                    sm.seller_sku,
                    sm.id
            """
        ]
        return super()._select(sql)

    def _from(self, sql = ''):
        """ SQL to group fields
            @param {SQL} Query
        """
        sql = ['from sale_order_management sm']
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