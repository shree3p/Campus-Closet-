import os

from flask import Flask

from .models import db, seed_reference_data


def create_app():
    app = Flask(__name__)
    os.makedirs(app.instance_path, exist_ok=True)
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "campus-closet-week-one")
    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{os.path.join(app.instance_path, 'campus_closet.db')}"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)

    from .routes import main_bp

    app.register_blueprint(main_bp)

    with app.app_context():
        db.create_all()
        seed_reference_data()

    return app
