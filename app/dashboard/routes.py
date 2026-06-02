from flask import Blueprint, render_template
from flask_login import login_required

from app.models import Caption, MediaAsset, Persona, Post


dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/")
@login_required
def index():
    stats = {
        "personas": Persona.query.count(),
        "active_personas": Persona.query.filter_by(is_active=True).count(),
        "media_assets": MediaAsset.query.count(),
        "draft_assets": MediaAsset.query.filter_by(status="draft").count(),
        "captions": Caption.query.count(),
        "planned_posts": Post.query.filter(Post.status.in_(["planned", "ready"])).count(),
        "review_queue": MediaAsset.query.filter_by(status="draft").count(),
    }
    recent_personas = Persona.query.order_by(Persona.created_at.desc()).limit(5).all()
    ready_assets = MediaAsset.query.filter_by(status="ready_to_post").order_by(MediaAsset.updated_at.desc()).limit(5).all()
    review_assets = MediaAsset.query.filter_by(status="draft").order_by(MediaAsset.created_at.asc()).limit(5).all()
    upcoming_posts = Post.query.order_by(Post.scheduled_for.is_(None), Post.scheduled_for.asc()).limit(5).all()
    return render_template(
        "dashboard/index.html",
        stats=stats,
        recent_personas=recent_personas,
        ready_assets=ready_assets,
        review_assets=review_assets,
        upcoming_posts=upcoming_posts,
    )
