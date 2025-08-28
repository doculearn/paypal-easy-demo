# demo/admin.py
from django.contrib import admin
from .models import PaymentDemo

@admin.register(PaymentDemo)
class PaymentDemoAdmin(admin.ModelAdmin):
    list_display = ['id', 'amount', 'currency', 'description', 'status', 'paypal_order_id', 'created_at']
    list_filter = ['status', 'currency', 'created_at']
    search_fields = ['description', 'paypal_order_id', 'payer_email']
    readonly_fields = ['paypal_order_id', 'created_at', 'updated_at']
