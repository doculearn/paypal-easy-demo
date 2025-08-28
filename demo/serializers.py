# demo/serializers.py
from rest_framework import serializers
from .models import PaymentDemo

class PaymentDemoSerializer(serializers.ModelSerializer):
    user_email = serializers.CharField(source='user.email', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = PaymentDemo
        fields = [
            'id',
            'amount',
            'currency',
            'description',
            'paypal_order_id',
            'status',
            'status_display',
            'user_email',
            'payer_email',
            'error_message',
            'created_at',
            'updated_at'
        ]
        read_only_fields = [
            'id', 'paypal_order_id', 'status', 'payer_email', 
            'error_message', 'created_at', 'updated_at'
        ]

class CreatePaymentSerializer(serializers.Serializer):
    amount = serializers.DecimalField(max_digits=10, decimal_places=2, min_value=0.01)
    description = serializers.CharField(max_length=200)
    currency = serializers.CharField(max_length=3, default='USD')
    return_url = serializers.URLField(required=False)
    cancel_url = serializers.URLField(required=False)
    brand_name = serializers.CharField(max_length=100, required=False)