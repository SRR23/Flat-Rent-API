
# Flat-Rent API

This is a RESTful API for a flat rent platform built with Django and Django Rest Framework (DRF). The API allows owners to create, read, update, and delete flat details posts. Renters can view post and booked desired flat via sending email to owners.


## Features

- User authentication (registration, login)
- Owners and Renters have individual registration system
- Confirmation mail for activate account
- CRUD operations for flat information posts
- Booking system for flats via sending email
- add to booking list functionality
- Search and filtering for flats
- Token-based authentication

## Installation

Follow these steps to set up and run the project locally:

    1. Clone the Repository

    First, clone the repository from GitHub:

    git clone https://github.com/SRR23/Flat-Rent-API.git
    cd config

    2. Set Up a Virtual Environment
    Create and activate a virtual environment:

    # On macOS/Linux
    python3 -m venv venv
    source venv/bin/activate

    # On Windows
    python -m venv venv
    venv\Scripts\activate

    3. Install Dependencies
    Install the required packages:

    pip install -r requirements.txt

    4. Apply Migrations
    Run database migrations:

    python manage.py migrate

    5. Create a Superuser (Optional)
    To access the Django admin panel, create a superuser:

    python manage.py createsuperuser
    Follow the prompts to set up your admin account.

    6. Run the Development Server
    Start the Django development server:

    python manage.py runserver

    The API will be available at:
    📌 http://127.0.0.1:8000/
    
## API Endpoints

    Authentication:
        POST /api/register/
        POST /api/login/

    User Profile:
        GET /api/profile/ # Get Profile
        PUT /api/profile/{id}/ # Update Profile

    Owners Flat Management:
        POST /api/owner/flats/add/ # Create a Flat Post
        GET /api/owner/flats_list/ # Show Owner Listed Flats
        PUT /api/owner/flats/{id}/ # Update One of Owner Flats
        DELETE /api/owner/flats/{id}/ # Delete One of Owner Flats
    
    Renter Bookings:
        GET /api/renter/bookings/ # Booking List
        DELETE /api/renter/bookings/delete/{slug}/ # Remove From Booking History
        POST /api/renter/send_message/{slug}/ # Send Booking message via email to owner
    
    Flat Listing & Filtering:
        GET /api/home/ # Show Few Flats in home page
        GET /api/all_flats/ # Show All Flats
        GET /api/flat_details/{slug}/ # Show Flat Detail
        GET /api/search/?category={title} & location={title} # Search Flats by Category and Location
        GET /api/filter_category/?category={id} # Filter Flats by Category
    
    Flat Metadata:
        GET /api/locations/ # List All Locations
        GET /api/categories/ # List All Categories
    
    Contact With Admin:
        POST /api/contact/ # Message will sent to Admin Mail

## Authentication

    This API uses JWT-based authentication. To access protected routes, include your token in the request headers:
    Authorization: Bearer your_token_here

## Technologies Used

    Python
    Django
    Django Rest Framework (DRF)
    Postgresql
    Cloudinary # For store image
    JWT Token Authentication
