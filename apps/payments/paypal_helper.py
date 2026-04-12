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

    # Calculate amounts
    deposit_amount = booking.deposit_amount
    total_amount = booking.total_amount

    # Build payment data
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
            "item_list": {
                "items": []
            },
            "amount": {
                "total": f"{deposit_amount:.2f}",
                "currency": "AUD"
            },
            "description": f"Deposit payment for booking {booking.booking_number}",
            "invoice_number": booking.booking_number,
            "custom": str(booking.id)
        }]
    }

    # Add items to the transaction
    for booking_item in booking.items.all():
        item = {
            "name": booking_item.item.name[:127],  # PayPal max length
            "sku": str(booking_item.item.id),
            "price": f"{booking_item.price_per_day:.2f}",
            "currency": "AUD",
            "quantity": booking_item.quantity
        }
        payment_data["transactions"][0]["item_list"]["items"].append(item)

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
