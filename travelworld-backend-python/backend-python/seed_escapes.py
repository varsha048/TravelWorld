import os
from datetime import date
from app import create_app
from extensions import db
from models import NextEscape

def seed():
    app = create_app()
    with app.app_context():
        # Drop and recreate tables to apply schema changes
        from models import EscapeBooking
        EscapeBooking.__table__.drop(db.engine, checkfirst=True)
        NextEscape.__table__.drop(db.engine, checkfirst=True)
        db.create_all()
        
        itinerary_goa = "Day 1: Arrival at Dabolim Airport, transfer to resort in Calangute. Evening welcome dinner by the beach with live music.<br>Day 2: Morning watersports at Baga Beach (Parasailing, Jet Ski). Afternoon visit to Aguada Fort. Sunset cruise on the Mandovi River.<br>Day 3: Explore Old Goa (Basilica of Bom Jesus, Se Cathedral). Authentic Goan fish thali lunch. Evening leisure at Anjuna flea market.<br>Day 4: Morning Yoga session. Breakfast, check-out, and airport drop."
        
        itinerary_maldives = "Day 1: Arrival at Male International Airport. Scenic seaplane transfer to your private water villa. Evening leisure.<br>Day 2: Morning guided snorkeling session at the house reef. Afternoon Balinese spa treatment. Sunset dolphin cruise.<br>Day 3: Full day island hopping. Special Diwali Gala Dinner on a private sandbank with traditional Indian sweets and fireworks.<br>Day 4: Free day for scuba diving or relaxing by the infinity pool. Evening sunset fishing experience.<br>Day 5: Check-out and speedboat transfer back to Male for departure."
        
        itinerary_swiss = "Day 1: Arrival in Zurich. Train transfer to Lucerne. Check-in to hotel overlooking Lake Lucerne. Evening walk across the Chapel Bridge.<br>Day 2: Full day excursion to Mount Titlis via rotating cable car. Experience the Ice Flyer and Glacier Cave. Return to Lucerne.<br>Day 3: Transfer to Interlaken. Explore the charming town. Special Christmas Eve dinner with traditional fondue.<br>Day 4: Scenic Alpine train ride on the GoldenPass line to Montreux. Visit Chillon Castle on Lake Geneva.<br>Day 5: Train transfer to Geneva airport for departure."
        
        itinerary_generic = "Day 1: Airport arrival and VIP transfer to your premium hotel. Welcome briefing and evening at leisure.<br>Day 2: Comprehensive guided city tour covering top historical and cultural landmarks. Authentic local cuisine for dinner.<br>Day 3: Day trip to a nearby scenic attraction or nature reserve. Optional adventure activities. Evening shopping.<br>Day 4: Final breakfast, hotel check-out, and comfortable transfer to the airport for your onward journey."

        escapes_data = [
            {"title": "Independence Day Goa Retreat", "city": "Goa", "photo": "images/tour-img01.jpg", "desc": "Enjoy a 4-day long weekend in Goa.", "price": 499, "start": date(2026, 8, 14), "end": date(2026, 8, 17), "itinerary": itinerary_goa},
            {"title": "Diwali Maldives Escape", "city": "Maldives", "photo": "images/tour-img02.jpg", "desc": "Celebrate Diwali in the Maldives.", "price": 1299, "start": date(2026, 11, 6), "end": date(2026, 11, 10), "itinerary": itinerary_maldives},
            {"title": "Christmas in Swiss Alps", "city": "Switzerland", "photo": "images/tour-img03.jpg", "desc": "A magical snowy Christmas.", "price": 1599, "start": date(2026, 12, 23), "end": date(2026, 12, 27), "itinerary": itinerary_swiss},
            {"title": "New Year Dubai Bash", "city": "Dubai", "photo": "images/tour-img04.jpg", "desc": "Ring in the new year in style.", "price": 899, "start": date(2026, 12, 30), "end": date(2027, 1, 3), "itinerary": itinerary_generic},
            {"title": "Republic Day Rajasthan Tour", "city": "Rajasthan", "photo": "images/tour-img05.jpg", "desc": "Explore forts and palaces.", "price": 399, "start": date(2027, 1, 23), "end": date(2027, 1, 26), "itinerary": itinerary_generic},
            {"title": "Holi in Mathura", "city": "Mathura", "photo": "images/tour-img06.jpg", "desc": "Experience the festival of colors.", "price": 299, "start": date(2027, 3, 20), "end": date(2027, 3, 23), "itinerary": itinerary_generic},
            {"title": "Good Friday Kerala Backwaters", "city": "Kerala", "photo": "images/tour-img07.jpg", "desc": "Relaxing long weekend on a houseboat.", "price": 450, "start": date(2027, 4, 15), "end": date(2027, 4, 18), "itinerary": itinerary_generic},
            {"title": "Labor Day Bali Trip", "city": "Bali", "photo": "images/tour-img08.jpg", "desc": "Tropical island getaway.", "price": 950, "start": date(2027, 4, 30), "end": date(2027, 5, 3), "itinerary": itinerary_generic},
            {"title": "Summer Break Europe Eurotrip", "city": "Europe", "photo": "images/tour-img09.jpg", "desc": "Multi-city European adventure.", "price": 2500, "start": date(2027, 6, 15), "end": date(2027, 6, 25), "itinerary": itinerary_generic},
            {"title": "Monsoon Trek in Sahyadris", "city": "Maharashtra", "photo": "images/tour-img10.jpg", "desc": "Weekend trekking adventure.", "price": 150, "start": date(2027, 7, 10), "end": date(2027, 7, 12), "itinerary": itinerary_generic},
            {"title": "Raksha Bandhan Rishikesh Rafting", "city": "Rishikesh", "photo": "images/tour-img01.jpg", "desc": "Adventure sports weekend.", "price": 250, "start": date(2027, 8, 14), "end": date(2027, 8, 16), "itinerary": itinerary_generic},
            {"title": "Gandhi Jayanti Bhutan Peace Tour", "city": "Bhutan", "photo": "images/tour-img02.jpg", "desc": "Spiritual and peaceful long weekend.", "price": 600, "start": date(2027, 10, 1), "end": date(2027, 10, 4), "itinerary": itinerary_generic},
            {"title": "Dussehra Mysore Palace Visit", "city": "Mysore", "photo": "images/tour-img03.jpg", "desc": "Witness the grand Dasara festival.", "price": 350, "start": date(2027, 10, 20), "end": date(2027, 10, 24), "itinerary": itinerary_generic},
            {"title": "Thanksgiving NYC Shopping", "city": "New York", "photo": "images/tour-img04.jpg", "desc": "Black Friday shopping spree.", "price": 1800, "start": date(2027, 11, 24), "end": date(2027, 11, 28), "itinerary": itinerary_generic},
            {"title": "Winter Solstice Iceland Auroras", "city": "Iceland", "photo": "images/tour-img05.jpg", "desc": "Northern lights chasing.", "price": 2200, "start": date(2027, 12, 18), "end": date(2027, 12, 22), "itinerary": itinerary_generic},
        ]
        
        for e in escapes_data:
            escape = NextEscape(
                title=e["title"],
                city=e["city"],
                photo=e["photo"],
                desc=e["desc"],
                itinerary=e["itinerary"],
                price=e["price"],
                start_date=e["start"],
                end_date=e["end"],
                total_slots=20,
                booked_slots=0
            )
            db.session.add(escape)
            
        db.session.commit()
        print("Successfully seeded 15 Next Escapes!")

if __name__ == "__main__":
    seed()
