from functools import wraps

from flask import Blueprint, abort, flash, redirect, render_template, request, session, url_for
from sqlalchemy import or_
from werkzeug.security import check_password_hash, generate_password_hash

from .models import ActivityLog, Category, Listing, Profile, Report, User, db


main_bp = Blueprint("main", __name__, template_folder="templates", static_folder="static")


def login_required(view_func):
    @wraps(view_func)
    def wrapped_view(*args, **kwargs):
        if "user_id" not in session:
            flash("Please log in with your Southern account to continue.", "warning")
            return redirect(url_for("main.login"))
        return view_func(*args, **kwargs)

    return wrapped_view


def admin_required(view_func):
    @wraps(view_func)
    def wrapped_view(*args, **kwargs):
        user = get_current_user()
        if user is None:
            return redirect(url_for("main.login"))
        if not user.is_admin:
            abort(403)
        return view_func(*args, **kwargs)

    return wrapped_view


def get_current_user():
    user_id = session.get("user_id")
    if not user_id:
        return None
    return db.session.get(User, user_id)


@main_bp.app_context_processor
def inject_template_context():
    return {"current_user": get_current_user()}


@main_bp.route("/")
def home():
    if session.get("user_id"):
        return redirect(url_for("main.browse"))
    return redirect(url_for("main.login"))


@main_bp.route("/login", methods=["GET", "POST"])
def login():
    if session.get("user_id"):
        return redirect(url_for("main.browse"))

    if request.method == "POST":
        identifier = request.form.get("identifier", "").strip()
        password = request.form.get("password", "")

        if not identifier or not password:
            flash("Enter your username or Southern email and your password.", "error")
            return render_template("login.html")

        user = User.query.filter(
            or_(User.username.ilike(identifier), User.email.ilike(identifier))
        ).first()

        if user is None or not check_password_hash(user.password_hash, password):
            flash("Invalid credentials. Please try again.", "error")
            return render_template("login.html")

        if user.account_status != "active":
            flash("This account is not active. Please contact the Campus Closet team.", "error")
            return render_template("login.html")

        session.clear()
        session["user_id"] = user.id

        db.session.add(
            ActivityLog(
                user_id=user.id,
                action_type="login",
                description="User logged in to Campus Closet.",
            )
        )
        db.session.commit()

        if user.is_admin:
            return redirect(url_for("main.admin_dashboard"))
        return redirect(url_for("main.browse"))

    return render_template("login.html")


@main_bp.route("/register", methods=["GET", "POST"])
def register():
    if session.get("user_id"):
        return redirect(url_for("main.browse"))

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        if not all([name, username, email, password]):
            flash("All fields are required for registration.", "error")
            return render_template("register.html")

        if not email.endswith("@southernct.edu"):
            flash("Campus Closet only allows @southernct.edu email addresses.", "error")
            return render_template("register.html")

        if User.query.filter(User.username.ilike(username)).first():
            flash("That username is already taken. Please choose another one.", "error")
            return render_template("register.html")

        if User.query.filter(User.email.ilike(email)).first():
            flash("That email is already registered. Please log in instead.", "error")
            return render_template("register.html")

        user = User(
            name=name,
            username=username,
            email=email,
            password_hash=generate_password_hash(password),
            role="student",
        )
        db.session.add(user)
        db.session.flush()

        db.session.add(
            Profile(
                user_id=user.id,
                major="",
                bio="",
                contact_preferences="In-app messages",
            )
        )
        db.session.add(
            ActivityLog(
                user_id=user.id,
                action_type="register",
                description="User created a new Campus Closet account.",
            )
        )
        db.session.commit()

        flash("Account created. Please log in with your new Southern account.", "success")
        return redirect(url_for("main.login"))

    return render_template("register.html")


@main_bp.route("/logout")
@login_required
def logout():
    user = get_current_user()
    if user:
        db.session.add(
            ActivityLog(
                user_id=user.id,
                action_type="logout",
                description="User logged out of Campus Closet.",
            )
        )
        db.session.commit()
    session.clear()
    flash("You have been logged out.", "success")
    return redirect(url_for("main.login"))


@main_bp.route("/browse")
@login_required
def browse():
    search = request.args.get("search", "").strip()
    category_name = request.args.get("category", "").strip()

    listings_query = Listing.query.join(Category).order_by(Listing.created_at.desc())
    if search:
        wildcard = f"%{search}%"
        listings_query = listings_query.filter(
            or_(Listing.title.ilike(wildcard), Listing.description.ilike(wildcard))
        )
    if category_name:
        listings_query = listings_query.filter(Category.name == category_name)

    categories = Category.query.order_by(Category.name).all()
    listings = listings_query.all()
    return render_template(
        "browse.html",
        categories=categories,
        listings=listings,
        selected_category=category_name,
        search=search,
    )


@main_bp.route("/listing/<int:listing_id>")
@login_required
def listing_detail(listing_id):
    listing = db.get_or_404(Listing, listing_id)
    return render_template("listing_detail.html", listing=listing)


@main_bp.route("/create-listing", methods=["GET", "POST"])
@login_required
def create_listing():
    categories = Category.query.order_by(Category.name).all()
    if request.method == "POST":
        flash(
            "The create-listing form is scaffolded for Week 1. Saving listings is the next team step.",
            "warning",
        )
    return render_template("create_listing.html", categories=categories)


@main_bp.route("/favorites")
@login_required
def favorites():
    return render_template(
        "placeholder.html",
        page_title="Favorites",
        heading="Saved Listings Placeholder",
        description="The Favorites section is wired into the project navigation and ready for the bridge-table logic from the ER diagram.",
    )


@main_bp.route("/messages")
@login_required
def messages():
    return render_template(
        "placeholder.html",
        page_title="Messages",
        heading="Messages Placeholder",
        description="This section matches the SRS conversation flow and is ready for conversation and message integration next.",
    )


@main_bp.route("/profile")
@login_required
def profile():
    user = get_current_user()
    return render_template("profile.html", user=user)


@main_bp.route("/admin")
@admin_required
def admin_dashboard():
    pending_reports = Report.query.filter_by(status="Pending").count()
    total_users = User.query.count()
    total_listings = Listing.query.count()
    return render_template(
        "admin.html",
        pending_reports=pending_reports,
        total_users=total_users,
        total_listings=total_listings,
    )
