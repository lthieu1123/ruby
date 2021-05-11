# -*- coding: utf-8 -*-

# Import libs
from odoo import api, models, fields
from odoo.tools.translate import _
from odoo.addons import decimal_precision as dp

class LazadaReportOrderNumberDelivered(models.Model):
    _name = 'lazada.report.order.number.delivered'
    _inherit = ['base.report']
    _description = 'Lazada Report Order Number Delivered'
    _auto = False

    # Allow override model fields
    row = fields.Date(string='Ngày giao')
    measure = fields.Float('# số lượng', required=True)
    order_number = fields.Char('Order Number', required=True)
    shop_id = fields.Many2one('sale.order.management.shop','Shop')


    # --------------------------------------- functions -------------------------------------------------

    def _select(self, sql = ''):
        """ SQL to select fields
            @param {SQL} Query
        """
        sql = [
            """
                select
                    row_number() OVER () as id,
                    count (distinct sm.order_number) as measure,
                    sm.order_number as order_number,
                    sm.shop_id as shop_id,
                    sm.deliver_date as row
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
                    sm.shop_id,
                    sm.order_number
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

class LazadaReportOrderNumberReturned(models.Model):
    _name = 'lazada.report.order.number.returned'
    _inherit = ['base.report']
    _description = 'Lazada Report Order Number Returned'
    _auto = False

    # Allow override model fields
    row = fields.Date(string='Ngày trả',search='_search_date')
    measure = fields.Float('# số lượng', required=True)
    order_number = fields.Char('Order Number', required=True)
    shop_id = fields.Many2one('sale.order.management.shop','Shop')


    # --------------------------------------- functions -------------------------------------------------
    @api.multi
    def _search_date(self, operator, value):
        print('operator: ',operator)
        print('value: ',value)

    def _select(self, sql = ''):
        """ SQL to select fields
            @param {SQL} Query
        """
        sql = [
            """
                select
                    row_number() OVER () as id,
                    count(*) as measure,
                    sm.order_number as order_number,
                    sm.shop_id as shop_id,
                    sm.deliver_date as row
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
                    sm.deliver_date,
                    sm.shop_id,
                    sm.order_number
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