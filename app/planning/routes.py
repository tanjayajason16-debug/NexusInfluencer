from datetime import datetime, timezone

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import login_required

from app.ai import AIError, generate_caption
from app.extensions import db
from app.models import Caption, MediaAsset, Persona, Post
from app.planning.forms import CaptionForm, PostForm


planning_bp = Blueprint("planning", __name__, url_prefix="/planning")


@planning_bp.route("/")
@login_required
def index():
    upcoming_posts = (
        Post.query.order_by(Post.scheduled_for.is_(None), Post.scheduled_for.asc(), Post.created_at.desc())
        .limit(20)
        .all()
    )
    ready_assets = MediaAsset.query.filter_by(status="ready_to_post").order_by(MediaAsset.updated_at.desc()).limit(12).all()
    recent_captions = Caption.query.order_by(Caption.created_at.desc()).limit(10).all()
    return render_template(
        "planning/index.html",
        upcoming_posts=upcoming_posts,
        ready_assets=ready_assets,
        recent_captions=recent_captions,
    )


@planning_bp.route("/captions/new", methods=["GET", "POST"])
@login_required
def create_caption():
    form = CaptionForm()
    populate_caption_choices(form)

    if no_personas():
        flash("Create a persona before adding captions.", "warning")
        return redirect(url_for("personas.create"))

    action = request.form.get("action")
    if request.method == "POST" and action == "generate":
        if form.persona_id.validate(form):
            persona = Persona.query.get(form.persona_id.data)
            if persona is None:
                flash("Selected persona not found.", "danger")
            else:
                asset = None
                if form.media_asset_id.data:
                    asset = MediaAsset.query.get(optional_id(form.media_asset_id.data))
                caption_prompt = clean_optional(form.prompt.data)
                if not caption_prompt and asset and asset.prompt:
                    caption_prompt = asset.prompt

                try:
                    generated_text = generate_caption(persona, prompt=caption_prompt)
                    form.text.data = generated_text
                    flash("AI caption generated. Review the text before saving.", "success")
                except AIError as exc:
                    flash(str(exc), "danger")
        return render_template("planning/caption_form.html", form=form)

    if form.validate_on_submit():
        caption = Caption(
            persona_id=form.persona_id.data,
            media_asset_id=optional_id(form.media_asset_id.data),
            text=form.text.data.strip(),
            tone=clean_optional(form.tone.data),
            hashtags=clean_optional(form.hashtags.data),
        )
        db.session.add(caption)
        db.session.commit()
        flash("Caption saved.", "success")
        return redirect(url_for("planning.index"))

    return render_template("planning/caption_form.html", form=form)


@planning_bp.route("/posts/new", methods=["GET", "POST"])
@login_required
def create_post():
    form = PostForm()
    populate_post_choices(form)

    if no_personas():
        flash("Create a persona before planning posts.", "warning")
        return redirect(url_for("personas.create"))

    if form.validate_on_submit():
        post = Post(
            persona_id=form.persona_id.data,
            media_asset_id=optional_id(form.media_asset_id.data),
            caption_id=optional_id(form.caption_id.data),
            platform=form.platform.data.strip(),
            scheduled_for=form.scheduled_for.data,
            status=form.status.data,
            manual_posting_notes=clean_optional(form.manual_posting_notes.data),
        )
        if post.status == "posted" and post.posted_at is None:
            post.posted_at = datetime.now(timezone.utc)
        db.session.add(post)
        db.session.commit()
        flash("Post planned.", "success")
        return redirect(url_for("planning.index"))

    if not form.platform.data:
        form.platform.data = "Instagram"
    if not form.status.data:
        form.status.data = "planned"

    return render_template("planning/post_form.html", form=form)


@planning_bp.route("/posts/<int:post_id>/status/<status>", methods=["POST"])
@login_required
def update_post_status(post_id, status):
    post = Post.query.get_or_404(post_id)
    valid_statuses = {"planned", "ready", "posted", "cancelled"}
    if status not in valid_statuses:
        flash("Invalid post status.", "danger")
        return redirect(url_for("planning.index"))

    post.status = status
    if status == "posted":
        post.posted_at = datetime.now(timezone.utc)
        if post.media_asset:
            post.media_asset.status = "posted"
    db.session.commit()
    flash("Post status updated.", "success")
    return redirect(url_for("planning.index"))


def populate_caption_choices(form):
    form.persona_id.choices = persona_choices()
    form.media_asset_id.choices = empty_choice("No linked asset") + media_asset_choices()


def populate_post_choices(form):
    form.persona_id.choices = persona_choices()
    form.media_asset_id.choices = empty_choice("No selected asset") + media_asset_choices()
    form.caption_id.choices = empty_choice("No selected caption") + caption_choices()


def persona_choices():
    return [(persona.id, persona.name) for persona in Persona.query.order_by(Persona.name.asc()).all()]


def media_asset_choices():
    assets = MediaAsset.query.order_by(MediaAsset.created_at.desc()).all()
    return [(asset.id, f"{asset.persona.name} - {asset.original_filename} ({asset.status})") for asset in assets]


def caption_choices():
    captions = Caption.query.order_by(Caption.created_at.desc()).all()
    return [(caption.id, f"{caption.persona.name} - {caption.text[:60]}") for caption in captions]


def empty_choice(label):
    return [(0, label)]


def optional_id(value):
    return value if value else None


def no_personas():
    return Persona.query.count() == 0


def clean_optional(value):
    if not value:
        return None
    cleaned = value.strip()
    return cleaned or None
