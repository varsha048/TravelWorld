import docx
from docx.shared import Pt, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH

def create_synopsis(filename):
    doc = docx.Document()

    # Title
    title = doc.add_heading('TravelWorld - Project Synopsis', 0)
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER

    # Introduction
    doc.add_heading('1. Introduction', level=1)
    doc.add_paragraph(
        "TravelWorld is a comprehensive, modern, and interactive web-based travel and tourism management system. "
        "The project aims to seamlessly bridge the gap between travel agencies and prospective tourists by offering "
        "an intuitive platform for browsing customized travel packages, exploring itineraries, and managing bookings."
    )

    # Objective
    doc.add_heading('2. Objectives', level=1)
    doc.add_paragraph(
        "The primary objective of the TravelWorld project is to digitize travel planning operations. Specifically, it aims to:\n"
        "- Provide a responsive, aesthetically pleasing frontend interface for users to explore global destinations.\n"
        "- Implement robust user authentication to secure user data and booking history.\n"
        "- Offer an intelligent AI-powered search and virtual assistant to help users find their ideal vacations based on natural language queries.\n"
        "- Deliver a comprehensive Admin Dashboard to allow travel agents to effortlessly manage tours, review customer inquiries, and respond via integrated email systems."
    )

    # Key Features
    doc.add_heading('3. Key Features', level=1)
    features = [
        "Dynamic Tour Exploration: Users can seamlessly search and filter tours by location, distance, and group size, complete with detailed itineraries and authentic user reviews.",
        "Secure User Authentication: Integrated JWT-based authentication using HTTP-only cookies to ensure security for user sessions, registrations, and logins.",
        "Interactive Bookings System: Real-time calculation of pricing, service charges, and automated booking processes, including row-level locking for exclusive limited-slot 'Next Escapes'.",
        "AI-Powered Smart Search: Integration with Google Gemini AI to interpret natural language queries (e.g., 'A romantic getaway in the snow') and instantly map them to relevant travel packages.",
        "Admin Management Dashboard: A secure, restricted portal where administrators can dynamically add/edit tours, manage upcoming escapes, and respond to user inquiries directly via an integrated Google SMTP email system."
    ]
    for feature in features:
        doc.add_paragraph(feature, style='List Bullet')

    # Technology Stack
    doc.add_heading('4. Technology Stack', level=1)
    tech = [
        "Frontend: HTML5, CSS3 (Custom responsive design without reliance on heavy frameworks), Vanilla JavaScript (ES6).",
        "Backend: Python, Flask Framework.",
        "Database: SQLite optimized with SQLAlchemy ORM.",
        "AI Integration: Google Gemini AI (Generative Language API) for semantic search and virtual assistance.",
        "Authentication: JSON Web Tokens (JWT), Werkzeug Security for password hashing.",
        "Email Integration: Python smtplib with Google SMTP."
    ]
    for t in tech:
        doc.add_paragraph(t, style='List Bullet')

    # System Architecture
    doc.add_heading('5. System Architecture', level=1)
    doc.add_paragraph(
        "TravelWorld operates on a RESTful client-server architecture. The frontend independently manages the UI state and communicates asynchronously (via Fetch API) with the Flask backend. "
        "The backend endpoints securely process business logic, enforce authentication via decorators, interact with the SQLite database via SQLAlchemy, and occasionally broker requests to external APIs like Google Gemini."
    )

    # Conclusion
    doc.add_heading('6. Conclusion', level=1)
    doc.add_paragraph(
        "TravelWorld successfully demonstrates a full-stack, scalable approach to building an intelligent travel platform. "
        "By fusing modern UI paradigms with AI-driven search capabilities and a solid backend architecture, the project provides a rich, engaging experience for users and an efficient management tool for travel administrators."
    )

    doc.save(filename)
    print(f"Successfully generated synopsis at {filename}")

if __name__ == '__main__':
    create_synopsis('TravelWorld_Project_Synopsis.docx')
