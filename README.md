# Yumma Services

Yumma is a Flask-based web application for managing and displaying listings for PG accommodations, hotels, restaurants, food items, and meals.
It provides forms for adding entries, secure admin access for management, image upload and display support, and email notifications for new submissions.

---

## Overview

The application allows administrators to:

* Add PG, Hotel, Restaurant, Food, and Meal listings
* View detailed pages for each listing type
* Upload images for listings
* Manage (view and delete) listings
* Receive email alerts when new PG submissions are added

The frontend is built using HTML templates with basic styling, while the backend uses Flask with PostgreSQL via SQLAlchemy for persistence.

---

## Key Features

* PG listing creation and details view
* Hotel listing creation and details view
* Restaurant listing creation and details view
* Food and Meal submission and display
* Admin login and logout
* Image upload and retrieval
* PostgreSQL database integration
* Email notifications using SMTP

---

## Tech Stack

**Backend**

* Python
* Flask
* Flask-SQLAlchemy
* PostgreSQL
* psycopg2-binary

**Frontend**

* HTML templates (Jinja2)
* Static assets

**Other**

* SMTP email via `smtplib`

---

## Project Structure

```
pgeats-main/
│
├── app.py                 # Main Flask application
├── config.py              # Email configuration
├── utils.py               # Email sending utility
├── requirements.txt       # Python dependencies
│
├── static/
│   └── uploads/           # Uploaded images
│
└── templates/             # HTML templates
    ├── home.html
    ├── admin_login.html
    ├── form.html
    ├── pg_details.html
    ├── pg_display.html
    ├── hotel_form.html
    ├── hotel_details.html
    ├── hotel_display.html
    ├── Restaurant_details.html
    ├── Restaurant_display.html
    ├── food_form.html
    ├── food_display.html
    ├── meal_form.html
    ├── meal_display.html
    └── EATS templates
```

---

## Installation

1. Clone or extract the project.

2. Create and activate a virtual environment (recommended).

3. Install dependencies:

```
pip install -r requirements.txt
```

4. Ensure PostgreSQL is available and the connection string inside `app.py` under:

```
app.config['SQLALCHEMY_DATABASE_URI']
```

is properly configured.

5. Ensure upload directory exists:

```
static/uploads
```

---

## Configuration

Email configuration is stored in `config.py` and used for administrative email alerts:

```
EMAIL_HOST
EMAIL_PORT
EMAIL_USERNAME
EMAIL_PASSWORD
ADMIN_EMAIL
```

Update these values if required.

---

## Running the Application

Execute:

```
python app.py
```

The application runs in debug mode by default.

Open the browser and navigate to:

```
http://127.0.0.1:5000/
```

---

## Routes

### Public

* `/` – Home
* `/pg` – Add PG
* `/pg-list` – View PG list
* `/pg-details/<id>` – View PG details
* `/hotel` – Add Hotel
* `/hotel-list` – View Hotel list
* `/hotel-details/<id>`
* `/Restaurant-list`
* `/Restaurant-details/<id>`
* `/food`
* `/meal`
* `/EATS-list`
* `/EATS-details/<id>`
* Image retrieval routes (e.g., `/get_image/<id>`)

### Admin

* `/admin-login`
* `/admin-logout`
* Delete routes exist for PG, Hotel, Restaurant, and EATS entries

---

## Image Handling

Images uploaded through forms are stored and retrieved using respective image endpoints:

```
/get_image/<id>
/get_food_image/<id>
/get_meal_image/<id>
/hotel_get_image/<id>
```

---

## Email Notifications

When a PG is submitted, an email notification is sent to the configured admin using the SMTP configuration in `config.py`.

---

## License

No license file is provided in this project.

---

## Notes

* Database tables are created automatically at startup using SQLAlchemy.
* Ensure valid database credentials before running.
* SMTP credentials must be valid for email notifications to work.
