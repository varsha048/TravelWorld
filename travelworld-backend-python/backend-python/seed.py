from app import create_app
from extensions import db
from models import Tour, Review, User
import random

sample_tours = [
    dict(title="Bali Paradise Escape", city="Bali", photo="images/tour-img01.jpg",
         desc="Explore lush jungles, rice terraces, and pristine beaches.",
         price=799, distance=320, max_group_size=12, featured=True,
         itinerary="Day 1: Arrival in Bali, transfer to Ubud hotel.\nDay 2: Visit Tegalalang Rice Terrace and Sacred Monkey Forest.\nDay 3: Beach hopping in Seminyak and sunset at Tanah Lot.\nDay 4: Departure."),
    dict(title="Swiss Alps Adventure", city="Zermatt", photo="images/tour-img02.jpg",
         desc="Hike through breathtaking alpine trails and charming villages.",
         price=1299, distance=540, max_group_size=8, featured=True,
         itinerary="Day 1: Arrival in Geneva, train to Zermatt.\nDay 2: Guided hike with Matterhorn views.\nDay 3: Glacier Paradise cable car and ice palace.\nDay 4: Free day for skiing or relaxation.\nDay 5: Departure."),
    dict(title="Santorini Sunset Tour", city="Santorini", photo="images/tour-img03.jpg",
         desc="Watch iconic sunsets over whitewashed cliffside towns.",
         price=999, distance=410, max_group_size=10, featured=True,
         itinerary="Day 1: Arrival in Santorini, check-in at Oia.\nDay 2: Catamaran cruise and hot springs.\nDay 3: Wine tasting and famous Oia sunset viewing.\nDay 4: Departure."),
    dict(title="Tokyo City Lights", city="Tokyo", photo="images/tour-img04.jpg",
         desc="Experience the blend of tradition and futuristic city life.",
         price=1150, distance=600, max_group_size=15, featured=True,
         itinerary="Day 1: Arrival at Narita, evening in Shinjuku.\nDay 2: Asakusa Senso-ji temple and Akihabara.\nDay 3: Shibuya crossing and Harajuku shopping.\nDay 4: Day trip to Mt. Fuji.\nDay 5: Departure."),
    dict(title="Amazon Rainforest Trek", city="Manaus", photo="images/tour-img05.jpg",
         desc="Discover exotic wildlife deep in the Amazon rainforest.",
         price=899, distance=700, max_group_size=6, featured=False,
         itinerary="Day 1: Arrival in Manaus, riverboat to jungle lodge.\nDay 2: Piranha fishing and caiman spotting.\nDay 3: Jungle trek and indigenous tribe visit.\nDay 4: Return to Manaus and departure."),
    dict(title="Sahara Desert Safari", city="Marrakech", photo="images/tour-img06.jpg",
         desc="Ride camels across golden dunes under starlit skies.",
         price=650, distance=250, max_group_size=10, featured=False,
         itinerary="Day 1: Arrival in Marrakech, explore Medina.\nDay 2: Drive across Atlas Mountains to Zagora.\nDay 3: Camel trek into Sahara, camp under stars.\nDay 4: Return to Marrakech."),
    dict(title="Machu Picchu Expedition", city="Cusco", photo="images/tour-img07.jpg",
         desc="Trek the Inca trail to the ancient citadel in the clouds.",
         price=1050, distance=480, max_group_size=8, featured=False,
         itinerary="Day 1: Acclimatize in Cusco, city tour.\nDay 2: Sacred Valley tour and train to Aguas Calientes.\nDay 3: Early morning Machu Picchu guided tour.\nDay 4: Return to Cusco and departure."),
    dict(title="Goa Beach Holiday", city="Goa", photo="images/tour-img02.jpg",
         desc="Relax on sandy beaches and explore historic churches.",
         price=450, distance=150, max_group_size=20, featured=True,
         itinerary="Day 1: Arrival in Goa, relax at Baga beach.\nDay 2: Old Goa churches and spice plantation tour.\nDay 3: Water sports and sunset cruise on Mandovi river.\nDay 4: Departure."),
]

review_texts = [
    "Amazing experience! The guide was very knowledgeable.",
    "Breathtaking views and well organized. Highly recommended.",
    "Good value for money, but the food could be better.",
    "An unforgettable trip. Every detail was taken care of.",
    "Loved the itinerary. Perfect balance of adventure and relaxation.",
    "The best vacation I've ever had. Will definitely book again!",
    "Incredible sights, though the travel time was a bit long.",
    "A magical experience from start to finish."
]

app = create_app()

with app.app_context():
    db.create_all()
    Tour.query.delete()
    Review.query.delete()
    
    # Ensure there is at least one user
    user = User.query.first()
    if not user:
        admin_user = User(username="MyName", email="admin@example.com", role="admin")
        admin_user.set_password("admin")
        db.session.add(admin_user)
        db.session.commit()
        user = admin_user
    
    for data in sample_tours:
        tour = Tour(**data)
        db.session.add(tour)
        db.session.flush() # Get tour ID
        
        # Add 2-3 random reviews per tour
        num_reviews = random.randint(2, 4)
        for _ in range(num_reviews):
            review = Review(
                user_id=user.id,
                tour_id=tour.id,
                rating=random.randint(4, 5),
                review_text=random.choice(review_texts)
            )
            db.session.add(review)
            
    db.session.commit()
    print(f"Seeded {len(sample_tours)} tours and their reviews")
