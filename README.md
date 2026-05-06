# Campus Closet

Campus Closet is a campus-only marketplace and virtual thrift store for Southern Connecticut State University students. The goal of the application is to give students a simple place to share clothing, dorm furniture, school supplies, and other useful items within the SCSU community.

The application uses a Southern email login system, a listings browse page, listing detail pages, and starter sections for creating listings, favorites, messaging, profiles, and admin moderation. It is built with Flask, SQLite, HTML templates, and CSS.

## Current Features

- Southern-themed login and registration flow
- `@southernct.edu` email validation
- Browse listings page with sample items
- Listing detail page
- Starter navigation for create listing, favorites, messages, profile, and admin
- SQLite database created automatically when the app starts

## Quick Start

Run these commands from the project folder:

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements.txt
python3 app.py
```

Then open:

`http://127.0.0.1:5051`

## Teammate Setup From GitHub

If you are opening the project from GitHub for the first time, run:

```bash
git clone https://github.com/shree3p/Campus-Closet-.git
cd Campus-Closet-
code .
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements.txt
python3 app.py
```

Then open:

`http://127.0.0.1:5051`

If you already cloned the repo before and just need the newest version, run:

```bash
git pull origin main
```

## Demo Login

- Student: `campusdemo@southernct.edu`
- Password: `CampusCloset123!`

- Admin: `admin@southernct.edu`
- Password: `CampusClosetAdmin123!`

You can also register a new account using any valid `@southernct.edu` email address.

## Main Files

- `app.py` starts the Flask application
- `campus_closet/routes.py` contains the page routes and login logic
- `campus_closet/models.py` contains the database models
- `campus_closet/templates/` contains the HTML pages
- `campus_closet/static/styles.css` contains the site styling

## Notes

- This project is meant for local development and class demonstration
- The database is SQLite, so no separate database setup is needed
- The app creates its database automatically the first time it runs
