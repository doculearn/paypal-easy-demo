# PayPal Easy Demo

A Django REST API demonstrating the capabilities of the [paypal-easy](https://pypi.org/project/paypal-easy/) package - a simplified wrapper for PayPal's Python Server SDK.

## [See it in Action](https://youtu.be/EMO9o9O4Fh4?si=5kgIg6Rlbwljzs_W)

### [Get the Postman Collection]([https://github.com/doculearn/paypal-easy-demo/blob/main/PayPal%20Easy%20Demo%20API.postman_collection.json])

## Overview

This demo showcases how paypal-easy transforms PayPal integration from complex, verbose code into simple, readable API calls. Instead of wrestling with 15+ lines of boilerplate and confusing imports, create payments with just a few lines.

## Features Demonstrated

- **Simple Payment Creation**: Create PayPal orders with minimal code
- **Real Payment Flow**: Complete payment lifecycle from creation to capture
- **Error Handling**: Proper error responses and validation
- **Webhook Support**: Handle PayPal webhook notifications
- **Payment Statistics**: Track payment metrics and totals
- **API Documentation**: Complete REST API with proper responses

## Quick Start

### Prerequisites

- Python 3.7+
- Django 4.2+
- PayPal Developer Account (for sandbox credentials)

### Installation

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd paypal-easy-demo
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # or
   venv\Scripts\activate     # Windows
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   # Create .env file
   PAYPAL_CLIENT_ID=your_sandbox_client_id
   PAYPAL_CLIENT_SECRET=your_sandbox_client_secret
   PAYPAL_SANDBOX=True
   ```

5. **Run migrations**
   ```bash
   python manage.py migrate
   python manage.py runserver
   ```

## API Endpoints

### Core Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/health/` | Health check and configuration status |
| POST | `/api/payments/create/` | Create a new PayPal payment |
| GET | `/api/payments/` | List all payments with pagination |
| GET | `/api/payments/{id}/` | Get payment details with PayPal status |
| POST | `/api/payments/{id}/capture/` | Capture an approved payment |
| GET | `/api/payments/stats/` | Payment statistics and totals |
| POST | `/api/paypal/webhook/` | PayPal webhook handler |

### Example Requests

**Create Payment:**
```json
POST /api/payments/create/
{
    "amount": 29.99,
    "description": "Premium subscription",
    "currency": "USD",
    "return_url": "https://yoursite.com/success",
    "cancel_url": "https://yoursite.com/cancel"
}
```

**Response:**
```json
{
    "success": true,
    "payment_id": 1,
    "paypal_order_id": "8C489256ML973904K",
    "approval_url": "https://www.sandbox.paypal.com/checkoutnow?token=8C489256ML973904K",
    "status": "CREATED",
    "amount": "29.99",
    "currency": "USD"
}
```

## Testing with Postman

Import the complete Postman collection to test all endpoints:

1. Download the collection from the [paypal-easy repository](https://github.com/yourusername/paypal-easy)
2. Import into Postman
3. Set `base_url` variable to `http://localhost:8000`
4. Run the requests in sequence

The collection includes:
- Health checks
- Payment creation and validation
- Payment lifecycle testing  
- Error scenario testing
- Webhook simulation

## Code Examples

### Before (PayPal SDK)
```python
from paypalserversdk.paypal_serversdk_client import PaypalServersdkClient
from paypalserversdk.configuration import Environment
from paypalserversdk.http.auth.o_auth_2 import ClientCredentialsAuthCredentials
from paypalserversdk.models.order_request import OrderRequest
from paypalserversdk.models.purchase_unit_request import PurchaseUnitRequest
from paypalserversdk.models.amount_with_breakdown import AmountWithBreakdown

# 15+ lines of complex setup...
credentials = ClientCredentialsAuthCredentials(
    o_auth_client_id=client_id,
    o_auth_client_secret=client_secret
)

client = PaypalServersdkClient(
    environment=Environment.SANDBOX,
    client_credentials_auth_credentials=credentials
)

amount = AmountWithBreakdown(
    currency_code="USD",
    value="29.99"
)

purchase_unit = PurchaseUnitRequest(
    amount=amount,
    description="Payment description"
)

order_request = OrderRequest(
    intent="CAPTURE",
    purchase_units=[purchase_unit]
)

response = client.orders.create_order({'body': order_request})
```

### After (paypal-easy)
```python
from paypal_easy import PayPalEasyClient, Environment, Currency

client = PayPalEasyClient(client_id, client_secret, Environment.SANDBOX)
result = client.create_order(
    amount=29.99,
    currency=Currency.USD,
    description="Payment description"
)
```

## Project Structure

```
paypal_easy_demo/
├── paypal_easy_demo/
│   ├── settings.py          # Django settings with PayPal config
│   └── urls.py             # Main URL configuration
├── demo/
│   ├── models.py           # Payment demo model
│   ├── serializers.py      # DRF serializers
│   ├── views.py            # API views using paypal-easy
│   └── urls.py             # Demo app URLs
├── requirements.txt        # Python dependencies
└── README.md              # This file
```

## Key Features Demonstrated

### 1. Simple Integration
The demo shows how paypal-easy reduces PayPal integration complexity:
- Clean, intuitive API
- Proper error handling
- Type hints for IDE support
- Consistent response formats

### 2. Complete Payment Flow
- Payment creation with approval URLs
- Payment capture after user approval
- Status checking and updates
- Webhook handling for notifications

### 3. Developer Experience
- Comprehensive error messages
- Built-in logging
- Django integration helpers
- Postman collection for testing

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `PAYPAL_CLIENT_ID` | PayPal application client ID | Required |
| `PAYPAL_CLIENT_SECRET` | PayPal application client secret | Required |
| `PAYPAL_SANDBOX` | Use sandbox environment | `True` |

## Sandbox Testing

The demo uses PayPal's sandbox environment by default. You can:
- Create test payments without real money
- Use PayPal's sandbox testing tools
- View transaction logs in the PayPal Developer Dashboard
- Test different payment scenarios and error conditions

## Contributing

This demo project welcomes contributions:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## Related Projects

- **[paypal-easy](https://pypi.org/project/paypal-easy/)** - The main package
- **[PayPal Server SDK](https://pypi.org/project/paypal-server-sdk/)** - Official PayPal SDK

## Support

- **Package Issues**: [GitHub Issues](https://github.com/yourusername/paypal-easy/issues)
- **Demo Issues**: [Demo Repository Issues](https://github.com/yourusername/paypal-easy-demo/issues)
- **PayPal Documentation**: [PayPal Developer Docs](https://developer.paypal.com/docs/)

## License

This demo project is open source and available under the MIT License.

---

**Try paypal-easy today**: `pip install paypal-easy`
