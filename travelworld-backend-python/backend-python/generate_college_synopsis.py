import docx
from docx.shared import Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH

def create_synopsis(filename):
    doc = docx.Document()
    
    # Helper to add section headers
    def add_section_header(text):
        h = doc.add_heading(text, level=1)

    # Title of the Project
    title = doc.add_heading('Title of the Project: TravelWorld Management System', 0)
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    # Introduction
    add_section_header('1. Introduction')
    doc.add_paragraph("TravelWorld is a comprehensive, modern, and interactive web-based travel and tourism management system. The project seamlessly bridges the gap between travel agencies and prospective tourists by offering an intuitive platform for browsing customized travel packages, exploring itineraries, and managing bookings. By leveraging AI capabilities, it provides a smart, personalized approach to travel planning.")
    
    # Problem Statement
    add_section_header('2. Problem Statement')
    doc.add_paragraph("Traditional travel planning methods often require customers to navigate fragmented systems, disjointed booking processes, and overwhelming amounts of unorganized data. Customers struggle to find tailored travel packages matching their specific needs. Additionally, travel administrators face challenges in managing dynamic itineraries, tracking inquiries, and coordinating limited-capacity tours effectively without a centralized platform.")
    
    # Objectives
    add_section_header('3. Objectives')
    objectives = [
        "To provide a centralized platform for exploring global travel destinations with detailed itineraries and transparent pricing.",
        "To implement an intelligent AI-powered virtual assistant and semantic search engine that interprets natural language to recommend relevant tours.",
        "To facilitate secure and seamless booking experiences, including handling concurrent booking requests efficiently.",
        "To offer administrators a dedicated dashboard to manage tours, monitor bookings, and respond to customer inquiries in real-time."
    ]
    for obj in objectives:
        doc.add_paragraph(obj, style='List Bullet')
        
    # Scope of the Project
    add_section_header('4. Scope of the Project')
    doc.add_paragraph("The scope encompasses the design, development, and deployment of a full-stack web application. For end-users, it covers secure registration/login, browsing tours, viewing interactive itineraries, AI-assisted searching, booking packages, and reading/writing reviews. For administrators, it covers a secure backend panel to manage database records (tours, upcoming escapes), monitor user interactions, and handle direct email communications via SMTP.")
    
    # Proposed Methodology
    add_section_header('5. Proposed Methodology')
    doc.add_paragraph("The project follows an Agile development methodology, allowing iterative enhancements and continuous integration of features. The architecture relies on a RESTful client-server model. The frontend focuses on an interactive, responsive UI using Vanilla JavaScript and Fetch API, while the backend utilizes the Python Flask framework coupled with SQLite via SQLAlchemy ORM. Secure JWT-based HTTP-only cookies handle authentication, ensuring data integrity across the system.")
    
    # Modules
    add_section_header('6. Modules')
    modules = {
        "User Authentication": "Handles secure user registration, login, and session management using JWT cookies and password hashing.",
        "Tour Management": "Allows users to browse various tours, read detailed day-by-day itineraries, and explore destination specifics. Administrators can dynamically add, update, or remove tours.",
        "Booking System": "Manages tour reservations. Incorporates row-level database locking to prevent overbooking for exclusive 'Next Escape' limited-slot packages.",
        "AI Assistant & Semantic Search": "Integrates Google Gemini AI to interpret complex user queries and recommend the most suitable tours, acting as a virtual travel agent.",
        "Review & Rating System": "Enables authenticated users to leave feedback and ratings (1-5 stars) on completed tours, aggregating scores dynamically for prospective customers.",
        "Admin Dashboard & Communications": "Provides a restricted portal for administrators to oversee operations, track system metrics, and reply to user inquiries directly using Python's smtplib integration."
    }
    for mod, desc in modules.items():
        p = doc.add_paragraph()
        p.add_run(mod + ": ").bold = True
        p.add_run(desc)
        
    # Software & Hardware Requirements
    add_section_header('7. Software & Hardware Requirements')
    doc.add_heading('Software Requirements:', level=2)
    s_reqs = [
        "Operating System: Windows 10/11, macOS, or Linux",
        "Frontend: HTML5, CSS3, Vanilla JavaScript (ES6)",
        "Backend: Python 3.9+, Flask Framework",
        "Database: SQLite 3",
        "Libraries/APIs: SQLAlchemy, PyJWT, Google GenerativeLanguage API"
    ]
    for r in s_reqs:
        doc.add_paragraph(r, style='List Bullet')
        
    doc.add_heading('Hardware Requirements:', level=2)
    h_reqs = [
        "Processor: Intel Core i3 (or equivalent) and above",
        "RAM: 4 GB minimum (8 GB recommended)",
        "Storage: Minimum 1 GB of free disk space",
        "Internet Connection: Required for AI API integration and SMTP communication"
    ]
    for r in h_reqs:
        doc.add_paragraph(r, style='List Bullet')
        
    # Expected Outcome
    add_section_header('8. Expected Outcome')
    doc.add_paragraph("The expected outcome is a fully functional, secure, and user-friendly web application that streamlines the travel planning and booking process. Users will benefit from AI-driven personalized recommendations and an intuitive interface, while administrators will gain a powerful centralized tool to efficiently manage the travel agency's daily operations.")
    
    # Conclusion
    add_section_header('9. Conclusion')
    doc.add_paragraph("In conclusion, the TravelWorld Management System addresses the core inefficiencies in traditional travel planning. By fusing modern web technologies with advanced AI capabilities, the project delivers a scalable, robust, and engaging platform that significantly enhances the user experience and optimizes administrative workflows.")
    
    doc.save(filename)
    print(f"Successfully generated synopsis at {filename}")

if __name__ == '__main__':
    create_synopsis('TravelWorld_College_Synopsis.docx')
