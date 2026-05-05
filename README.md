# Campus Closet

Campus Closet is a Flask starter for the CSC 330 final project. This first pass follows the SRS and Week 1 implementation plan by setting up:

- a blue-and-white Southern-themed login/register flow
- starter database models aligned to the ER diagram and class diagram
- a browse page with sample listings
- placeholder sections for create listing, favorites, messages, profile, and admin

## Quick Start

1. Create and activate a virtual environment.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Run the app:

```bash
python3 app.py
```

4. Open the local Flask URL shown in the terminal.

## Demo Accounts

- Student: `campusdemo@southernct.edu` / `CampusCloset123!`
- Admin: `admin@southernct.edu` / `CampusClosetAdmin123!`

You can also create your own student account with any `@southernct.edu` email address.

## Project Structure

- `app.py`: Flask entry point
- `campus_closet/__init__.py`: app factory and database bootstrap
- `campus_closet/models.py`: starter SQLAlchemy models based on the SRS entities
- `campus_closet/routes.py`: auth, browse, detail, and placeholder routes
- `campus_closet/templates/`: Jinja templates
- `campus_closet/static/styles.css`: blue-and-white visual theme

## Scope Notes

This scaffold intentionally does not complete every feature yet. Login/register works, browsing works, listing details work, and the remaining sections are prepared so teammates can keep building and commit their own parts.
