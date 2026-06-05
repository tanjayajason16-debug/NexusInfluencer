from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_user, logout_user

from app.auth.forms import LoginForm
from app.models import User


auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.index"))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower()).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            next_url = request.args.get("next")
            return redirect(next_url or url_for("dashboard.index"))

        flash("Invalid email or password.", "danger")

    return render_template("auth/login.html", form=form)


@auth_bp.route("/logout", methods=["POST"])
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("auth.login"))


@auth_bp.route("/setup-db")
def setup_db():
    from app.extensions import db
    from app.models import User
    from flask import current_app
    import os

    db_url = current_app.config.get("SQLALCHEMY_DATABASE_URI", "NOT SET")
    # Mask password in URL for display
    safe_url = db_url.split("@")[-1] if "@" in db_url else db_url

    try:
        db.create_all()
        admin_email = current_app.config.get("ADMIN_EMAIL")
        admin_password = current_app.config.get("ADMIN_PASSWORD")

        if not admin_email or not admin_password:
            return (
                f"DB connected OK (host: {safe_url}) but ADMIN_EMAIL / ADMIN_PASSWORD "
                "env vars are not set in Vercel. Add them and redeploy."
            ), 200

        existing_user = User.query.filter_by(email=admin_email.lower()).first()
        if not existing_user:
            admin_user = User(email=admin_email.lower(), is_admin=True)
            admin_user.set_password(admin_password)
            db.session.add(admin_user)
            db.session.commit()
            return f"Success! Tables created and admin '{admin_email}' registered. You can now log in.", 200
        else:
            return f"Already set up. Admin '{admin_email}' exists. You can log in now.", 200

    except Exception as e:
        return (
            f"Database setup failed.\n"
            f"DB host: {safe_url}\n"
            f"Error: {str(e)}\n\n"
            f"Check that DATABASE_URL is correctly set in Vercel with the right Supabase password."
        ), 200


