# -*- coding: utf-8 -*-

# Import libs
from odoo import api, models, fields
from odoo.tools.translate import _

class EccBillValueSupplierReport(models.Model):
    _name = 'sale.order.management.report'
    _inherit = ['ecc.base.report']
    _description = 'Bill and Value supplier report'
    _auto = False

    ecc_row = fields.Date('Created Date')
    ecc_col = fields.Many2one('sale.order.management.shop', 'Shop', required=True)
    ecc_measure = fields.Integer('# of Lines',readonly=True)
    ecc_value = fields.Float('Value',readonly=True)

    # --------------------------------------- functions -------------------------------------------------

    def _select(self, sql = ''):
        """ SQL to select fields
            @param {SQL} Query
        """
        sql = [
            """
                select 
                row_number() OVER () as id,
                count(*) as ecc_measure,
                sm.order_item_id as order_item,
                sm.created_at as create_date,
                sm.shop_id as shop,
                sm.unit_price as unit_price
            """
        ]

        return super()._select(sql)

    def _group_by(self, sql = ''):
        """ SQL to group fields
            @param {SQL} Query
        """
        sql = [
            """
                group by cs.id, t.x, t.y
            """
        ]
        return super()._select(sql)

    def _from(self, sql = ''):
        """ SQL to group fields
            @param {SQL} Query
        """
        from_sql = 'from ecc_contract_supplier cs'
        sql = [from_sql]
        return super()._select(sql)

    def _join(self, sql = ''):
        """ SQL to group fields
            @param {SQL} Query
        """
        sql = [
            """
                left join project_project p on p.id = cs.ecc_project_id
                left join account_invoice inv on inv.partner_id = cs.ecc_partner and inv.type = 'out_invoice'
                left join account_payment pay on pay.partner_id = cs.ecc_partner and pay.payment_type = 'outbound'
                cross join lateral (values('Contract Value',cs.ecc_amount_total),('Invoice Value',inv.amount_total_signed),('Payment Value',pay.amount)) as t(x,y)
                where p.active=true
            """
        ]

        return super()._join(sql)

    @api.model_cr
    def init(self):
        self.execute_query_to_create_view()