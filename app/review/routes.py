from flask import Blueprint, flash, redirect, render_template, url_for
from flask_login import current_user, login_required

from app.extensions import db
from app.models import MediaAsset, ReviewNote
from app.review.forms import ApproveForm, RejectForm


review_bp = Blueprint("review", __name__, url_prefix="/review")


@review_bp.route("/")
@login_required
def index():
    draft_assets = MediaAsset.query.filter_by(status="draft").order_by(MediaAsset.created_at.asc()).all()
    recent_notes = ReviewNote.query.order_by(ReviewNote.created_at.desc()).limit(20).all()
    approve_form = ApproveForm()
    reject_form = RejectForm()
    return render_template(
        "review/index.html",
        draft_assets=draft_assets,
        recent_notes=recent_notes,
        approve_form=approve_form,
        reject_form=reject_form,
    )


@review_bp.route("/<int:asset_id>/approve", methods=["POST"])
@login_required
def approve(asset_id):
    asset = MediaAsset.query.get_or_404(asset_id)
    form = ApproveForm()
    if form.validate_on_submit():
        asset.status = "approved"
        add_review_note(asset, "approved", clean_optional(form.note.data))
        db.session.commit()
        flash("Asset approved.", "success")
    else:
        flash("Approval could not be saved.", "danger")
    return redirect(url_for("review.index"))


@review_bp.route("/<int:asset_id>/reject", methods=["POST"])
@login_required
def reject(asset_id):
    asset = MediaAsset.query.get_or_404(asset_id)
    form = RejectForm()
    if form.validate_on_submit():
        asset.status = "rejected"
        add_review_note(asset, "rejected", form.note.data.strip())
        db.session.commit()
        flash("Asset rejected.", "warning")
    else:
        flash("A rejection note is required.", "danger")
    return redirect(url_for("review.index"))


def add_review_note(asset, decision, note):
    db.session.add(
        ReviewNote(
            media_asset=asset,
            user_id=current_user.id,
            decision=decision,
            note=note,
        )
    )


def clean_optional(value):
    if not value:
        return None
    cleaned = value.strip()
    return cleaned or None
