# admin.py
from django.contrib import admin
from .models import (
    Category, Supplier, Product, Store,
    StoreInventory, User, Order, OrderItem
)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at', 'updated_at')
    search_fields = ('name',)
    list_filter = ('created_at',)


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ('name', 'inn', 'rating', 'contact_phone', 'created_at')
    search_fields = ('name', 'inn', 'email')
    list_filter = ('rating', 'created_at')


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'article', 'barcode', 'price', 'is_active', 'supplier', 'created_at')
    list_filter = ('is_active', 'supplier', 'category', 'created_at')
    search_fields = ('name', 'article', 'barcode')
    raw_id_fields = ('supplier', 'category')
    readonly_fields = ('created_at', 'updated_at')


class StoreInventoryInline(admin.TabularInline):
    model = StoreInventory
    extra = 1
    raw_id_fields = ('product',)


@admin.register(Store)
class StoreAdmin(admin.ModelAdmin):
    list_display = ('name', 'region', 'phone', 'is_active', 'created_at')
    list_filter = ('is_active', 'region', 'created_at')
    search_fields = ('name', 'address', 'phone')
    inlines = [StoreInventoryInline]
    readonly_fields = ('created_at', 'updated_at')


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('login', 'full_name', 'role', 'store', 'is_active', 'last_login')
    list_filter = ('role', 'is_active', 'store', 'created_at')
    search_fields = ('login', 'full_name', 'email', 'phone')
    readonly_fields = ('last_login', 'created_at', 'updated_at')
    fieldsets = (
        (None, {
            'fields': ('login', 'password_hash', 'full_name')
        }),
        ('Дополнительная информация', {
            'fields': ('role', 'store', 'phone', 'email')
        }),
        ('Настройки доступа', {
            'fields': ('is_active', 'permissions')
        }),
        ('Даты', {
            'fields': ('last_login', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1
    raw_id_fields = ('product',)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_number', 'customer_name', 'store', 'status', 'total_sum', 'created_at')
    list_filter = ('status', 'store', 'created_at')
    search_fields = ('order_number', 'customer_name', 'customer_phone')
    inlines = [OrderItemInline]
    readonly_fields = ('created_at', 'updated_at', 'total_sum')
    raw_id_fields = ('store', 'created_by')


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'product', 'quantity', 'price', 'total_price')
    list_filter = ('created_at',)
    raw_id_fields = ('order', 'product')