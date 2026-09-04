import os
import smtplib
from email.message import EmailMessage
import requests
import markdown

def generate_and_send_tour_package(email: str, destination: str):
    """
    Background worker function that generates a detailed tour package using Gemini
    and sends it via email.
    """
    api_key = os.getenv("GEMINI_API_KEY")
    mail_user = os.getenv("MAIL_USERNAME")
    mail_pass = os.getenv("MAIL_PASSWORD")

    if not api_key or api_key == "your_key_here":
        print("[EmailService] No GEMINI_API_KEY found, aborting.")
        return

    # 1. Generate the detailed tour package
    try:
        print(f"[EmailService] Generating tour package for {destination}...")
        prompt = (
            f"Write a highly detailed and enticing 3-day travel itinerary for {destination}. "
            "Format it nicely in Markdown with headers, bullet points, and excitement. "
            "Address it directly to the traveler. "
            "Include recommendations for morning, afternoon, and evening activities."
        )
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"temperature": 0.7}
        }
        res = requests.post(url, json=payload, timeout=60)
        res.raise_for_status()
        
        response_data = res.json()
        markdown_content = response_data.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "").strip()
    except Exception as e:
        print(f"[EmailService] Error generating content: {e}")
        return

    # Convert markdown to HTML for the email
    html_content = markdown.markdown(markdown_content)

    # Wrap in a basic HTML template
    full_html = f"""
    <html>
      <body style="font-family: Arial, sans-serif; color: #333; line-height: 1.6; max-width: 600px; margin: 0 auto; padding: 20px;">
        <div style="background-color: #f7a72d; padding: 20px; text-align: center; border-radius: 8px 8px 0 0;">
          <h1 style="color: white; margin: 0;">Your Dream Trip to {destination}! ✈️</h1>
        </div>
        <div style="padding: 20px; border: 1px solid #eee; border-top: none; border-radius: 0 0 8px 8px;">
          {html_content}
          <br/>
          <hr style="border: none; border-top: 1px solid #eee; margin: 20px 0;"/>
          <p style="text-align: center; font-size: 14px; color: #888;">
            Ready to book? Visit TravelWorld today!
          </p>
        </div>
      </body>
    </html>
    """

    # 2. Send the email
    if not mail_user or not mail_pass:
        print(f"[EmailService] Missing MAIL_USERNAME or MAIL_PASSWORD in .env.")
        print(f"[EmailService] Generated Email for {email} but NOT sent.")
        # Save to file for debugging
        with open("mock_email.html", "w", encoding="utf-8") as f:
            f.write(full_html)
        print("[EmailService] Saved mockup to mock_email.html")
        return

    try:
        print(f"[EmailService] Sending email to {email}...")
        msg = EmailMessage()
        msg['Subject'] = f"Your Detailed Tour Package for {destination} 🌍"
        msg['From'] = mail_user
        msg['To'] = email
        msg.set_content(f"Your itinerary for {destination} is ready! Please view this email in an HTML-compatible client.")
        msg.add_alternative(full_html, subtype='html')

        # Use Gmail's SMTP server
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(mail_user, mail_pass)
            smtp.send_message(msg)
            
        print(f"[EmailService] Successfully sent email to {email}!")
    except Exception as e:
        print(f"[EmailService] Failed to send email: {e}")


def send_booking_email(email: str, username: str, tour_title: str, ticket_url: str):
    """
    Sends a booking confirmation email with the ticket URL.
    """
    mail_user = os.getenv("MAIL_USERNAME")
    mail_pass = os.getenv("MAIL_PASSWORD")

    html_content = f"""
    <html>
      <body style="font-family: Arial, sans-serif; color: #333; line-height: 1.6; max-width: 600px; margin: 0 auto; padding: 20px;">
        <div style="background-color: #27ae60; padding: 20px; text-align: center; border-radius: 8px 8px 0 0;">
          <h1 style="color: white; margin: 0;">Booking Confirmed! 🎉</h1>
        </div>
        <div style="padding: 20px; border: 1px solid #eee; border-top: none; border-radius: 0 0 8px 8px;">
          <h2>Hi {username},</h2>
          <p>Your payment for <strong>{tour_title}</strong> was successful!</p>
          <p>You can view and download your PDF ticket here:</p>
          <p><a href="{ticket_url}" style="display:inline-block; padding:10px 20px; background:#f97316; color:white; text-decoration:none; border-radius:5px;">Download Ticket</a></p>
          <br/>
          <hr style="border: none; border-top: 1px solid #eee; margin: 20px 0;"/>
          <p style="text-align: center; font-size: 14px; color: #888;">
            Thank you for choosing TravelWorld!
          </p>
        </div>
      </body>
    </html>
    """

    if not mail_user or not mail_pass:
        print("[EmailService] Missing MAIL_USERNAME/PASSWORD. Mocking booking email.")
        with open("mock_booking_email.html", "w", encoding="utf-8") as f:
            f.write(html_content)
        return

    try:
        print(f"[EmailService] Sending booking email to {email}...")
        msg = EmailMessage()
        msg['Subject'] = f"Booking Confirmation: {tour_title} ✅"
        msg['From'] = mail_user
        msg['To'] = email
        msg.set_content(f"Hi {username}, your booking for {tour_title} is confirmed. View ticket: {ticket_url}")
        msg.add_alternative(html_content, subtype='html')

        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(mail_user, mail_pass)
            smtp.send_message(msg)
            
        print(f"[EmailService] Successfully sent booking email to {email}!")
    except Exception as e:
        print(f"[EmailService] Failed to send booking email: {e}")
