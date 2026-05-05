from datetime import datetime

from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash


db = SQLAlchemy()


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default="student")
    account_status = db.Column(db.String(20), nullable=False, default="active")
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    profile = db.relationship("Profile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    listings = db.relationship("Listing", back_populates="owner", lazy=True)
    favorites = db.relationship("Favorite", back_populates="user", lazy=True, cascade="all, delete-orphan")
    sent_messages = db.relationship("Message", foreign_keys="Message.sender_id", back_populates="sender", lazy=True)
    reports_submitted = db.relationship("Report", foreign_keys="Report.reporter_id", back_populates="reporter", lazy=True)
    reports_reviewed = db.relationship("Report", foreign_keys="Report.reviewed_by_admin_id", back_populates="reviewed_by_admin", lazy=True)
    reviews_written = db.relationship("Review", foreign_keys="Review.reviewer_id", back_populates="reviewer", lazy=True)
    reviews_received = db.relationship("Review", foreign_keys="Review.reviewee_id", back_populates="reviewee", lazy=True)
    notifications = db.relationship("Notification", back_populates="user", lazy=True, cascade="all, delete-orphan")
    activity_logs = db.relationship("ActivityLog", back_populates="user", lazy=True, cascade="all, delete-orphan")

    @property
    def is_admin(self):
        return self.role == "admin"


class Profile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False, unique=True)
    major = db.Column(db.String(120))
    bio = db.Column(db.Text)
    profile_image = db.Column(db.String(255))
    contact_preferences = db.Column(db.String(255), default="In-app messages")

    user = db.relationship("User", back_populates="profile")


class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False, unique=True)
    description = db.Column(db.String(255))

    listings = db.relationship("Listing", back_populates="category", lazy=True)


class Listing(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey("category.id"), nullable=False)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=False)
    item_condition = db.Column(db.String(80), nullable=False)
    pickup_location = db.Column(db.String(120), nullable=False)
    availability_status = db.Column(db.String(40), nullable=False, default="Available")
    image_url = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    owner = db.relationship("User", back_populates="listings")
    category = db.relationship("Category", back_populates="listings")
    favorites = db.relationship("Favorite", back_populates="listing", lazy=True, cascade="all, delete-orphan")
    conversations = db.relationship("Conversation", back_populates="listing", lazy=True)
    reports = db.relationship("Report", back_populates="listing", lazy=True)
    reviews = db.relationship("Review", back_populates="listing", lazy=True)


class Favorite(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    listing_id = db.Column(db.Integer, db.ForeignKey("listing.id"), nullable=False)
    saved_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    user = db.relationship("User", back_populates="favorites")
    listing = db.relationship("Listing", back_populates="favorites")

    __table_args__ = (db.UniqueConstraint("user_id", "listing_id", name="uq_favorite_user_listing"),)


class Conversation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    listing_id = db.Column(db.Integer, db.ForeignKey("listing.id"), nullable=False)
    participant_one_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    participant_two_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    last_updated = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    listing = db.relationship("Listing", back_populates="conversations")
    participant_one = db.relationship("User", foreign_keys=[participant_one_id])
    participant_two = db.relationship("User", foreign_keys=[participant_two_id])
    messages = db.relationship("Message", back_populates="conversation", lazy=True, cascade="all, delete-orphan")


class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    conversation_id = db.Column(db.Integer, db.ForeignKey("conversation.id"), nullable=False)
    sender_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    message_text = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, nullable=False, default=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    conversation = db.relationship("Conversation", back_populates="messages")
    sender = db.relationship("User", foreign_keys=[sender_id], back_populates="sent_messages")


class Report(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    reporter_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    listing_id = db.Column(db.Integer, db.ForeignKey("listing.id"))
    reported_user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    reason = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text)
    status = db.Column(db.String(40), nullable=False, default="Pending")
    reviewed_by_admin_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    resolved_at = db.Column(db.DateTime)

    reporter = db.relationship("User", foreign_keys=[reporter_id], back_populates="reports_submitted")
    reviewed_by_admin = db.relationship("User", foreign_keys=[reviewed_by_admin_id], back_populates="reports_reviewed")
    listing = db.relationship("Listing", back_populates="reports")
    reported_user = db.relationship("User", foreign_keys=[reported_user_id])


class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    reviewer_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    reviewee_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    listing_id = db.Column(db.Integer, db.ForeignKey("listing.id"))
    rating = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.Text)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    reviewer = db.relationship("User", foreign_keys=[reviewer_id], back_populates="reviews_written")
    reviewee = db.relationship("User", foreign_keys=[reviewee_id], back_populates="reviews_received")
    listing = db.relationship("Listing", back_populates="reviews")


class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    notification_type = db.Column(db.String(60), nullable=False)
    message = db.Column(db.String(255), nullable=False)
    is_read = db.Column(db.Boolean, nullable=False, default=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    user = db.relationship("User", back_populates="notifications")


class ActivityLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    action_type = db.Column(db.String(80), nullable=False)
    description = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    user = db.relationship("User", back_populates="activity_logs")


def seed_reference_data():
    category_rows = [
        ("Clothing", "Jackets, shoes, uniforms, and everyday wear."),
        ("Dorm Furniture", "Storage, chairs, lamps, and room basics."),
        ("School Supplies", "Binders, notebooks, calculators, and more."),
        ("Electronics", "Small campus-safe tech and accessories."),
        ("Other", "Anything that does not fit the main categories yet."),
    ]

    if Category.query.count() == 0:
        for name, description in category_rows:
            db.session.add(Category(name=name, description=description))
        db.session.commit()

    demo_user = User.query.filter_by(email="campusdemo@southernct.edu").first()
    if demo_user is None:
        demo_user = User(
            name="Campus Demo",
            username="campusdemo",
            email="campusdemo@southernct.edu",
            password_hash=generate_password_hash("CampusCloset123!"),
            role="student",
        )
        db.session.add(demo_user)
        db.session.flush()
        db.session.add(
            Profile(
                user_id=demo_user.id,
                major="Undeclared",
                bio="Starter account for Week 1 demo listings.",
                contact_preferences="In-app messages",
            )
        )

    admin_user = User.query.filter_by(email="admin@southernct.edu").first()
    if admin_user is None:
        admin_user = User(
            name="Campus Closet Admin",
            username="campusadmin",
            email="admin@southernct.edu",
            password_hash=generate_password_hash("CampusClosetAdmin123!"),
            role="admin",
        )
        db.session.add(admin_user)
        db.session.flush()
        db.session.add(
            Profile(
                user_id=admin_user.id,
                major="Administration",
                bio="Starter admin account for moderation demos.",
                contact_preferences="In-app messages",
            )
        )

    db.session.commit()

    if Listing.query.count() == 0:
        categories = {category.name: category for category in Category.query.all()}
        starter_listings = [
            {
                "title": "Blue Desk Lamp",
                "description": "Working lamp for a dorm desk. Pickup near Engleman Hall.",
                "item_condition": "Good",
                "pickup_location": "Engleman Hall lobby",
                "category": "Dorm Furniture",
            },
            {
                "title": "Winter Jacket",
                "description": "Medium size jacket in clean condition for cold weather walks across campus.",
                "item_condition": "Very Good",
                "pickup_location": "Student Center",
                "category": "Clothing",
            },
            {
                "title": "Calculator and Notebook Bundle",
                "description": "Helpful starter set for classes. One calculator and two unused notebooks.",
                "item_condition": "Good",
                "pickup_location": "Buley Library entrance",
                "category": "School Supplies",
            },
        ]

        for item in starter_listings:
            db.session.add(
                Listing(
                    user_id=demo_user.id,
                    category_id=categories[item["category"]].id,
                    title=item["title"],
                    description=item["description"],
                    item_condition=item["item_condition"],
                    pickup_location=item["pickup_location"],
                    availability_status="Available",
                )
            )

        db.session.add(
            ActivityLog(
                user_id=demo_user.id,
                action_type="seed_data",
                description="Starter listings created for Week 1 demo flow.",
            )
        )
        db.session.commit()

