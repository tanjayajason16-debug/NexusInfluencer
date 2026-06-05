from pathlib import Path
from datetime import datetime, time, timedelta
import io

from flask import Blueprint, current_app, flash, redirect, render_template, request, send_file, url_for
from flask_login import login_required
from werkzeug.utils import secure_filename

from app.extensions import db
from app.media.forms import MediaAssetForm, MediaStatusForm
from app.models import MEDIA_STATUSES, MediaAsset, Persona
from app.storage import StorageError, delete_file, open_file, save_file


media_bp = Blueprint("media", __name__, url_prefix="/media")


@media_bp.route("/")
@login_required
def index():
    persona_id = request.args.get("persona_id", type=int)
    status = request.args.get("status", "")
    media_type = request.args.get("media_type", "")
    date_from = request.args.get("date_from", "")
    date_to = request.args.get("date_to", "")

    query = MediaAsset.query.join(Persona)
    if persona_id:
        query = query.filter(MediaAsset.persona_id == persona_id)
    if status:
        query = query.filter(MediaAsset.status == status)
    if media_type:
        query = query.filter(MediaAsset.media_type == media_type)
    if date_from:
        parsed_from = parse_filter_date(date_from)
        if parsed_from:
            query = query.filter(MediaAsset.created_at >= parsed_from)
    if date_to:
        parsed_to = parse_filter_date(date_to)
        if parsed_to:
            query = query.filter(MediaAsset.created_at < parsed_to + timedelta(days=1))

    assets = query.order_by(MediaAsset.created_at.desc()).all()
    personas = Persona.query.order_by(Persona.name.asc()).all()
    return render_template(
        "media/index.html",
        assets=assets,
        personas=personas,
        statuses=MEDIA_STATUSES,
        selected_persona_id=persona_id,
        selected_status=status,
        selected_media_type=media_type,
        selected_date_from=date_from,
        selected_date_to=date_to,
    )


@media_bp.route("/new", methods=["GET", "POST"])
@login_required
def create():
    form = MediaAssetForm()
    form.persona_id.choices = persona_choices()

    if not form.persona_id.choices:
        flash("Create a persona before uploading media.", "warning")
        return redirect(url_for("personas.create"))

    if form.validate_on_submit():
        upload = form.file.data
        media_type = detect_media_type(upload.filename)
        if not media_type:
            flash("Unsupported media type.", "danger")
            return render_template("media/form.html", form=form)

        try:
            stored_path = save_file(upload, media_type)
        except StorageError as exc:
            flash(str(exc), "danger")
            return render_template("media/form.html", form=form)

        asset = MediaAsset(
            persona_id=form.persona_id.data,
            media_type=media_type,
            file_path=stored_path,
            original_filename=secure_filename(upload.filename),
            status="draft",
            prompt=clean_optional(form.prompt.data),
            caption_idea=clean_optional(form.caption_idea.data),
            generation_notes=clean_optional(form.generation_notes.data),
        )
        db.session.add(asset)
        db.session.commit()
        flash("Media asset uploaded as draft.", "success")
        return redirect(url_for("media.detail", asset_id=asset.id))

    return render_template("media/form.html", form=form)


@media_bp.route("/<int:asset_id>", methods=["GET", "POST"])
@login_required
def detail(asset_id):
    asset = MediaAsset.query.get_or_404(asset_id)
    form = MediaStatusForm(obj=asset)

    if form.validate_on_submit():
        asset.status = form.status.data
        db.session.commit()
        flash("Media status updated.", "success")
        return redirect(url_for("media.detail", asset_id=asset.id))

    return render_template("media/detail.html", asset=asset, form=form)


@media_bp.route("/<int:asset_id>/delete", methods=["POST"])
@login_required
def delete(asset_id):
    asset = MediaAsset.query.get_or_404(asset_id)
    try:
        delete_file(asset.file_path)
    except StorageError:
        pass
    db.session.delete(asset)
    db.session.commit()
    flash("Media asset deleted.", "info")
    return redirect(url_for("media.index"))


@media_bp.route("/<int:asset_id>/download")
@login_required
def download(asset_id):
    asset = MediaAsset.query.get_or_404(asset_id)

    try:
        content = open_file(asset.file_path)
    except StorageError:
        flash("The media file could not be found.", "danger")
        return redirect(url_for("media.detail", asset_id=asset.id))

    if isinstance(content, Path):
        return send_file(content, as_attachment=True, download_name=asset.original_filename)

    buffer, content_type = content
    buffer.seek(0)
    return send_file(buffer, as_attachment=True, download_name=asset.original_filename, mimetype=content_type)


def persona_choices():
    return [(persona.id, persona.name) for persona in Persona.query.order_by(Persona.name.asc()).all()]


def detect_media_type(filename):
    extension = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    if extension in current_app.config["ALLOWED_IMAGE_EXTENSIONS"]:
        return "image"
    if extension in current_app.config["ALLOWED_VIDEO_EXTENSIONS"]:
        return "video"
    return None


def clean_optional(value):
    if not value:
        return None
    cleaned = value.strip()
    return cleaned or None


def parse_filter_date(value):
    try:
        return datetime.combine(datetime.strptime(value, "%Y-%m-%d").date(), time.min)
    except ValueError:
        return None
