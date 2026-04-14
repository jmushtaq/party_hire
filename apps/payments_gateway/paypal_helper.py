import paypalrestsdk
from django.conf import settings
from decimal import Decimal

# Configure PayPal SDK
paypalrestsdk.configure({
    "mode": settings.PAYPAL_MODE,
    "client_id": settings.PAYPAL_CLIENT_ID,
    "client_secret": settings.PAYPAL_CLIENT_SECRET
})

def create_payment(booking, request):
    """Create a PayPal payment for a booking deposit"""

    # Calculate deposit amount
    deposit_amount = booking.deposit_amount

    # Build payment data - simplified version without item breakdown
    payment_data = {
        "intent": "sale",
        "payer": {
            "payment_method": "paypal"
        },
        "redirect_urls": {
            "return_url": f"{settings.PAYPAL_RETURN_URL}?booking_id={booking.id}",
            "cancel_url": f"{settings.PAYPAL_CANCEL_URL}?booking_id={booking.id}"
        },
        "transactions": [{
            "amount": {
                "total": f"{deposit_amount:.2f}",
                "currency": "AUD",
                "details": {
                    "subtotal": f"{deposit_amount:.2f}",
                }
            },
            "description": f"Deposit payment for booking {booking.booking_number}",
            "invoice_number": booking.booking_number,
            "custom": str(booking.id),
            "item_list": {
                "items": [{
                    "name": f"Deposit for Booking {booking.booking_number}",
                    "sku": booking.booking_number,
                    "price": f"{deposit_amount:.2f}",
                    "currency": "AUD",
                    "quantity": 1
                }]
            }
        }]
    }

    # Create payment
    payment = paypalrestsdk.Payment(payment_data)

    if payment.create():
        return payment
    else:
        print(f"PayPal payment creation failed: {payment.error}")
        return None

def execute_payment(payment_id, payer_id):
    """Execute a PayPal payment after buyer approval"""
    payment = paypalrestsdk.Payment.find(payment_id)

    if payment.execute({"payer_id": payer_id}):
        return payment
    else:
        print(f"PayPal payment execution failed: {payment.error}")
        return None

def get_payment_details(payment_id):
    """Get details of a PayPal payment"""
    try:
        return paypalrestsdk.Payment.find(payment_id)
    except:
        return None

def refund_payment(transaction_id, amount=None):
    """Refund a PayPal payment"""
    payment = paypalrestsdk.Payment.find(transaction_id)

    if payment.state == "approved":
        refund_data = {
            "amount": {
                "total": f"{amount:.2f}" if amount else payment.transactions[0].amount.total,
                "currency": "AUD"
            }
        }
        return payment.refund(refund_data)
    return None
