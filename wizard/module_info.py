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
import base64
import io
import pandas as pd


class ModuleInfo(models.TransientModel):
    _name = 'rubi.module.info'
    _description = 'Rubi Information'
    _inherit = 'ir.module.module'

    my_module_id = fields.Many2one('ir.module.module','My module',default=lambda self: self._get_module_default())

    def _get_module_default(self):
        return self.env.ref('base.module_ruby').id
    
    @api.onchange('my_module_id')
    def _onchange_my_module_id(self):
        self.shortdesc = self.my_module_id.shortdesc
        self.license = self.my_module_id.license
        self.installed_version = self.my_module_id.installed_version
        self.description_html = self.my_module_id.description_html
        self.icon_image = self.my_module_id.icon_image
        self.author = self.my_module_id.author