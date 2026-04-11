from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils import timezone
from django.http import JsonResponse
from decimal import Decimal
from .models import Booking, BookingItem
from apps.items.models import HireItem, ItemAvailability
import stripe
from datetime import datetime, timedelta
import json

stripe.api_key = settings.STRIPE_SECRET_KEY

def booking_cart(request):
    """Display shopping cart"""
    cart = request.session.get('booking_cart', {})
    items = []
    total = Decimal('0')

    for item_id, item_data in cart.items():
        try:
            item = HireItem.objects.get(id=item_id)
            start_date = item_data.get('start_date')
            end_date = item_data.get('end_date')

            if not start_date or not end_date:
                continue

            days = (datetime.strptime(end_date, '%Y-%m-%d') -
                    datetime.strptime(start_date, '%Y-%m-%d')).days + 1
            item_total = item.price_per_day * item_data['quantity'] * days
            total += item_total
            items.append({
                'item': item,
                'quantity': item_data['quantity'],
                'start_date': start_date,
                'end_date': end_date,
                'days': days,
                'total': item_total
            })
        except (KeyError, ValueError, HireItem.DoesNotExist):
            continue

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

def set_date_range(request):
    """Set the global date range and validate cart items"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            start_date = data.get('start_date')
            end_date = data.get('end_date')

            if start_date and end_date:
                start = datetime.strptime(start_date, '%Y-%m-%d')
                end = datetime.strptime(end_date, '%Y-%m-%d')

                if start.date() < timezone.now().date():
                    return JsonResponse({'success': False, 'error': 'Start date cannot be in the past'})

                if end < start:
                    return JsonResponse({'success': False, 'error': 'End date must be after start date'})

                # Store dates in session
                request.session['booking_start_date'] = start_date
                request.session['booking_end_date'] = end_date

                # Validate and update cart items
                cart = request.session.get('booking_cart', {})
                items_to_remove = []

                for item_id, item_data in cart.items():
                    item = HireItem.objects.get(id=item_id)
                    current_date = start
                    is_available = True

                    while current_date <= end:
                        if ItemAvailability.objects.filter(
                            item=item, date=current_date.date(), is_booked=True
                        ).exists():
                            is_available = False
                            break
                        current_date += timedelta(days=1)

                    if is_available:
                        # Update dates in cart
                        item_data['start_date'] = start_date
                        item_data['end_date'] = end_date
                        cart[item_id] = item_data
                    else:
                        items_to_remove.append({'id': item_id, 'name': item.name})
                        del cart[item_id]

                request.session['booking_cart'] = cart

                return JsonResponse({
                    'success': True,
                    'start_date': start_date,
                    'end_date': end_date,
                    'unavailable_items': items_to_remove,
                    'cart_count': len(cart)
                })

        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

    return JsonResponse({'success': False, 'error': 'Invalid request'})

def get_date_range(request):
    """Get the current date range from session"""
    start_date = request.session.get('booking_start_date')
    end_date = request.session.get('booking_end_date')

    # If no dates set, suggest next Thursday to Monday
    if not start_date or not end_date:
        today = timezone.now().date()
        # Find next Thursday
        days_until_thursday = (3 - today.weekday()) % 7
        if days_until_thursday == 0:
            days_until_thursday = 7
        start_date = (today + timedelta(days=days_until_thursday)).isoformat()
        # Monday is 4 days after Thursday
        end_date = (today + timedelta(days=days_until_thursday + 4)).isoformat()

    return JsonResponse({
        'start_date': start_date,
        'end_date': end_date
    })

def add_to_cart(request, item_id):
    """Add item to shopping cart with global date range"""
    item = get_object_or_404(HireItem, id=item_id)

    # Check if date range is set
    start_date = request.session.get('booking_start_date')
    end_date = request.session.get('booking_end_date')

    if not start_date or not end_date:
        messages.error(request, "Please select your hire dates first")
        return redirect('items:item_detail', slug=item.slug)

    if request.method == 'POST':
        quantity = request.POST.get('quantity', 1)

        try:
            quantity = int(quantity)
            if quantity < 1:
                quantity = 1
            if quantity > item.quantity_available:
                messages.error(request, f"Only {item.quantity_available} units available for {item.name}")
                return redirect('items:item_detail', slug=item.slug)

            # Check availability with global dates
            start = datetime.strptime(start_date, '%Y-%m-%d')
            end = datetime.strptime(end_date, '%Y-%m-%d')

            current_date = start
            unavailable_dates = []
            while current_date <= end:
                availability = ItemAvailability.objects.filter(
                    item=item,
                    date=current_date.date(),
                    is_booked=True
                ).exists()
                if availability:
                    unavailable_dates.append(current_date.strftime('%Y-%m-%d'))
                current_date += timedelta(days=1)

            if unavailable_dates:
                messages.error(
                    request,
                    f"{item.name} is not available on: {', '.join(unavailable_dates[:3])}"
                )
                return redirect('items:item_detail', slug=item.slug)

            # Add to cart
            cart = request.session.get('booking_cart', {})
            cart[str(item_id)] = {
                'quantity': quantity,
                'start_date': start_date,
                'end_date': end_date
            }
            request.session['booking_cart'] = cart

            messages.success(request, f"✓ {item.name} has been added to your cart!")
            return redirect('items:item_list')

        except ValueError as e:
            messages.error(request, f"Invalid quantity")
            return redirect('items:item_detail', slug=item.slug)

    return redirect('items:item_detail', slug=item.slug)

def update_cart_item(request, item_id):
    """Update quantity of item in cart"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            new_quantity = int(data.get('quantity', 1))

            cart = request.session.get('booking_cart', {})

            if str(item_id) in cart:
                item_data = cart[str(item_id)]

                # Validate quantity against available stock
                item = HireItem.objects.get(id=item_id)
                if new_quantity > item.quantity_available:
                    return JsonResponse({
                        'success': False,
                        'error': f'Only {item.quantity_available} units available'
                    })

                if new_quantity <= 0:
                    # Remove item if quantity is 0 or less
                    del cart[str(item_id)]
                else:
                    item_data['quantity'] = new_quantity
                    cart[str(item_id)] = item_data

                request.session['booking_cart'] = cart

                # Recalculate totals
                subtotal = Decimal('0')
                item_total_calc = Decimal('0')
                for item_id_str, item_data in cart.items():
                    cart_item = HireItem.objects.get(id=item_id_str)
                    days = (datetime.strptime(item_data['end_date'], '%Y-%m-%d') -
                            datetime.strptime(item_data['start_date'], '%Y-%m-%d')).days + 1
                    item_total = cart_item.price_per_day * item_data['quantity'] * days
                    subtotal += item_total

                    if int(item_id_str) == item_id:
                        item_total_calc = item_total

                delivery_cost = Decimal('50') if subtotal > 0 else Decimal('0')
                grand_total = subtotal + delivery_cost
                deposit = grand_total * Decimal('0.3')

                return JsonResponse({
                    'success': True,
                    'item_total': float(item_total_calc),
                    'subtotal': float(subtotal),
                    'grand_total': float(grand_total),
                    'deposit': float(deposit),
                    'cart_count': len(cart)
                })

            return JsonResponse({'success': False, 'error': 'Item not found in cart'})

        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

    return JsonResponse({'success': False, 'error': 'Invalid request method'})

def remove_from_cart(request, item_id):
    """Remove item from cart"""
    if request.method == 'POST':
        cart = request.session.get('booking_cart', {})

        if str(item_id) in cart:
            del cart[str(item_id)]
            request.session['booking_cart'] = cart

            # Recalculate totals
            subtotal = Decimal('0')
            for item_id_str, item_data in cart.items():
                item = HireItem.objects.get(id=item_id_str)
                days = (datetime.strptime(item_data['end_date'], '%Y-%m-%d') -
                        datetime.strptime(item_data['start_date'], '%Y-%m-%d')).days + 1
                item_total = item.price_per_day * item_data['quantity'] * days
                subtotal += item_total

            delivery_cost = Decimal('50') if subtotal > 0 else Decimal('0')
            grand_total = subtotal + delivery_cost
            deposit = grand_total * Decimal('0.3')

            return JsonResponse({
                'success': True,
                'subtotal': float(subtotal),
                'grand_total': float(grand_total),
                'deposit': float(deposit),
                'cart_count': len(cart)
            })

        return JsonResponse({'success': False, 'error': 'Item not found in cart'})

    return JsonResponse({'success': False, 'error': 'Invalid request method'})

def checkout(request):
    """Checkout process"""
    if request.method == 'POST':
        cart = request.session.get('booking_cart', {})
        if not cart:
            messages.error(request, "Your cart is empty")
            return redirect('items:item_list')

        try:
            # Get customer information
            customer_name = request.POST.get('name', '').strip()
            customer_email = request.POST.get('email', '').strip()
            customer_phone = request.POST.get('phone', '').strip()
            customer_address = request.POST.get('address', '').strip()
            start_date = request.session.get('booking_start_date')
            end_date = request.session.get('booking_end_date')

            # Validate required fields
            if not all([customer_name, customer_email, customer_phone, customer_address, start_date, end_date]):
                messages.error(request, "Please fill in all required fields")
                return render(request, 'bookings/checkout.html')

            # Create booking
            booking = Booking.objects.create(
                customer_name=customer_name,
                customer_email=customer_email,
                customer_phone=customer_phone,
                customer_address=customer_address,
                start_date=start_date,
                end_date=end_date,
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
            try:
                intent = stripe.PaymentIntent.create(
                    amount=int(booking.deposit_amount * 100),
                    currency='aud',
                    metadata={'booking_id': booking.id}
                )
                client_secret = intent.client_secret
            except Exception as e:
                # If Stripe fails, still create booking but mark as pending payment
                client_secret = None
                messages.warning(request, "Payment processing is not fully configured. Please contact us to complete your booking.")

            # Clear cart
            del request.session['booking_cart']

            # Send email notification
            try:
                send_booking_confirmation_email(booking)
            except Exception as e:
                print(f"Email error: {e}")

            if client_secret:
                return render(request, 'bookings/payment.html', {
                    'booking': booking,
                    'client_secret': client_secret,
                    'stripe_public_key': settings.STRIPE_PUBLIC_KEY
                })
            else:
                messages.info(request, f"Booking #{booking.booking_number} created. Please contact us to complete payment.")
                return redirect('bookings:booking_success', booking_number=booking.booking_number)

        except Exception as e:
            messages.error(request, f"Error creating booking: {str(e)}")
            return redirect('bookings:cart')

    # GET request - show checkout form
    cart = request.session.get('booking_cart', {})
    if not cart:
        messages.error(request, "Your cart is empty")
        return redirect('items:item_list')

    return render(request, 'bookings/checkout.html')

def booking_success(request, booking_number):
    """Display booking success page"""
    booking = get_object_or_404(Booking, booking_number=booking_number)
    return render(request, 'bookings/booking_success.html', {'booking': booking})

def send_booking_confirmation_email(booking):
    """Send booking confirmation email"""
    subject = f"Booking Confirmation - {booking.booking_number}"
    try:
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
    except Exception as e:
        print(f"Failed to send email: {e}")


def check_availability(request, item_id):
    """Check if an item is available for the selected dates"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            start_date = data.get('start_date')
            end_date = data.get('end_date')
            quantity = int(data.get('quantity', 1))

            item = get_object_or_404(HireItem, id=item_id)
            start = datetime.strptime(start_date, '%Y-%m-%d')
            end = datetime.strptime(end_date, '%Y-%m-%d')

            # Check each date in range
            unavailable_dates = []
            current_date = start
            while current_date <= end:
                availability = ItemAvailability.objects.filter(
                    item=item,
                    date=current_date.date(),
                    is_booked=True
                ).exists()
                if availability:
                    unavailable_dates.append(current_date.strftime('%Y-%m-%d'))
                current_date += timedelta(days=1)

            if unavailable_dates:
                return JsonResponse({
                    'available': False,
                    'message': f"Not available on: {', '.join(unavailable_dates[:3])}"
                })

            # Check quantity
            if quantity > item.quantity_available:
                return JsonResponse({
                    'available': False,
                    'message': f"Only {item.quantity_available} units available"
                })

            days = (end - start).days + 1
            total = item.price_per_day * quantity * days

            return JsonResponse({
                'available': True,
                'message': f"Available! Total: ${total:.2f} for {days} days"
            })

        except Exception as e:
            return JsonResponse({'available': False, 'message': str(e)})

    return JsonResponse({'available': False, 'message': 'Invalid request'})
