from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views.generic import FormView
from django.db import transaction
from decimal import Decimal
from payments import RedirectNeeded
from apps.payments_gateway.models import Payment

from apps.bookings.models import Booking, BookingItem
from apps.items.models import HireItem, ItemAvailability
from apps.checkout.forms import CheckoutForm
from apps.bookings.invoice import generate_booking_invoice  # Use local invoice function

import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class CheckoutView(FormView):
    """
    Enhanced checkout view with payment integration and invoice generation
    """
    template_name = 'checkout/checkout.html'
    form_class = CheckoutForm
    success_url = '/checkout/success/'

    def get_initial(self):
        """Pre-populate form with session data if available"""
        initial = super().get_initial()
        cart = self.request.session.get('booking_cart', {})
        if cart:
            initial['start_date'] = self.request.session.get('booking_start_date')
            initial['end_date'] = self.request.session.get('booking_end_date')
        return initial

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cart = self.request.session.get('booking_cart', {})
        subtotal, delivery_cost, grand_total, deposit = self.calculate_cart_totals(cart)
        context.update({
            'subtotal': subtotal,
            'delivery_cost': delivery_cost,
            'total': grand_total,
            'deposit': deposit,
            'booking_start_date': self.request.session.get('booking_start_date'),
            'booking_end_date': self.request.session.get('booking_end_date'),
        })
        return context

    def calculate_cart_totals(self, cart):
        """Calculate cart totals"""
        subtotal = Decimal('0')
        for item_id, item_data in cart.items():
            try:
                item = HireItem.objects.get(id=item_id)
                start = datetime.strptime(item_data['start_date'], '%Y-%m-%d')
                end = datetime.strptime(item_data['end_date'], '%Y-%m-%d')
                item_total = item.calculate_total_price(item_data['quantity'], start, end)
                subtotal += item_total
            except Exception:
                continue

        delivery_cost = Decimal('50') if subtotal > 0 else Decimal('0')
        grand_total = subtotal + delivery_cost
        deposit = grand_total * Decimal('0.3')
        return subtotal, delivery_cost, grand_total, deposit

    @transaction.atomic
    def form_valid(self, form):
        """Process the checkout form, create booking, and initiate payment"""
        cart = self.request.session.get('booking_cart', {})
        if not cart:
            messages.error(self.request, "Your cart is empty")
            return redirect('items:item_list')

        try:
            # Get form data
            start_date = self.request.session.get('booking_start_date')
            end_date = self.request.session.get('booking_end_date')

            if not start_date or not end_date:
                messages.error(self.request, "Please select your hire dates first")
                return redirect('items:item_list')

            # Create booking
            booking = Booking.objects.create(
                customer_name=form.cleaned_data['customer_name'],
                customer_email=form.cleaned_data['customer_email'],
                customer_phone=form.cleaned_data['customer_phone'],
                customer_address=form.cleaned_data['customer_address'],
                notes=form.cleaned_data.get('notes', ''),
                start_date=start_date,
                end_date=end_date,
                delivery_cost=Decimal('50')
            )

            subtotal = Decimal('0')
            for item_id, item_data in cart.items():
                item = HireItem.objects.get(id=item_id)
                start = datetime.strptime(item_data['start_date'], '%Y-%m-%d')
                end = datetime.strptime(item_data['end_date'], '%Y-%m-%d')
                days = (end - start).days + 1

                item_total = item.calculate_total_price(item_data['quantity'], start, end)
                subtotal += item_total

                BookingItem.objects.create(
                    booking=booking,
                    item=item,
                    quantity=item_data['quantity'],
                    price_per_day=item.price,
                    number_of_days=days,
                    total_price=item_total
                )

                # Mark dates as unavailable
                current = start
                while current <= end:
                    ItemAvailability.objects.get_or_create(
                        item=item,
                        date=current.date(),
                        defaults={'is_booked': True, 'quantity_booked': 1}
                    )
                    current += timedelta(days=1)

            booking.subtotal = subtotal
            booking.calculate_total()
            booking.save()

            # Store booking in session for payment
            self.request.session['pending_booking_id'] = booking.id
            self.request.session['booking_email'] = booking.customer_email

            # Clear cart
            del self.request.session['booking_cart']

            # Create payment record
            payment = Payment.objects.create(
                variant='paypal',
                description=f"Booking {booking.booking_number} - Deposit",
                total=booking.deposit_amount,
                currency='AUD',
                delivery=booking.delivery_cost,
                billing_first_name=booking.customer_name.split()[0] if booking.customer_name else '',
                billing_last_name=booking.customer_name.split()[-1] if len(booking.customer_name.split()) > 1 else '',
                billing_email=booking.customer_email,
            )

            # Store payment ID in session
            self.request.session['payment_id'] = payment.id

            # Redirect to payment processing
            return redirect('checkout:process_payment', payment_id=payment.id)

        except Exception as e:
            logger.error(f"Checkout error: {str(e)}")
            messages.error(self.request, f"Error processing checkout: {str(e)}")
            return redirect('bookings:cart')

    def form_invalid(self, form):
        """Handle invalid form"""
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(self.request, f"{field}: {error}")
        return super().form_invalid(form)


def process_payment(request, payment_id):
    """Process payment"""
    payment = get_object_or_404(Payment, id=payment_id)

    try:
        return redirect(payment.get_process_url())
    except RedirectNeeded as redirect_to:
        return redirect(str(redirect_to))
    except Exception as e:
        logger.error(f"Payment processing error: {str(e)}")
        messages.error(request, "Error processing payment. Please try again.")
        return redirect('checkout:checkout')


def payment_success(request):
    """Handle successful payment"""
    payment_id = request.GET.get('payment_id')
    if not payment_id:
        messages.error(request, "Invalid payment response")
        return redirect('home')

    try:
        payment = Payment.objects.get(id=payment_id)
        booking_id = request.session.get('pending_booking_id')
        booking = get_object_or_404(Booking, id=booking_id)

        # Update payment status
        payment.status = 'confirmed'
        payment.save()

        # Update booking
        booking.deposit_paid = True
        booking.status = 'deposit_paid'
        booking.stripe_payment_intent_id = payment.transaction_id or ''
        booking.save()

        # Generate invoice
        try:
            from apps.bookings.invoice import generate_booking_invoice
            invoice_path = generate_booking_invoice(booking)
        except Exception as e:
            logger.warning(f"Invoice generation failed: {e}")

        # Clear session
        if 'pending_booking_id' in request.session:
            del request.session['pending_booking_id']
        if 'booking_email' in request.session:
            del request.session['booking_email']
        if 'payment_id' in request.session:
            del request.session['payment_id']

        messages.success(request, f"Payment successful! Your booking {booking.booking_number} is confirmed.")
        return redirect('bookings:booking_success', booking_number=booking.booking_number)

    except Exception as e:
        logger.error(f"Payment success error: {str(e)}")
        messages.error(request, "Error processing payment confirmation")
        return redirect('home')


def payment_cancel(request):
    """Handle cancelled payment"""
    messages.warning(request, "Payment was cancelled. You can try again when ready.")
    return redirect('bookings:cart')
