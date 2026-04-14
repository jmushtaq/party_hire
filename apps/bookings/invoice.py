from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from django.conf import settings
from django.utils import timezone
import os

def generate_booking_invoice(booking):
    """Generate PDF invoice for a booking"""
    filename = f"invoice_{booking.booking_number}_{timezone.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    filepath = os.path.join(settings.MEDIA_ROOT, 'invoices', filename)
    os.makedirs(os.path.dirname(filepath), exist_ok=True)

    doc = SimpleDocTemplate(filepath, pagesize=A4)
    styles = getSampleStyleSheet()
    story = []

    # Title style
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#2563eb'),
        spaceAfter=30
    )

    # Header
    story.append(Paragraph("Party Hire - Tax Invoice", title_style))
    story.append(Spacer(1, 0.2 * inch))

    # Invoice details
    info_style = styles['Normal']
    story.append(Paragraph(f"<b>Invoice Number:</b> INV-{booking.booking_number}", info_style))
    story.append(Paragraph(f"<b>Date:</b> {timezone.now().strftime('%Y-%m-%d')}", info_style))
    story.append(Paragraph(f"<b>Booking Number:</b> {booking.booking_number}", info_style))
    story.append(Spacer(1, 0.2 * inch))

    # Customer details
    story.append(Paragraph("<b>Customer Details:</b>", info_style))
    story.append(Paragraph(f"Name: {booking.customer_name}", info_style))
    story.append(Paragraph(f"Email: {booking.customer_email}", info_style))
    story.append(Paragraph(f"Phone: {booking.customer_phone}", info_style))
    story.append(Paragraph(f"Address: {booking.customer_address}", info_style))
    story.append(Spacer(1, 0.2 * inch))

    # Hire period
    story.append(Paragraph("<b>Hire Period:</b>", info_style))
    story.append(Paragraph(f"Start Date: {booking.start_date}", info_style))
    story.append(Paragraph(f"End Date: {booking.end_date}", info_style))
    story.append(Spacer(1, 0.2 * inch))

    # Items table
    data = [['Item', 'Quantity', 'Days', 'Unit Price', 'Total']]
    for item in booking.items.all():
        data.append([
            item.item.name,
            str(item.quantity),
            str(item.number_of_days),
            f"${item.price_per_day:.2f}",
            f"${item.total_price:.2f}"
        ])

    table = Table(data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    story.append(table)
    story.append(Spacer(1, 0.2 * inch))

    # Totals
    story.append(Paragraph(f"<b>Subtotal:</b> ${booking.subtotal:.2f}", info_style))
    story.append(Paragraph(f"<b>Delivery:</b> ${booking.delivery_cost:.2f}", info_style))
    story.append(Paragraph(f"<b>Total Amount:</b> ${booking.total_amount:.2f}", info_style))
    story.append(Paragraph(f"<b>Deposit Paid:</b> ${booking.deposit_amount:.2f}", info_style))

    remaining = booking.total_amount - booking.deposit_amount
    story.append(Paragraph(f"<b>Balance Due:</b> ${remaining:.2f}", info_style))
    story.append(Spacer(1, 0.3 * inch))

    # Footer
    story.append(Paragraph("<b>Payment Instructions:</b>", info_style))
    story.append(Paragraph("Balance is due before delivery. Payment can be made via bank transfer or credit card.", info_style))

    doc.build(story)
    return filepath
