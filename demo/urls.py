# demo/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # Health check
    path('health/', views.HealthCheckAPIView.as_view(), name='health_check'),
    
    # Payments
    path('payments/', views.PaymentListAPIView.as_view(), name='payment_list'),
    path('payments/create/', views.CreatePaymentAPIView.as_view(), name='create_payment'),
    path('payments/<int:id>/', views.PaymentDetailAPIView.as_view(), name='payment_detail'),
    path('payments/<int:payment_id>/capture/', views.CapturePaymentAPIView.as_view(), name='capture_payment'),
    path('payments/stats/', views.PaymentStatsAPIView.as_view(), name='payment_stats'),
    path('payments/<int:payment_id>/success/', views.PaymentSuccessView.as_view(), name='payment_success'),
    
    # PayPal webhook
    path('paypal/webhook/', views.PayPalWebhookAPIView.as_view(), name='paypal_webhook'),
]
