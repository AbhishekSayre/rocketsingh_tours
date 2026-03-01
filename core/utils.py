from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from django.http import HttpResponse
import io

def generate_booking_pdf(booking, travelers, tour):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    elements = []

    styles = getSampleStyleSheet()
    styleN = styles["Normal"]
    styleH = styles["Heading1"]

    # Header
    elements.append(Paragraph("Booking Confirmation", styleH))
    elements.append(Spacer(1, 12))

    # Tour Info
    elements.append(Paragraph(f"<b>Tour Name:</b> {tour.name}", styleN))
    elements.append(Paragraph(f"<b>Destination:</b> {tour.destination}", styleN))
    elements.append(Paragraph(f"<b>Duration:</b> {tour.duration}", styleN))
    elements.append(Paragraph(f"<b>Tour Date:</b> {booking.tour_date.strftime('%B %d, %Y')}", styleN))
    elements.append(Spacer(1, 12))

    # Booking Details
    elements.append(Paragraph("<b>Booking Details:</b>", styleN))
    elements.append(Paragraph(f"Booking ID: {booking.id}", styleN))
    elements.append(Paragraph(f"Number of Travelers: {booking.num_travelers}", styleN))
    elements.append(Paragraph(f"Special Request: {booking.special_request}", styleN))
    elements.append(Paragraph(f"Total Paid: ₹{booking.total_amount}", styleN))
    elements.append(Paragraph(f"Payment Status: {booking.payment_status}", styleN))
    elements.append(Paragraph(f"Booking Date: {booking.created_at.strftime('%d-%m-%Y')}", styleN))
    elements.append(Spacer(1, 12))

    # Travelers Table
    elements.append(Paragraph("<b>Traveler Details:</b>", styleN))
    data = [["Name", "Age", "Phone", "Email"]]
    for t in travelers:
        data.append([t.name, t.age, t.phone, t.email])

    table = Table(data, hAlign='LEFT')
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#01342F")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('INNERGRID', (0,0), (-1,-1), 0.25, colors.gray),
        ('BOX', (0,0), (-1,-1), 0.5, colors.gray),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
    ]))
    elements.append(table)
    elements.append(Spacer(1, 12))

    # Support Info
    elements.append(Paragraph("<b>Contact & Support</b>", styleN))
    elements.append(Paragraph("📞 Phone: +91 9876543210", styleN))
    elements.append(Paragraph("📧 Email: support@rocketsingh.com", styleN))
    elements.append(Paragraph("🏢 Address: 09, Nandanwan Street, Nagpur, India", styleN))

    doc.build(elements)
    buffer.seek(0)
    return buffer
    
