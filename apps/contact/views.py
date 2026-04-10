from django.shortcuts import render, redirect
from django.core.mail import send_mail
from django.contrib import messages
from django.conf import settings
from django.template.loader import render_to_string

def contact_view(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        subject = request.POST.get('subject')
        message = request.POST.get('message')

        # Send email
        email_subject = f"Contact Form: {subject}"
        email_body = render_to_string('emails/contact_email.html', {
            'name': name,
            'email': email,
            'phone': phone,
            'message': message
        })

        send_mail(
            email_subject,
            '',
            settings.DEFAULT_FROM_EMAIL,
            [settings.EMAIL_HOST_USER],
            html_message=email_body,
            fail_silently=False,
        )

        # Send auto-reply to customer
        send_mail(
            "Thank you for contacting us",
            render_to_string('emails/contact_auto_reply.txt', {'name': name}),
            settings.DEFAULT_FROM_EMAIL,
            [email],
            fail_silently=False,
        )

        messages.success(request, "Thank you for your message. We'll get back to you soon!")
        return redirect('contact:contact')

    return render(request, 'contact/contact.html')
