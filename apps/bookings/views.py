from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils import timezone
from decimal import Decimal
from .models import Booking, BookingItem
from apps.items.models import HireItem, ItemAvailability
import stripe
from datetime import datetime, timedelta

stripe.api_key = settings.STRIPE_SECRET_KEY

def booking_cart(request):
    cart = request.session.get('booking_cart', {})
    items = []
    total = Decimal('0')

    for item_id, item_data in cart.items():
        item = HireItem.objects.get(id=item_id)
        days = (datetime.strptime(item_data['end_date'], '%Y-%m-%d') -
                datetime.strptime(item_data['start_date'], '%Y-%m-%d')).days + 1
        item_total = item.price_per_day * item_data['quantity'] * days
        total += item_total
        items.append({
            'item': item,
            'quantity': item_data['quantity'],
            'start_date': item_data['start_date'],
            'end_date': item_data['end_date'],
            'days': days,
            'total': item_total
        })

    delivery_cost = Decimal('50') if total > 0 else Decimal('0')
    grand_total = total + delivery_cost
    deposit = grand_total * Decimal('0.3')

    return render(request, 'bookings/cart.html', {
        'items': items,
        'subtotal': total,
        'delivery_cost': delivery_cost,
        'total': grand_total,
        'deposit': deposit
    })

def add_to_cart(request, item_id):
    item = get_object_or_404(HireItem, id=item_id)

    if request.method == 'POST':
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        quantity = int(request.POST.get('quantity', 1))

        # Check availability
        start = datetime.strptime(start_date, '%Y-%m-%d')
        end = datetime.strptime(end_date, '%Y-%m-%d')

        current_date = start
        while current_date <= end:
            if ItemAvailability.objects.filter(item=item, date=current_date, is_booked=True).exists():
                messages.error(request, f"Item not available on {current_date.strftime('%Y-%m-%d')}")
                return redirect('items:item_detail', slug=item.slug)
            current_date += timedelta(days=1)

        cart = request.session.get('booking_cart', {})
        cart[str(item_id)] = {
            'quantity': quantity,
            'start_date': start_date,
            'end_date': end_date
        }
        request.session['booking_cart'] = cart
        messages.success(request, f"{item.name} added to cart")

    return redirect('bookings:cart')

def checkout(request):
    if request.method == 'POST':
        cart = request.session.get('booking_cart', {})
        if not cart:
            return redirect('items:item_list')

        # Create booking
        booking = Booking.objects.create(
            customer_name=request.POST.get('name'),
            customer_email=request.POST.get('email'),
            customer_phone=request.POST.get('phone'),
            customer_address=request.POST.get('address'),
            start_date=request.POST.get('start_date'),
            end_date=request.POST.get('end_date'),
            delivery_cost=Decimal('50')
        )

        subtotal = Decimal('0')
        for item_id, item_data in cart.items():
            item = HireItem.objects.get(id=item_id)
            days = (datetime.strptime(item_data['end_date'], '%Y-%m-%d') -
                    datetime.strptime(item_data['start_date'], '%Y-%m-%d')).days + 1
            item_total = item.price_per_day * item_data['quantity'] * days
            subtotal += item_total

            BookingItem.objects.create(
                booking=booking,
                item=item,
                quantity=item_data['quantity'],
                price_per_day=item.price_per_day,
                number_of_days=days,
                total_price=item_total
            )

            # Mark dates as unavailable
            start = datetime.strptime(item_data['start_date'], '%Y-%m-%d')
            end = datetime.strptime(item_data['end_date'], '%Y-%m-%d')
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

        # Create Stripe payment intent
        intent = stripe.PaymentIntent.create(
            amount=int(booking.deposit_amount * 100),
            currency='aud',
            metadata={'booking_id': booking.id}
        )

        # Clear cart
        del request.session['booking_cart']

        # Send email notification
        send_booking_confirmation_email(booking)

        return render(request, 'bookings/payment.html', {
            'booking': booking,
            'client_secret': intent.client_secret,
            'stripe_public_key': settings.STRIPE_PUBLIC_KEY
        })

    return render(request, 'bookings/checkout.html')

def send_booking_confirmation_email(booking):
    subject = f"Booking Confirmation - {booking.booking_number}"
    html_message = render_to_string('emails/booking_confirmation.html', {'booking': booking})
    plain_message = f"Thank you for your booking. Your booking number is {booking.booking_number}"

    send_mail(
        subject,
        plain_message,
        settings.DEFAULT_FROM_EMAIL,
        [booking.customer_email],
        html_message=html_message,
        fail_silently=False,
    )

def booking_success(request, booking_number):
    booking = get_object_or_404(Booking, booking_number=booking_number)
    return render(request, 'bookings/booking_success.html', {'booking': booking})
