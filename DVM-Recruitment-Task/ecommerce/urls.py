from django.urls import path, include

from .views import ecommerce_home, vendor, customer

app_name = "ecommerce"

urlpatterns = [
    path('', ecommerce_home.home, name='home'),
    path('profile', ecommerce_home.GoogleUserRoles.as_view(), name='roles'),
    path('vendor/', include(([
        path('', vendor.VendorDashboard.as_view(), name='vendor_dashboard'),
        path('items/add', vendor.VendorAddItems.as_view(), name='vendor_add_items'),
        path('items/<str:item>/edit', vendor.VendorEditItems.as_view(), name='vendor_edit_items'),
        path('orders', vendor.VendorViewOrders.as_view(), name='vendor_view_orders'),
        path('orders/export', vendor.vendor_order_generate_csv, name='vendor_order_generate_csv'),
    ]))),
    path('customer/', include(([
        path('', customer.CustomerDashboard.as_view(), name='customer_dashboard'),
        path('<str:vendor>/items', customer.CustomerVendorItems.as_view(), name='customer_vendor_items'),
        # path('<str:item>/cart/add', customer.CustomerCartAddItems.as_view(), name='customer_cart_add_items'),
        path('<str:item>/detail', customer.CustomerViewItem.as_view(), name='customer_item_details'),
        path('addmoney', customer.CustomerAddMoney.as_view(), name='customer_add_money'),
        path('cart', customer.CustomerCart.as_view(), name='customer_cart'),
        path('cart/<str:item>/edit', customer.CustomerCartItemsEdit.as_view(), name='customer_cart_item_edit'),
        path('cart/checkout', customer.CustomerCheckout.as_view(), name='customer_cart_checkout'),
        path('<str:item>/review/add', customer.CustomerItemReview.as_view(), name='customer_add_review'),
        path('orders', customer.CustomerViewPrevOrders.as_view(), name='customer_view_prev_orders'),
        path('address', customer.CustomerShippingAddress.as_view(), name='customer_shipping_address'),
        path('wishlist', customer.CustomerWishList.as_view(), name='customer_wishlist'),
    ]))),
]
