# -*- coding: utf-8 -*-

# Import libs
from odoo import api, models, fields
from odoo.tools.translate import _

class RubyReportDelivered(models.Model):
    _name = 'sale.order.management.report'
    _inherit = ['base.report']
    _description = 'Bill and Value supplier report'
    _auto = False

    # Allow override model fields
    row = fields.Date(string='Created Date')
    measure = fields.Float('# of Value', required=True)
    col = fields.Many2one('sale.order.management.shop', string="Shop")
    unit_price = fields.Float('Unit Price', required=True)

    # --------------------------------------- functions -------------------------------------------------

    def _select(self, sql = ''):
        """ SQL to select fields
            @param {SQL} Query
        """
        sql = [
            """
                select row_number() OVER () as id,
                count(*) as measure,
                sm.created_at as row,
                sm.unit_price as unit_price,
                sm.shop_id as col
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
                    sm.created_at,
                    sm.unit_price,
                    sm.shop_id
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