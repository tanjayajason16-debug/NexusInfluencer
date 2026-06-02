from flask import Blueprint, flash, redirect, render_template, url_for
from flask_login import login_required

from app.extensions import db
from app.models import Caption, MediaAsset, Persona
from app.personas.forms import PersonaForm


personas_bp = Blueprint("personas", __name__, url_prefix="/personas")


@personas_bp.route("/")
@login_required
def index():
    personas = Persona.query.order_by(Persona.created_at.desc()).all()
    return render_template("personas/index.html", personas=personas)


@personas_bp.route("/new", methods=["GET", "POST"])
@login_required
def create():
    form = PersonaForm()

    if form.validate_on_submit():
        persona = Persona()
        apply_form(persona, form)
        db.session.add(persona)
        db.session.commit()
        flash("Persona created.", "success")
        return redirect(url_for("personas.detail", persona_id=persona.id))

    return render_template("personas/form.html", form=form, title="New Persona")


@personas_bp.route("/<int:persona_id>")
@login_required
def detail(persona_id):
    persona = Persona.query.get_or_404(persona_id)
    return render_template("personas/detail.html", persona=persona)


@personas_bp.route("/<int:persona_id>/profile")
@login_required
def profile(persona_id):
    persona = Persona.query.get_or_404(persona_id)
    publishable_statuses = ("approved", "ready_to_post")
    assets = (
        MediaAsset.query.filter(
            MediaAsset.persona_id == persona.id,
            MediaAsset.status.in_(publishable_statuses),
        )
        .order_by(MediaAsset.updated_at.desc())
        .all()
    )
    captions = (
        Caption.query.filter_by(persona_id=persona.id)
        .order_by(Caption.created_at.desc())
        .all()
    )
    captions_by_asset = {}
    general_captions = []
    for caption in captions:
        if caption.media_asset_id:
            captions_by_asset.setdefault(caption.media_asset_id, []).append(caption)
        else:
            general_captions.append(caption)

    return render_template(
        "personas/profile.html",
        persona=persona,
        assets=assets,
        captions_by_asset=captions_by_asset,
        general_captions=general_captions,
    )


@personas_bp.route("/<int:persona_id>/edit", methods=["GET", "POST"])
@login_required
def edit(persona_id):
    persona = Persona.query.get_or_404(persona_id)
    form = PersonaForm(obj=persona)

    if form.validate_on_submit():
        apply_form(persona, form)
        db.session.commit()
        flash("Persona updated.", "success")
        return redirect(url_for("personas.detail", persona_id=persona.id))

    return render_template("personas/form.html", form=form, title="Edit Persona", persona=persona)


@personas_bp.route("/<int:persona_id>/delete", methods=["POST"])
@login_required
def delete(persona_id):
    persona = Persona.query.get_or_404(persona_id)
    db.session.delete(persona)
    db.session.commit()
    flash("Persona deleted.", "info")
    return redirect(url_for("personas.index"))


def apply_form(persona, form):
    persona.name = form.name.data.strip()
    persona.niche = form.niche.data.strip()
    persona.bio = clean_optional(form.bio.data)
    persona.personality = clean_optional(form.personality.data)
    persona.visual_style = clean_optional(form.visual_style.data)
    persona.caption_tone = clean_optional(form.caption_tone.data)
    persona.reference_notes = clean_optional(form.reference_notes.data)
    persona.reference_image_path = clean_optional(form.reference_image_path.data)
    persona.is_active = bool(form.is_active.data)


def clean_optional(value):
    if not value:
        return None
    cleaned = value.strip()
    return cleaned or None
