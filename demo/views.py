# demo/views.py
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from django.conf import settings
from django.shortcuts import get_object_or_404
import logging

from paypal_easy import PayPalEasyClient, Environment, Currency
from .models import PaymentDemo
from .serializers import PaymentDemoSerializer, CreatePaymentSerializer

logger = logging.getLogger(__name__)

def get_paypal_client():
    """Get configured PayPal client"""
    env = Environment.SANDBOX if settings.PAYPAL_SANDBOX else Environment.PRODUCTION
    return PayPalEasyClient(
        client_id=settings.PAYPAL_CLIENT_ID,
        client_secret=settings.PAYPAL_CLIENT_SECRET,
        environment=env
    )

class HealthCheckAPIView(APIView):
    """Health check endpoint"""
    permission_classes = [AllowAny]
    
    def get(self, request):
        return Response({
            'status': 'healthy',
            'paypal_sandbox': settings.PAYPAL_SANDBOX,
            'paypal_configured': bool(settings.PAYPAL_CLIENT_ID != 'demo_client_id'),
            'environment': 'sandbox' if settings.PAYPAL_SANDBOX else 'production'
        })

class CreatePaymentAPIView(APIView):
    """Create a PayPal payment"""
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = CreatePaymentSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {'errors': serializer.errors}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        data = serializer.validated_data
        
        try:
            # Create payment record
            payment = PaymentDemo.objects.create(
                user=request.user if request.user.is_authenticated else None,
                amount=data['amount'],
                description=data['description'],
                currency=data.get('currency', 'USD'),
                status='pending'
            )
            
            # Get currency enum
            try:
                currency_enum = getattr(Currency, data.get('currency', 'USD'))
            except AttributeError:
                currency_enum = Currency.USD
            
            # Create PayPal order using paypal-easy
            client = get_paypal_client()
            result = client.create_order(
                amount=data['amount'],
                currency=currency_enum,
                description=data['description'],
                return_url=data.get('return_url', f'http://localhost:8000/api/payments/{payment.id}/success/'),
                cancel_url=data.get('cancel_url', f'http://localhost:8000/api/payments/{payment.id}/cancel/'),
                brand_name=data.get('brand_name', 'PayPal Easy Demo')
            )
            
            if hasattr(result, 'id'):  # Success
                payment.paypal_order_id = result.id
                payment.save()
                
                logger.info(f"Payment {payment.id} created with PayPal order {result.id}")
                
                return Response({
                    'success': True,
                    'payment_id': payment.id,
                    'paypal_order_id': result.id,
                    'approval_url': result.approval_url,
                    'status': result.status.value,
                    'amount': str(data['amount']),
                    'currency': data.get('currency', 'USD'),
                    'description': data['description']
                }, status=status.HTTP_201_CREATED)
            else:  # Error
                payment.status = 'failed'
                payment.error_message = result.message
                payment.save()
                
                logger.error(f"Payment {payment.id} failed: {result.message}")
                
                return Response({
                    'success': False,
                    'error': result.message,
                    'payment_id': payment.id
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except Exception as e:
            logger.error(f"Payment creation error: {str(e)}")
            return Response(
                {'error': f'Payment creation failed: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class PaymentListAPIView(ListAPIView):
    """List all payments"""
    queryset = PaymentDemo.objects.all()
    serializer_class = PaymentDemoSerializer
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by status
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        # Filter by currency
        currency_filter = self.request.query_params.get('currency')
        if currency_filter:
            queryset = queryset.filter(currency=currency_filter.upper())
        
        return queryset

class PaymentDetailAPIView(RetrieveAPIView):
    """Get payment details"""
    queryset = PaymentDemo.objects.all()
    serializer_class = PaymentDemoSerializer
    permission_classes = [AllowAny]
    lookup_field = 'id'
    
    def retrieve(self, request, *args, **kwargs):
        payment = self.get_object()
        
        # Get current PayPal status if available
        paypal_data = {}
        if payment.paypal_order_id:
            try:
                client = get_paypal_client()
                result = client.get_order(payment.paypal_order_id)
                if hasattr(result, 'status'):
                    paypal_data = {
                        'paypal_status': result.status.value,
                        'paypal_payer_email': result.payer_email,
                        'paypal_approval_url': result.approval_url,
                        'paypal_amount': str(result.amount) if result.amount else None,
                        'paypal_currency': result.currency.value if result.currency else None
                    }
            except Exception as e:
                paypal_data = {'paypal_error': str(e)}
        
        # Serialize payment data
        serializer = self.get_serializer(payment)
        response_data = serializer.data
        response_data.update(paypal_data)
        
        return Response(response_data)

class CapturePaymentAPIView(APIView):
    """Capture a PayPal payment"""
    permission_classes = [AllowAny]
    
    def post(self, request, payment_id):
        try:
            payment = get_object_or_404(PaymentDemo, id=payment_id)
            
            if not payment.paypal_order_id:
                return Response(
                    {'error': 'No PayPal order ID found'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            if payment.status == 'completed':
                return Response(
                    {'message': 'Payment already completed', 'status': 'completed'}, 
                    status=status.HTTP_200_OK
                )
            
            # Capture payment using paypal-easy
            client = get_paypal_client()
            result = client.capture_order(payment.paypal_order_id)
            
            if hasattr(result, 'status') and result.status.value == 'COMPLETED':
                payment.status = 'completed'
                if result.payer_email:
                    payment.payer_email = result.payer_email
                payment.save()
                
                logger.info(f"Payment {payment.id} captured successfully")
                
                return Response({
                    'success': True,
                    'payment_id': payment.id,
                    'paypal_order_id': payment.paypal_order_id,
                    'status': result.status.value,
                    'payer_email': result.payer_email,
                    'amount': str(result.amount) if result.amount else str(payment.amount),
                    'message': 'Payment captured successfully'
                })
            else:
                error_msg = f'Capture failed: {result.status.value if hasattr(result, "status") else "Unknown error"}'
                payment.error_message = error_msg
                payment.save()
                
                logger.error(f"Payment {payment.id} capture failed: {error_msg}")
                
                return Response({
                    'success': False,
                    'error': error_msg,
                    'payment_id': payment.id
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except Exception as e:
            logger.error(f"Payment {payment_id} capture error: {str(e)}")
            return Response(
                {'error': f'Capture failed: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class PayPalWebhookAPIView(APIView):
    """Handle PayPal webhook notifications"""
    permission_classes = [AllowAny]
    
    def post(self, request):
        try:
            data = request.data
            event_type = data.get('event_type')
            resource = data.get('resource', {})
            
            logger.info(f"PayPal webhook received: {event_type}")
            
            # Handle different webhook events
            if event_type == 'CHECKOUT.ORDER.APPROVED':
                order_id = resource.get('id')
                if order_id:
                    try:
                        payment = PaymentDemo.objects.get(paypal_order_id=order_id)
                        logger.info(f"Order {order_id} approved for payment {payment.id}")
                    except PaymentDemo.DoesNotExist:
                        logger.warning(f"No payment found for PayPal order {order_id}")
            
            elif event_type == 'PAYMENT.CAPTURE.COMPLETED':
                order_id = resource.get('supplementary_data', {}).get('related_ids', {}).get('order_id')
                if order_id:
                    try:
                        payment = PaymentDemo.objects.get(paypal_order_id=order_id)
                        payment.status = 'completed'
                        payer_info = resource.get('payer', {})
                        if payer_info.get('email_address'):
                            payment.payer_email = payer_info['email_address']
                        payment.save()
                        logger.info(f"Payment {payment.id} completed via webhook")
                    except PaymentDemo.DoesNotExist:
                        logger.warning(f"No payment found for PayPal order {order_id}")
            
            return Response({'status': 'webhook processed'})
            
        except Exception as e:
            logger.error(f"Webhook processing error: {str(e)}")
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class PaymentStatsAPIView(APIView):
    """Get payment statistics"""
    permission_classes = [AllowAny]
    
    def get(self, request):
        try:
            stats = {
                'total_payments': PaymentDemo.objects.count(),
                'completed_payments': PaymentDemo.objects.filter(status='completed').count(),
                'pending_payments': PaymentDemo.objects.filter(status='pending').count(),
                'failed_payments': PaymentDemo.objects.filter(status='failed').count(),
                'cancelled_payments': PaymentDemo.objects.filter(status='cancelled').count(),
            }
            
            # Add total amounts
            from django.db.models import Sum
            total_completed = PaymentDemo.objects.filter(status='completed').aggregate(
                total=Sum('amount')
            )['total'] or 0
            
            stats['total_completed_amount'] = str(total_completed)
            
            return Response(stats)
            
        except Exception as e:
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
