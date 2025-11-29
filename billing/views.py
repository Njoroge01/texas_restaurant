from django.shortcuts import render, get_object_or_404
from .models import Invoice


def view_receipt(request, invoice_id):
    invoice = get_object_or_404(Invoice, id=invoice_id)
    order = invoice.order
    items = order.orderitem_set.all()
    return render(request, 'billing/receipt.html', {
        'invoice': invoice,
        'order': order,
        'items': items,
    })

from django.http import HttpResponse
from django.conf import settings
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
import os

def download_receipt(request, invoice_id):
    from .models import Invoice
    invoice = Invoice.objects.get(id=invoice_id)
    order = invoice.order
    items = order.orderitem_set.all()

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="Invoice_{invoice.invoice_number}.pdf"'

    p = canvas.Canvas(response, pagesize=letter)
    width, height = letter

    # --- Logo Section ---
    logo_path = os.path.join(settings.BASE_DIR, 'static', 'images', 'logo.png')
    if os.path.exists(logo_path):
        p.drawImage(logo_path, 60, height - 120, width=100, height=60, preserveAspectRatio=True)

    # --- Title Section ---
    p.setFont("Helvetica-Bold", 18)
    p.drawCentredString(width / 2 + 50, height - 80, "Texas Restaurant")
    p.setFont("Helvetica", 12)
    p.drawCentredString(width / 2 + 50, height - 100, f"Invoice No: {invoice.invoice_number}")

    # --- Invoice details ---
    y = height - 160
    p.setFont("Helvetica", 10)
    p.drawString(60, y, f"Date: {invoice.date_issued.strftime('%Y-%m-%d %H:%M')}")
    p.drawString(60, y - 15, f"Customer: {order.customer.name}")
    p.drawString(60, y - 30, f"Payment Method: {invoice.payment_method}")

    # --- Table Header ---
    y -= 60
    p.setFont("Helvetica-Bold", 11)
    p.drawString(60, y, "Item")
    p.drawString(250, y, "Qty")
    p.drawString(300, y, "Price")
    p.drawString(400, y, "Subtotal")
    p.line(60, y - 5, 500, y - 5)
    y -= 20

    # --- Table Rows ---
    p.setFont("Helvetica", 10)
    for item in items:
        p.drawString(60, y, item.menu_item.name)
        p.drawString(250, y, str(item.quantity))
        p.drawString(300, y, f"{item.menu_item.price:.2f}")
        p.drawString(400, y, f"{item.subtotal():.2f}")
        y -= 15
        if y < 100:
            p.showPage()
            y = height - 100

    # --- Total ---
    y -= 20
    p.line(60, y, 500, y)
    p.setFont("Helvetica-Bold", 12)
    p.drawRightString(500, y - 25, f"Total: Ksh {order.total_amount:.2f}")

    # --- Footer ---
    p.setFont("Helvetica-Oblique", 10)
    p.drawCentredString(width / 2, 50, "Thank you for dining with us!")

    p.showPage()
    p.save()
    return response
from django.http import HttpResponse
from django.template.loader import render_to_string
import pdfkit  # make sure to install this later

def download_receipt(request, invoice_id):
    invoice = Invoice.objects.get(id=invoice_id)
    html = render_to_string('billing/receipt.html', {'invoice': invoice})
    pdf = pdfkit.from_string(html, False)
    response = HttpResponse(pdf, content_type='application/pdf')
    filename = f"Receipt_{invoice.invoice_number}.pdf"
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response
