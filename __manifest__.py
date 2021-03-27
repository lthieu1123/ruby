# -*- coding: utf-8 -*-
{
    'name': "Tool Quản Lý Toàn Diện RUBI",
    'summary': """
        Tool Quản Lý Toàn Diện RUBI""",
    'description': """
    """,
    'author': "Hiếu Lâm",
    'website': "",
    'category': 'rubi',
    'version': '8.0.6',
    'license': 'AGPL-3',
    'depends': ['base','web','mail','decimal_precision'],
    'data': [
        'security/user_group.xml',
        'data/directory_data.xml',
        'data/discuss.xml',
        'data/functions.xml',
        'security/ir.model.access.csv',
        'wizard/set_order_to_delivered_returned_views.xml',
        'wizard/set_reconcile_date_views.xml',
        'wizard/set_order_for_shopee_views.xml',
        'wizard/lazada_reconcile_fee_views.xml',
        'wizard/module_info.xml',
        'views/sale_order_management_view.xml',
        'static/src/xml/custom_render_formview_template.xml',
        'views/sale_order_management_shop_views.xml',
        'report/report_ruby_views.xml',
        'report/lazada_report_order_number_views.xml',
        'report/shopee_report_order_view.xml',
        'views/menu_action.xml',
        'views/shopee_views.xml',
        'views/sale_order_management_shopee_shop_views.xml',
        'views/lazada_formula_views.xml',
        'views/lazada_report_sum_views.xml',
        'views/directory_shop_views.xml',
        'views/shopee_menu_views.xml',
        'views/menu_views.xml',
        'views/sendo_tiki_views.xml'
    ],
    'demo': [],
    'qweb': [
        'static/src/xml/inherit_button_action.xml'
    ],
    # 'installable': True,
    # 'auto_install': True,
}
