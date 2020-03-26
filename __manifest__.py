# -*- coding: utf-8 -*-
{
    'name': "Tool Quản Lý Toàn Diện RUBI",
    'summary': """
        Tool Quản Lý Toàn Diện RUBI""",
    'description': """
        Quản lý các đơn hàng đang xử lý, đã gửi, chuyển hoàn
    """,
    'author': "Hiếu Lâm",
    'website': "",
    'category': 'rubi',
    'version': '0.1',
    'depends': ['base','web'],
    'data': [
        'security/user_group.xml',
        # 'data/company_user_data.xml',
        'security/ir.model.access.csv',
        'wizard/set_order_to_delivered_returned_views.xml',
        'wizard/set_reconcile_date_views.xml',
        'views/sale_order_management_view.xml',
        'static/src/xml/custom_render_formview_template.xml',
        'views/sale_order_management_shop_views.xml',
        'report/report_ruby_views.xml',
        'views/menu_action.xml',
        # 'views/shopee_views.xml',
        # 'views/shopee_menu_views.xml',
        'views/menu_views.xml',
        
    ],
    'demo': [],
    'qweb': [
        'static/src/xml/inherit_button_action.xml'
    ],
    'installable': True,
    'auto_install': True,
}