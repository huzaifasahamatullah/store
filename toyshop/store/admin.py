from django.contrib import admin
from .models import Category, Product, Order, OrderItem

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    readonly_fields = ('product', 'quantity', 'price')  # Make fields read-only
    extra = 0  # Remove extra blank fields

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user_name', 'user_email', 'get_total_price', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('user_name', 'user_email', 'user_phone')
    readonly_fields = ('created_at',)
    inlines = [OrderItemInline]

    def get_total_price(self, obj):
        """
        Calculate the total price of all items in the order.
        """
        return sum(item.price * item.quantity for item in obj.items.all())
    
    get_total_price.short_description = 'Total Price'

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return self.readonly_fields + ('user_name', 'user_email', 'user_address', 'user_phone')
        return self.readonly_fields


# Register additional models
admin.site.register(Category)
admin.site.register(Product)
