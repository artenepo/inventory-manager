from django.contrib import admin

from .models import Product, Brand, Item, Category, Supplier


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ("name", "phone")


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    empty_value_display = ""
    list_display = ("created_date", "product", "cost", "status", "sold_date")


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "cost")
    list_filter = ("category", "brand")


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    ...


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    ...
