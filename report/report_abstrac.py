# -*- coding: utf-8 -*-

# Import libs
from odoo import tools, api, models, fields, exceptions
from odoo.tools.translate import _

# Import global files
SQL_METHOD_INDEX = ['select', 'from', 'join', 'where', 'group']

class BaseReport(models.AbstractModel):
    _name = 'base.report'
    _description = 'Base Report'
    _order = 'row'
    _auto = False

    # Allow override model fields
    # name = fields.Char('Name', required=True)
    row = fields.Char('Row', required=True)
    col = fields.Char('Col')
    measure = fields.Float('Measure', required=True)


    # --------------------------------------- functions -------------------------------------------------

    def _select(self, sql = ''):
        """ SQL to select fields
            @param {SQL} Query
        """
        sql = sql if type(sql) == list else [sql]
        return sql
    
    def _join(self, sql = ''):
        """ SQL to join fields
            @param {SQL} Query
        """
        sql = sql if type(sql) == list else [sql]
        return sql

    def _from(self, sql = ''):
        """ SQL to group fields
            @param {SQL} Query
        """
        sql = sql if type(sql) == list else [sql]
        return sql
    
    def _where(self, sql = ''):
        """ SQL to filter fields
            @param {SQL} Query
        """
        sql = sql if type(sql) == list else [sql]
        return sql

    def _group_by(self, sql = ''):
        """ SQL to group fields
            @param {SQL} Query
        """
        sql = sql if type(sql) == list else [sql]
        return sql

    def _get_view_name(self):
        # Get the view name to save to database
        return self._table

    def _build_query_to_create_view_report(self, options):
        # Build the sql with multiple options
        # Only support union
        if type(options) != list:
            raise exceptions.ValidationError(_('The options to build query incorrect'))
        
        join_option = '\n union \n'
        sql = 'CREATE VIEW %s AS \n' % (self._get_view_name())

        for op in options:
            method_arr = list(map(lambda r: 0, SQL_METHOD_INDEX))
            for key in op.keys():
                if key in SQL_METHOD_INDEX and op[key]:
                    method_index = SQL_METHOD_INDEX.index(key)
                    method_arr.insert(method_index, op[key])
            
            method_arr = list(filter(lambda r: r != 0, method_arr))
            sql += ''.join(str(method) for method in method_arr) + join_option

        return sql[:len(sql) - len(join_option)]

    def _build_query_options(self):
        # Build the options

        options = []

        _select = self._select()
        _from = self._from()
        _join = self._join()
        _where = self._where()
        _group_by = self._group_by()

        for i in range(0, len(_select)):
            options.append({
                    'select': _select[i],
                    'from': _from[i],
                    'join': None if len(_join) < (i + 1) or not _join[i] else _join[i],
                    'where': None if len(_where) < (i + 1) or not _where[i] else _where[i],
                    'group': None if len(_group_by) < (i + 1) or not _group_by[i] else _group_by[i]
                }
            )

        return options

    def execute_query_to_create_view(self, sql = '', options = []):
        """ Execute the query sql to support report
            @param {String} *sql* The sql
            @param {Array} *options* Array options to build query
                            - The element of options should be define following this structure:
                                {
                                    'select': value,
                                    'from': value,
                                    'join': value,
                                    'where': self.value,
                                    'group': self.value
                                }
        """
        tools.drop_view_if_exists(self._cr, self._get_view_name())
        options =  options if len(options) else self._build_query_options()
        sql = sql if sql else self._build_query_to_create_view_report(options)

        self._cr.execute(sql)
    
    @api.model
    def read_group(self, domain, fields, groupby, offset=0, limit=None, orderby=False, lazy=True):
        result = super().read_group(domain, fields, groupby, offset, limit, orderby, lazy)
        if len(result) == 1:
            return result
        return list(filter(lambda group: group.get('__count',False),result))   

    @api.model
    def update_report(self):
        self.execute_query_to_create_view()