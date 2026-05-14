# Campus Closet

Campus Closet is a Southern Connecticut State University student marketplace created for CSC 330. The application gives SCSU students a campus-only platform where they can register with a Southern email, post listings, browse available items, save favorites, message other students, and report listings when moderation is needed.

The project is built with Flask, SQLite, HTML, and CSS. It is designed to run locally, and the database is created automatically on first launch.

## Team Roles

- Shree Patel: Team Lead, UI design, front-end development, feature integration, and project coordination
- Shiv Patel: Backend workflows, listing logic, and route implementation
- Jeremiah Trail: Database planning, ER relationship alignment, and schema support
- Tavoy Arnett: Troubleshooting, QA support, and admin feature assistance

## How The Application Works

- Students create an account using a valid `@southernct.edu` email address
- Users can browse listings by category or keyword
- Students can create their own listings and upload an image from their computer
- Listings can be saved to Favorites for later viewing
- Users can message listing owners through the built-in messaging system
- Listings can be reported to the admin for moderation review
- Listing owners can delete their own posts when they are no longer available
- The admin account can review reports and remove listings when necessary

## Run Instructions

From the project folder, run:

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements.txt
python3 app.py
```

Then open:

`http://127.0.0.1:5051`

## Login Credentials

Professor test student account:

- Email: `campusdemo@southernct.edu`
- Password: `CampusCloset123!`

Professor test admin account:

- Email: `admin@southernct.edu`
- Password: `CampusClosetAdmin123!`

You can also register a new student account using any valid `@southernct.edu` email address.

## Main Files

- `app.py`: starts the Flask application
- `requirements.txt`: lists the Python dependencies
- `campus_closet/models.py`: defines the database models
- `campus_closet/routes.py`: contains the route logic and application behavior
- `campus_closet/templates/`: stores the HTML templates
- `campus_closet/static/`: stores the stylesheet, logo, and upload folder

## Notes

- This project is intended to be run locally.
- SQLite data is generated automatically in the `instance/` folder on first run.
- Uploaded listing images are stored in `campus_closet/static/uploads/`.
