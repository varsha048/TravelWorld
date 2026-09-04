import os
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors

def generate_ticket_pdf(booking, tour, app_static_folder):
    """
    Generates a PDF ticket for a booking and saves it to the static folder.
    Returns the path to the generated PDF.
    """
    tickets_dir = os.path.join(app_static_folder, 'tickets')
    if not os.path.exists(tickets_dir):
        os.makedirs(tickets_dir)
        
    filename = f"ticket_{booking.id}.pdf"
    filepath = os.path.join(tickets_dir, filename)
    
    # Create the PDF
    c = canvas.Canvas(filepath, pagesize=letter)
    width, height = letter
    
    # Draw Background/Header
    c.setFillColor(colors.HexColor("#f7a72d"))
    c.rect(0, height - 120, width, 120, fill=True, stroke=False)
    
    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", 36)
    c.drawString(40, height - 60, "TRAVELWORLD")
    
    c.setFont("Helvetica", 14)
    c.drawString(40, height - 90, "E-TICKET CONFIRMATION")
    
    # Draw Booking Info
    c.setFillColor(colors.black)
    c.setFont("Helvetica-Bold", 20)
    c.drawString(40, height - 160, f"Tour: {tour.title}")
    
    c.setFont("Helvetica", 14)
    c.drawString(40, height - 200, f"Booking ID: #{booking.id:06d}")
    c.drawString(40, height - 230, f"Guest Name: {booking.guest_name}")
    c.drawString(40, height - 260, f"Travel Date: {booking.date.strftime('%Y-%m-%d') if hasattr(booking.date, 'strftime') else str(booking.date)}")
    c.drawString(40, height - 290, f"Guests: {booking.guests_count}")
    
    # Total Price
    c.setFont("Helvetica-Bold", 16)
    c.drawString(40, height - 340, f"Total Paid: Rs. {booking.total_price}")
    
    # Draw a mock QR code (just a square with text)
    c.rect(width - 150, height - 280, 100, 100, fill=False, stroke=True)
    c.setFont("Helvetica", 10)
    c.drawString(width - 140, height - 235, "VALID TICKET")
    
    # Footer
    c.setFont("Helvetica-Oblique", 12)
    c.setFillColor(colors.gray)
    c.drawString(40, 50, "Thank you for booking with TravelWorld. Have a great trip!")
    
    c.save()
    return filepath
