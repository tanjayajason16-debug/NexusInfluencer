from datetime import datetime, timezone

from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from app.extensions import db


MEDIA_STATUSES = ("draft", "approved", "rejected", "ready_to_post", "posted")
MEDIA_TYPES = ("image", "video")
POST_STATUSES = ("planned", "ready", "posted", "cancelled")


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    is_admin = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Persona(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False, index=True)
    niche = db.Column(db.String(160), nullable=False)
    bio = db.Column(db.Text, nullable=True)
    personality = db.Column(db.Text, nullable=True)
    visual_style = db.Column(db.Text, nullable=True)
    caption_tone = db.Column(db.Text, nullable=True)
    reference_notes = db.Column(db.Text, nullable=True)
    reference_image_path = db.Column(db.String(500), nullable=True)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    media_assets = db.relationship("MediaAsset", back_populates="persona", cascade="all, delete-orphan")
    captions = db.relationship("Caption", back_populates="persona", cascade="all, delete-orphan")
    posts = db.relationship("Post", back_populates="persona", cascade="all, delete-orphan")


class MediaAsset(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    persona_id = db.Column(db.Integer, db.ForeignKey("persona.id"), nullable=False, index=True)
    media_type = db.Column(db.String(20), nullable=False, index=True)
    file_path = db.Column(db.String(500), nullable=False)
    original_filename = db.Column(db.String(255), nullable=False)
    status = db.Column(db.String(40), default="draft", nullable=False, index=True)
    prompt = db.Column(db.Text, nullable=True)
    caption_idea = db.Column(db.Text, nullable=True)
    generation_notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    persona = db.relationship("Persona", back_populates="media_assets")
    captions = db.relationship("Caption", back_populates="media_asset")
    posts = db.relationship("Post", back_populates="media_asset")
    review_notes = db.relationship("ReviewNote", back_populates="media_asset", cascade="all, delete-orphan")


class Caption(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    persona_id = db.Column(db.Integer, db.ForeignKey("persona.id"), nullable=False, index=True)
    media_asset_id = db.Column(db.Integer, db.ForeignKey("media_asset.id"), nullable=True, index=True)
    text = db.Column(db.Text, nullable=False)
    tone = db.Column(db.String(120), nullable=True)
    hashtags = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    persona = db.relationship("Persona", back_populates="captions")
    media_asset = db.relationship("MediaAsset", back_populates="captions")
    posts = db.relationship("Post", back_populates="caption")


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    persona_id = db.Column(db.Integer, db.ForeignKey("persona.id"), nullable=False, index=True)
    media_asset_id = db.Column(db.Integer, db.ForeignKey("media_asset.id"), nullable=True, index=True)
    caption_id = db.Column(db.Integer, db.ForeignKey("caption.id"), nullable=True, index=True)
    platform = db.Column(db.String(80), default="Instagram", nullable=False)
    scheduled_for = db.Column(db.DateTime, nullable=True, index=True)
    status = db.Column(db.String(40), default="planned", nullable=False, index=True)
    posted_at = db.Column(db.DateTime, nullable=True)
    manual_posting_notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    persona = db.relationship("Persona", back_populates="posts")
    media_asset = db.relationship("MediaAsset", back_populates="posts")
    caption = db.relationship("Caption", back_populates="posts")


class ReviewNote(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    media_asset_id = db.Column(db.Integer, db.ForeignKey("media_asset.id"), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False, index=True)
    decision = db.Column(db.String(40), nullable=False, index=True)
    note = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    media_asset = db.relationship("MediaAsset", back_populates="review_notes")
    user = db.relationship("User")
