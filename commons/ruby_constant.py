# -*- coding: utf-8 -*-

from odoo.tools.translate import _

#Delta time
DELTA_TIME = 7

header = {
    'Order Item Id': 'order_item_id',
    'Order Type': 'order_type',
    'Order Flag': 'order_flag',
    'Lazada Id': 'lazada_id',
    'Seller SKU': 'seller_sku',
    'Lazada SKU': 'lazada_sku',
    'Created at': 'created_at',
    'Updated at': 'updated_at',
    'Order Number': 'order_number',
    'Invoice Required': 'invoice_required',
    'Customer Name': 'customer_name',
    'Customer Email': 'customer_email',
    'National Registration Number': 'national_registration_number',
    'Shipping Name': 'shipping_name',
    'Shipping Address': 'shipping_address',
    'Shipping Address2': 'shipping_address2',
    'Shipping Address3': 'shipping_address3',
    'Shipping Address4': 'shipping_address4',
    'Shipping Address5': 'shipping_address5',
    'Shipping Phone Number': 'shipping_phone_number',
    'Shipping Phone Number2': 'shipping_phone_number2',
    'Shipping City': 'shipping_city',
    'Shipping Postcode': 'shipping_postcode',
    'Shipping Country': 'shipping_country',
    'Shipping Region': 'shipping_region',
    'Billing Name': 'billing_name',
    'Billing Address': 'billing_address',
    'Billing Address2': 'billing_address2',
    'Billing Address3': 'billing_address3',
    'Billing Address4': 'billing_address4',
    'Billing Address5': 'billing_address5',
    'Billing Phone Number': 'billing_phone_number',
    'Billing Phone Number2': 'billing_phone_number2',
    'Billing City': 'billing_city',
    'Billing Postcode': 'billing_postcode',
    'Billing Country': 'billing_country',
    'Tax Code': 'tax_code',
    'Branch Number': 'branch_number',
    'Tax Invoice requested': 'tax_invoice_requested',
    'Payment Method': 'payment_method',
    'Paid Price': 'paid_price',
    'Unit Price': 'unit_price',
    'Shipping Fee': 'shipping_fee',
    'Wallet Credits': 'wallet_credits',
    'Item Name': 'item_name',
    'Variation': 'variation',
    'CD Shipping Provider': 'cd_shipping_provider',
    'Shipping Provider': 'shipping_provider',
    'Shipment Type Name': 'shipment_type_name',
    'Shipping Provider Type': 'shipping_provider_type',
    'CD Tracking Code': 'cd_tracking_code',
    'Tracking Code': 'tracking_code',
    'Tracking URL': 'tracking_url',
    'Shipping Provider (first mile)': 'shipping_provider_first_mile',
    'Tracking Code (first mile)': 'tracking_code_first_mile',
    'Tracking URL (first mile)': 'tracking_url_first_mile',
    'Promised shipping time': 'promised_shipping_time',
    'Premium': 'premium',
    'Status': 'status',
    'Cancel / Return Initiator': 'cancel_return_initiator',
    'Reason': 'reason',
    'Reason Detail': 'reason_detail',
    'Editor': 'editor',
    'Bundle ID': 'bundle_id',
    'Bundle Discount': 'bundle_discount',
    'Refund Amount': 'refund_amount'
}

shopee_header = {
    'Mã đơn hàng': 'ma_don_hang',
    'Mã Kiện Hàng': 'forder_id',
    'Ngày đặt hàng': 'ngay_dat_hang',
    'Trạng Thái Đơn Hàng': 'tinh_trang_don_hang',
    'Nhận xét từ Người mua': 'nhan_xet_tu_nguoi_mua',
    'Mã vận đơn': 'ma_van_don',
    'Đơn Vị Vận Chuyển': 'lua_chon_van_chuyen',
    'Phương thức giao hàng': 'phuong_thuc_giao_hang',
    'Loại đơn hàng': 'loai_don_hang',
    'Ngày giao hàng dự kiến': 'ngay_giao_hang_du_kien',
    'Ngày gửi hàng': 'ngay_gui_hang',
    'Thời gian giao hàng': 'thoi_gian_giao_hang',
    'Tình trạng Trả hàng / Hoàn tiền': 'tinh_trang_tra_hang_hoan_tien',
    'SKU sản phẩm': 'sku_san_pham',
    'Tên sản phẩm': 'ten_san_pham',
    'Cân nặng sản phẩm': 'can_nang_san_pham_1',
    'Tổng cân nặng': 'tong_can_nang',
    'Cân nặng sản phẩm.1': 'can_nang_san_pham_2',
    'SKU phân loại hàng': 'sku_phan_loai_hang',
    'Tên phân loại hàng': 'ten_phan_loai_hang',
    'Giá gốc': 'gia_goc',
    'Người bán trợ giá': 'nguoi_ban_tu_giam',
    'Được Shopee trợ giá': 'duoc_shopee_tro_gia',
    'Tổng số tiền được người bán trợ giá': 'duoc_nguoi_ban_tro_gia',
    'Giá ưu đãi': 'gia_uu_dai',
    'Số lượng': 'so_luong',
    'Tổng giá bán (sản phẩm)': 'product_subtotal',
    'Tổng giá trị đơn hàng (VND)': 'tien_don_hang',
    'Mã giảm giá của Shop': 'ma_giam_gia_cua_shop',
    'Hoàn Xu': 'hoan_xu',
    'Mã giảm giá của Shopee': 'shopee_voucher',
    'Chỉ tiêu combo khuyến mãi': 'chi_tieu_combo_khuyen_mai',
    'Giảm giá từ combo Shopee': 'giam_gia_tu_combo_shopee',
    'Giảm giá từ Combo của Shop': 'giam_gia_tu_combo_cua_shop',
    'Shopee Xu được hoàn': 'shopee_xu_duoc_hoan',
    'Số tiền được giảm khi thanh toán bằng thẻ Ghi nợ': 'so_tien_duoc_giam_khi_thanh_bang_the_ghi_no',
    'Phí vận chuyển (dự kiến)': 'phi_van_chuyen',
    'Phí vận chuyển mà người mua trả': 'phi_van_chuyen_ma_nguoi_mua_tra',
    'Tổng số tiền người mua thanh toán': 'tong_so_tien',
    'Thời gian hoàn thành đơn hàng': 'thoi_gian_hoan_thang_don_hang',
    'Thời gian đơn hàng được thanh toán': 'thoi_gian_don_hang_duoc_thanh_toan',
    'Phương thức thanh toán': 'phuong_thuc_thanh_toan',
    'Phí cố định': 'phi_co_dinh',
    'Phí Dịch Vụ': 'phi_dich_vu',
    'Phí giao dịch': 'phi_giao_dich',
    'Tiền ký quỹ': 'tien_ky_quy',
    'Người Mua': 'username',
    'Tên Người nhận': 'ten_nguoi_nhan',
    'Số điện thoại': 'so_dien_thoai',
    'Tỉnh/Thành phố': 'tinh_thanh_pho',
    'TP / Quận / Huyện': 'tp_quan_huyen',
    'Quận': 'district',
    'Địa chỉ nhận hàng': 'dia_chi_nhan_hang',
    'Quốc gia': 'quoc_gia',
    'Ghi chú': 'ghi_chu',
}


#FEE NAME
SHIP_FEE_BY_CUS = 'Shipping Fee (Paid By Customer)'
ITEM_PRICE = 'Item Price Credit'
SHIP_FEE_BY_SELLER = 'Shipping Fee Paid by Seller'
SHIP_FEE_VOUCHER_LAZADA = 'Shipping Fee Voucher (by Lazada)'
PROMOTION_CHARGES_VOUCHER = 'Promotional Charges Vouchers'
ADJ_PAYMENT_FEE = 'Adjustments Payment Fee'
PAYMENT_FEE = 'Payment Fee'
SPON_PRODUCT_FEE = 'Sponsored Product Fee'
REVERSAL_SHIP_FEE = 'Reversal shipping Fee (Paid by Customer)'
REVERSAL_ITEM_PRICE = 'Reversal Item Price'
ADJ_SHIP_FEE = 'Adjustments Shipping Fee'
SHIP_FEE_CLAIM = 'Shipping Fee Claims'
SHIP_FEE_SUBSIDY = 'Auto. Shipping fee subsidy (by Lazada)'

#KEY HEADER
ODER_ITEM_NO = 'Order Item No.'
TRANSACTION_DATE = 'Transaction Date'
FEE_NAME = 'Fee Name'
AMOUNT = 'Amount'
ORDER_NO = 'Order No.'
ORDER_STATUS = 'Order Item Status'
ITEM_PRICE = 'Item Price Credit'


#PRICE FOR LAZADA
SHIPPING_FEE_PAID_BY_CUSTOMER =  'Shipping Fee (Paid By Customer)'
ITEM_PRICE_CREDIT =  'Item Price Credit'
PROMOTIONAL_CHARGES_VOUCHERS =  'Promotional Charges Vouchers'
SHIPPING_FEE_VOUCHER_BY_LAZADA =  'Shipping Fee Voucher (by Lazada)'
SHIPPING_FEE_PAID_BY_SELLER =  'Shipping Fee Paid by Seller'
PROMOTIONAL_CHARGES_FLEXICOMBO =  'Promotional Charges Flexi-Combo'
MARKETING_SOLUTION_SOCIAL_MEDIA_ADVERTISING =  'Marketing solution /social media advertising'
REVERSAL_ITEM_PRICE =  'Reversal Item Price'
REVERSAL_SHIPPING_FEE_PAID_BY_CUSTOMER =  'Reversal shipping Fee (Paid by Customer)'
REVERSAL_PROMOTIONAL_CHARGES_FLEXICOMBO =  'Reversal Promotional Charges Flexi-Combo'
REVERSAL_SHIPPING_FEE_VOUCHER_BY_LAZADA =  'Reversal Shipping Fee Voucher (by Lazada)'
REVERSAL_PROMOTIONAL_CHARGES_VOUCHERS =  'Reversal Promotional Charges Vouchers'
LAZADA_BONUS =  'Lazada Bonus'
LAZADA_BONUS_LZD_COFUND =  'Lazada Bonus - LZD co-fund'
SPONSORED_DISCOVERY_TOP_UP =  'Sponsored Discovery - Top up'

SELLER_SKU = 'Seller SKU'