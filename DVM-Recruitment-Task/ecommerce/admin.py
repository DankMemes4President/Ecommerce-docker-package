from django.contrib import admin
from import_export.admin import ImportExportModelAdmin

from .models import User, Vendor, Customer, Item, Review, OrderedItems, Cart, Order, ShippingAddress

@admin.register(User)
class UserAdmin(ImportExportModelAdmin):
    pass


@admin.register(Vendor)
class VendorAdmin(ImportExportModelAdmin):
    pass


@admin.register(Customer)
class CustomerAdmin(ImportExportModelAdmin):
    pass


@admin.register(Item)
class ItemAdmin(ImportExportModelAdmin):
    pass


@admin.register(Review)
class ReviewAdmin(ImportExportModelAdmin):
    pass


@admin.register(OrderedItems)
class OrderedItemsAdmin(ImportExportModelAdmin):
    pass


@admin.register(Cart)
class CartAdmin(ImportExportModelAdmin):
    pass


@admin.register(Order)
class OrderAdmin(ImportExportModelAdmin):
    pass


@admin.register(ShippingAddress)
class ShippingAddressAdmin(ImportExportModelAdmin):
    pass
