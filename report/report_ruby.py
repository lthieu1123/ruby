# -*- coding: utf-8 -*-

# Import libs
from odoo import api, models, fields
from odoo.tools.translate import _

class EccBillValueSupplierReport(models.Model):
    _name = 'sale.order.management.report'
    _inherit = ['ecc.base.report']
    _description = 'Bill and Value supplier report'
    _auto = False