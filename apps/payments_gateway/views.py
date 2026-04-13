from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from apps.bookings.models import Booking
from .paypal_helper import create_payment, execute_payment

def initiate_payment(request, booking_id):
    """Initiate PayPal payment for a booking"""
    booking = get_object_or_404(Booking, id=booking_id)

    # Verify booking belongs to session or user
    # For now, just check that the email matches (you can improve this)
    if request.session.get('booking_email') != booking.customer_email:
        messages.error(request, "Invalid booking")
        return redirect('bookings:cart')

    # Create PayPal payment
    payment = create_payment(booking, request)

    if payment:
        # Store payment ID in session
        request.session['paypal_payment_id'] = payment.id

        # Redirect to PayPal approval URL
        for link in payment.links:
            if link.rel == "approval_url":
                return redirect(link.href)

        messages.error(request, "PayPal approval URL not found")
    else:
        messages.error(request, "Could not create PayPal payment. Please try again.")

    return redirect('bookings:checkout')

@csrf_exempt
def payment_success(request):
    """Handle successful PayPal payment"""
    payment_id = request.GET.get('paymentId')
    payer_id = request.GET.get('PayerID')
    booking_id = request.GET.get('booking_id')

    if not all([payment_id, payer_id, booking_id]):
        messages.error(request, "Invalid payment response")
        return redirect('home')

    # Execute the payment
    payment = execute_payment(payment_id, payer_id)

    if payment and payment.state == "approved":
        # Update booking status
        booking = get_object_or_404(Booking, id=booking_id)
        booking.deposit_paid = True
        booking.status = 'deposit_paid'
        booking.stripe_payment_intent_id = payment_id  # Store PayPal transaction ID
        booking.save()

        # Clear session cart
        if 'booking_cart' in request.session:
            del request.session['booking_cart']

        messages.success(request, f"Payment successful! Your booking {booking.booking_number} is confirmed.")
        return redirect('bookings:booking_success', booking_number=booking.booking_number)
    else:
        messages.error(request, "Payment could not be processed. Please contact support.")
        return redirect('bookings:cart')

def payment_cancel(request):
    """Handle cancelled PayPal payment"""
    booking_id = request.GET.get('booking_id')

    messages.warning(request, "Payment was cancelled. You can try again when you're ready.")

    if booking_id:
        return redirect('bookings:checkout')
    return redirect('bookings:cart')
