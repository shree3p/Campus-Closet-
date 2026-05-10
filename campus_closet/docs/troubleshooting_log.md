# Campus Closet Troubleshooting Log

## Port Already In Use
Problem:
- Flask server will not start on port 5051.

Fix:
- Stop the old server using CTRL + C.

---

## Virtual Environment Not Active
Problem:
- Python packages are missing.

Fix:
- Run:
source .venv/bin/activate

---

## Missing Packages
Problem:
- Flask or SQLAlchemy import errors appear.

Fix:
- Run:
python3 -m pip install -r requirements.txt

---

## Wrong Git Branch
Problem:
- Changes are being made on main branch.

Fix:
- Run:
git checkout -b tavoy-admin-qa

---

## Push Denied
Problem:
- GitHub push access denied.

Fix:
- Confirm repository collaborator access or contact project owner.

---

## App Will Not Start
Problem:
- Flask application crashes during startup.

Fix:
- Verify dependencies are installed and virtual environment is active.