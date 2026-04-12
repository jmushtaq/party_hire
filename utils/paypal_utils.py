import paypalrestsdk
from django.conf import settings

def test_paypal_con():
    '''
    from utils.paypal_utils import test_paypal_con
    test_paypal_con()
    '''
    paypalrestsdk.configure({
        "mode": settings.PAYPAL_MODE,
        "client_id": settings.PAYPAL_CLIENT_ID,
        "client_secret": settings.PAYPAL_CLIENT_SECRET
    })
    print(settings.PAYPAL_MODE)
    print(settings.PAYPAL_CLIENT_ID[:10])
    print(settings.PAYPAL_CLIENT_SECRET[:10])

    # Test creating a simple payment
    try:
        payment = paypalrestsdk.Payment({
            "intent": "sale",
            "payer": {"payment_method": "paypal"},
            "transactions": [{
                "amount": {"total": "10.00", "currency": "AUD"},
                "description": "Test payment"
            }],
            "redirect_urls": {
                "return_url": "http://localhost:8002/",
                "cancel_url": "http://localhost:8002/"
            }
        })

        if payment.create():
            print("✅ PayPal connection successful!")
        else:
            print(f"❌ Error: {payment.error}")
    except Exception as e:
        print(f"❌ Exception: {e}")

