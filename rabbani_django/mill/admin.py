from django.contrib import admin

from .models import Product, Order, Profile, ContactMessage


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'tag', 'rate_per_kg', 'is_available')
    list_filter = ('tag', 'is_available')
    search_fields = ('name',)


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone', 'city')
    search_fields = ('user__username', 'phone')


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('tracking_number', 'customer', 'product', 'destination_city', 'total_amount', 'status', 'created_at')
    list_filter = ('status', 'destination_city', 'product')
    search_fields = ('tracking_number', 'customer__username', 'phone')
    readonly_fields = ('tracking_number', 'product_cost', 'delivery_fare', 'total_amount', 'created_at', 'updated_at')


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone', 'created_at')
    search_fields = ('name', 'phone')
