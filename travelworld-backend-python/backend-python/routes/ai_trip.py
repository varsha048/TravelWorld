import os
import json
from flask import Blueprint, request, jsonify
from auth_utils import token_required
from extensions import db, limiter
from google import genai
from google.genai import types

ai_trip_bp = Blueprint("ai_trip", __name__)

@ai_trip_bp.route("/generate", methods=["POST"])
@token_required
@limiter.limit("5 per day")
def generate_trip():
    data = request.get_json()
    destination = data.get("destination")
    days = data.get("days", 3)
    budget = data.get("budget", "medium")
    interests = data.get("interests", "general")
    
    if not destination:
        return jsonify(status="fail", message="Destination is required"), 400
        
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        return jsonify(status="fail", message="Gemini API Key not configured"), 500
        
    client = genai.Client(api_key=api_key)
    
    prompt = f"""
    Create a {days}-day travel itinerary for {destination}.
    Budget: {budget}.
    Interests: {interests}.
    
    Format the response as JSON with the following structure:
    {{
        "title": "A catchy title for the trip",
        "description": "A short summary",
        "itinerary": [
            {{
                "day": 1,
                "activities": ["Activity 1", "Activity 2"]
            }}
        ],
        "estimated_cost_usd": 500
    }}
    
    Ensure the JSON is valid and return ONLY the JSON, nothing else.
    """
    
    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
        )
        
        # Parse the JSON from the response text
        text = response.text.strip()
        if text.startswith("```json"):
            text = text[7:]
        if text.endswith("```"):
            text = text[:-3]
            
        trip_data = json.loads(text.strip())
        return jsonify(status="success", data=trip_data), 200
        
    except Exception as e:
        return jsonify(status="fail", message=str(e)), 500

@ai_trip_bp.route("/email", methods=["POST"])
def email_trip():
    data = request.get_json()
    email_address = data.get("email")
    trip_data = data.get("trip")
    
    if not email_address or not trip_data:
        return jsonify(status="fail", message="Email and trip data are required"), 400
        
    mail_user = os.environ.get("MAIL_USERNAME")
    mail_pass = os.environ.get("MAIL_PASSWORD")
    
    if not mail_user or not mail_pass:
        return jsonify(status="fail", message="Email configuration is missing on the server"), 500
        
    import smtplib
    from email.message import EmailMessage
    
    try:
        title = trip_data.get("title", "Your Custom Itinerary")
        desc = trip_data.get("description", "")
        cost = trip_data.get("estimated_cost_usd", "0")
        
        # Build HTML content
        days_html = ""
        for day in trip_data.get("itinerary", []):
            activities_html = "".join([f"<li>{act}</li>" for act in day.get("activities", [])])
            days_html += f"<h3>Day {day.get('day')}</h3><ul>{activities_html}</ul>"
            
        full_html = f"""
        <html>
          <body style="font-family: Arial, sans-serif; color: #333; line-height: 1.6; max-width: 600px; margin: 0 auto; padding: 20px;">
            <div style="background-color: #a855f7; padding: 20px; text-align: center; border-radius: 8px 8px 0 0;">
              <h1 style="color: white; margin: 0;">{title} ✈️</h1>
            </div>
            <div style="padding: 20px; border: 1px solid #eee; border-top: none; border-radius: 0 0 8px 8px;">
              <p style="font-size: 16px; color: #555;">{desc}</p>
              {days_html}
              <div style="margin-top: 20px; padding: 15px; background: #f3e8ff; border-radius: 8px; text-align: center;">
                  <h3 style="color: #a855f7; margin: 0;">Estimated Cost: Rs.{cost}</h3>
              </div>
              <br/>
              <hr style="border: none; border-top: 1px solid #eee; margin: 20px 0;"/>
              <p style="text-align: center; font-size: 14px; color: #888;">
                Ready to book? Visit TravelWorld today!
              </p>
            </div>
          </body>
        </html>
        """
        
        msg = EmailMessage()
        msg['Subject'] = f"{title} - Your TravelWorld Itinerary 🌍"
        msg['From'] = mail_user
        msg['To'] = email_address
        msg.set_content(f"Your itinerary is ready! Please view this email in an HTML-compatible client.")
        msg.add_alternative(full_html, subtype='html')
        
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(mail_user, mail_pass)
            smtp.send_message(msg)
            
        return jsonify(status="success", message="Email sent successfully!"), 200
        
    except Exception as e:
        return jsonify(status="fail", message=str(e)), 500
