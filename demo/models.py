# demo/models.py
from django.db import models
from django.contrib.auth.models import User

class PaymentDemo(models.Model):
    PAYMENT_STATUS = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.CharField(max_length=200)
    currency = models.CharField(max_length=3, default='USD')
    paypal_order_id = models.CharField(max_length=100, blank=True, null=True)
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS, default='pending')
    payer_email = models.EmailField(blank=True, null=True)
    error_message = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Payment #{self.id} - ${self.amount} ({self.status})"
    
    class Meta:
        ordering = ['-created_at']
