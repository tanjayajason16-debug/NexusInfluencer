from flask import Flask

from app.config import Config
from app.extensions import db, login_manager


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"
    login_manager.login_message_category = "warning"

    @login_manager.user_loader
    def load_user(user_id):
        from app.models import User

        return db.session.get(User, int(user_id))

    from app.auth.routes import auth_bp
    from app.dashboard.routes import dashboard_bp
    from app.media.routes import media_bp
    from app.personas.routes import personas_bp
    from app.planning.routes import planning_bp
    from app.review.routes import review_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(media_bp)
    app.register_blueprint(personas_bp)
    app.register_blueprint(planning_bp)
    app.register_blueprint(review_bp)

    register_commands(app)

    return app


def register_commands(app):
    @app.cli.command("init-db")
    def init_db():
        from app import models  # noqa: F401

        db.create_all()
        print("Database tables created.")

    @app.cli.command("create-admin")
    def create_admin():
        import click
        from app.models import User

        db.create_all()

        email = click.prompt("Admin email")
        password = click.prompt("Admin password", hide_input=True, confirmation_prompt=True)

        existing_user = User.query.filter_by(email=email.lower()).first()
        if existing_user:
            raise click.ClickException("A user with this email already exists.")

        user = User(email=email.lower(), is_admin=True)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        click.echo(f"Admin user created: {user.email}")
