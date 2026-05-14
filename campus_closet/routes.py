from datetime import datetime
from functools import wraps

from flask import Blueprint, abort, flash, redirect, render_template, request, session, url_for
from sqlalchemy import and_, or_
from werkzeug.security import check_password_hash, generate_password_hash

from .models import ActivityLog, Category, Conversation, Favorite, Listing, Message, Profile, Report, User, db


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


def get_listing_conversation(listing_id, user_one_id, user_two_id):
    return Conversation.query.filter(
        Conversation.listing_id == listing_id,
        or_(
            and_(
                Conversation.participant_one_id == user_one_id,
                Conversation.participant_two_id == user_two_id,
            ),
            and_(
                Conversation.participant_one_id == user_two_id,
                Conversation.participant_two_id == user_one_id,
            ),
        ),
    ).first()


def user_can_access_conversation(conversation, user_id):
    return conversation.participant_one_id == user_id or conversation.participant_two_id == user_id


def get_conversation_partner(conversation, user_id):
    if conversation.participant_one_id == user_id:
        return conversation.participant_two
    return conversation.participant_one


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
    user = get_current_user()
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
    favorite_listing_ids = {favorite.listing_id for favorite in user.favorites}
    conversation_count = Conversation.query.filter(
        or_(
            Conversation.participant_one_id == user.id,
            Conversation.participant_two_id == user.id,
        )
    ).count()
    return render_template(
        "browse.html",
        categories=categories,
        listings=listings,
        selected_category=category_name,
        search=search,
        favorite_listing_ids=favorite_listing_ids,
        saved_count=len(favorite_listing_ids),
        conversation_count=conversation_count,
    )


@main_bp.route("/listing/<int:listing_id>")
@login_required
def listing_detail(listing_id):
    listing = db.get_or_404(Listing, listing_id)
    user = get_current_user()
    is_favorite = (
        Favorite.query.filter_by(user_id=user.id, listing_id=listing.id).first() is not None
    )
    existing_conversation = None
    if listing.user_id != user.id:
        existing_conversation = get_listing_conversation(listing.id, user.id, listing.user_id)
    return render_template(
        "listing_detail.html",
        listing=listing,
        is_favorite=is_favorite,
        existing_conversation=existing_conversation,
    )


@main_bp.route("/create-listing", methods=["GET", "POST"])
@login_required
def create_listing():
    categories = Category.query.order_by(Category.name).all()
    form_data = {
        "title": "",
        "category": "",
        "condition": "",
        "pickup_location": "",
        "availability": "Available",
        "description": "",
        "image_url": "",
    }

    if request.method == "POST":
        form_data.update(
            {
                "title": request.form.get("title", "").strip(),
                "category": request.form.get("category", "").strip(),
                "condition": request.form.get("condition", "").strip(),
                "pickup_location": request.form.get("pickup_location", "").strip(),
                "availability": request.form.get("availability", "").strip(),
                "description": request.form.get("description", "").strip(),
                "image_url": request.form.get("image_url", "").strip(),
            }
        )

        required_fields = [
            form_data["title"],
            form_data["category"],
            form_data["condition"],
            form_data["pickup_location"],
            form_data["availability"],
            form_data["description"],
        ]
        if not all(required_fields):
            flash("Please complete all required listing fields before saving.", "error")
            return render_template("create_listing.html", categories=categories, form_data=form_data)

        try:
            category_id = int(form_data["category"])
        except ValueError:
            flash("Please choose a valid listing category.", "error")
            return render_template("create_listing.html", categories=categories, form_data=form_data)

        category = db.session.get(Category, category_id)
        if category is None:
            flash("Please choose a valid listing category.", "error")
            return render_template("create_listing.html", categories=categories, form_data=form_data)

        if len(form_data["title"]) > 150:
            flash("Listing titles must be 150 characters or fewer.", "error")
            return render_template("create_listing.html", categories=categories, form_data=form_data)

        if len(form_data["condition"]) > 80:
            flash("Condition must be 80 characters or fewer.", "error")
            return render_template("create_listing.html", categories=categories, form_data=form_data)

        if len(form_data["pickup_location"]) > 120:
            flash("Pickup location must be 120 characters or fewer.", "error")
            return render_template("create_listing.html", categories=categories, form_data=form_data)

        if len(form_data["availability"]) > 40:
            flash("Availability must be 40 characters or fewer.", "error")
            return render_template("create_listing.html", categories=categories, form_data=form_data)

        if len(form_data["image_url"]) > 255:
            flash("Image links must be 255 characters or fewer.", "error")
            return render_template("create_listing.html", categories=categories, form_data=form_data)

        if form_data["image_url"] and not form_data["image_url"].startswith(("http://", "https://")):
            flash("Image links should start with http:// or https://.", "error")
            return render_template("create_listing.html", categories=categories, form_data=form_data)

        user = get_current_user()
        listing = Listing(
            user_id=user.id,
            category_id=category.id,
            title=form_data["title"],
            description=form_data["description"],
            item_condition=form_data["condition"],
            pickup_location=form_data["pickup_location"],
            availability_status=form_data["availability"],
            image_url=form_data["image_url"] or None,
        )
        db.session.add(listing)
        db.session.flush()
        db.session.add(
            ActivityLog(
                user_id=user.id,
                action_type="create_listing",
                description=f"User created listing #{listing.id}: {listing.title}.",
            )
        )
        db.session.commit()

        flash("Listing created successfully. It now appears on Browse.", "success")
        return redirect(url_for("main.browse"))

    return render_template("create_listing.html", categories=categories, form_data=form_data)


@main_bp.route("/listing/<int:listing_id>/favorite", methods=["POST"])
@login_required
def toggle_favorite(listing_id):
    user = get_current_user()
    listing = db.get_or_404(Listing, listing_id)
    next_url = request.form.get("next")
    if not next_url or not next_url.startswith("/"):
        next_url = url_for("main.listing_detail", listing_id=listing.id)

    if listing.user_id == user.id:
        flash("You do not need to save your own listing.", "warning")
        return redirect(next_url)

    favorite = Favorite.query.filter_by(user_id=user.id, listing_id=listing.id).first()
    if favorite is None:
        db.session.add(Favorite(user_id=user.id, listing_id=listing.id))
        db.session.add(
            ActivityLog(
                user_id=user.id,
                action_type="favorite_listing",
                description=f"User saved listing #{listing.id}: {listing.title}.",
            )
        )
        flash("Listing saved to your favorites.", "success")
    else:
        db.session.delete(favorite)
        db.session.add(
            ActivityLog(
                user_id=user.id,
                action_type="remove_favorite",
                description=f"User removed listing #{listing.id}: {listing.title} from favorites.",
            )
        )
        flash("Listing removed from your favorites.", "success")

    db.session.commit()
    return redirect(next_url)


@main_bp.route("/favorites")
@login_required
def favorites():
    user = get_current_user()
    favorite_rows = (
        Favorite.query.filter_by(user_id=user.id)
        .order_by(Favorite.saved_at.desc())
        .all()
    )
    return render_template("favorites.html", favorite_rows=favorite_rows)


@main_bp.route("/listing/<int:listing_id>/start-conversation", methods=["POST"])
@login_required
def start_conversation(listing_id):
    user = get_current_user()
    listing = db.get_or_404(Listing, listing_id)

    if listing.user_id == user.id:
        flash("This listing belongs to you, so there is no one else to message here.", "warning")
        return redirect(url_for("main.listing_detail", listing_id=listing.id))

    conversation = get_listing_conversation(listing.id, user.id, listing.user_id)
    if conversation is None:
        conversation = Conversation(
            listing_id=listing.id,
            participant_one_id=user.id,
            participant_two_id=listing.user_id,
        )
        db.session.add(conversation)
        db.session.flush()
        db.session.add(
            ActivityLog(
                user_id=user.id,
                action_type="start_conversation",
                description=f"User opened a conversation for listing #{listing.id}: {listing.title}.",
            )
        )
        db.session.commit()

    return redirect(url_for("main.messages", conversation=conversation.id))


@main_bp.route("/messages")
@login_required
def messages():
    user = get_current_user()
    conversations = (
        Conversation.query.filter(
            or_(
                Conversation.participant_one_id == user.id,
                Conversation.participant_two_id == user.id,
            )
        )
        .order_by(Conversation.last_updated.desc(), Conversation.created_at.desc())
        .all()
    )

    selected_conversation_id = request.args.get("conversation", type=int)
    selected_conversation = None
    if conversations:
        if selected_conversation_id is None:
            selected_conversation = conversations[0]
        else:
            selected_conversation = next(
                (conversation for conversation in conversations if conversation.id == selected_conversation_id),
                None,
            )
            if selected_conversation is None:
                abort(403)

    if selected_conversation is not None:
        unread_messages = [
            message
            for message in selected_conversation.messages
            if message.sender_id != user.id and not message.is_read
        ]
        if unread_messages:
            for message in unread_messages:
                message.is_read = True
            db.session.commit()

    conversation_summaries = []
    for conversation in conversations:
        ordered_messages = sorted(conversation.messages, key=lambda message: message.created_at)
        latest_message = ordered_messages[-1] if ordered_messages else None
        preview_text = "Conversation ready to start."
        if latest_message is not None:
            preview_text = latest_message.message_text
            if len(preview_text) > 72:
                preview_text = f"{preview_text[:69]}..."

        conversation_summaries.append(
            {
                "conversation": conversation,
                "partner": get_conversation_partner(conversation, user.id),
                "latest_message": latest_message,
                "preview_text": preview_text,
                "unread_count": sum(
                    1
                    for message in ordered_messages
                    if message.sender_id != user.id and not message.is_read
                ),
            }
        )

    selected_messages = []
    selected_partner = None
    if selected_conversation is not None:
        selected_messages = sorted(selected_conversation.messages, key=lambda message: message.created_at)
        selected_partner = get_conversation_partner(selected_conversation, user.id)

    return render_template(
        "messages.html",
        conversation_summaries=conversation_summaries,
        selected_conversation=selected_conversation,
        selected_messages=selected_messages,
        selected_partner=selected_partner,
    )


@main_bp.route("/messages/<int:conversation_id>/send", methods=["POST"])
@login_required
def send_message(conversation_id):
    user = get_current_user()
    conversation = db.get_or_404(Conversation, conversation_id)
    if not user_can_access_conversation(conversation, user.id):
        abort(403)

    message_text = request.form.get("message_text", "").strip()
    if not message_text:
        flash("Write a message before sending it.", "error")
        return redirect(url_for("main.messages", conversation=conversation.id))

    if len(message_text) > 1500:
        flash("Messages should stay under 1500 characters.", "error")
        return redirect(url_for("main.messages", conversation=conversation.id))

    db.session.add(
        Message(
            conversation_id=conversation.id,
            sender_id=user.id,
            message_text=message_text,
        )
    )
    conversation.last_updated = datetime.utcnow()
    db.session.add(
        ActivityLog(
            user_id=user.id,
            action_type="send_message",
            description=f"User sent a message in conversation #{conversation.id}.",
        )
    )
    db.session.commit()

    return redirect(url_for("main.messages", conversation=conversation.id))


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
