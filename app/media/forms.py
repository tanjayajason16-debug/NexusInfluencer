from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileField, FileRequired
from wtforms import SelectField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Optional

from app.models import MEDIA_STATUSES


ALLOWED_MEDIA_EXTENSIONS = ("jpg", "jpeg", "png", "webp", "mp4", "mov", "webm")


class MediaAssetForm(FlaskForm):
    persona_id = SelectField("Persona", coerce=int, validators=[DataRequired()])
    file = FileField(
        "Image or video",
        validators=[
            FileRequired(),
            FileAllowed(ALLOWED_MEDIA_EXTENSIONS, "Upload an image or video file."),
        ],
    )
    prompt = TextAreaField("Prompt", validators=[Optional()])
    caption_idea = TextAreaField("Caption idea", validators=[Optional()])
    generation_notes = TextAreaField("Generation notes", validators=[Optional()])
    submit = SubmitField("Upload asset")


class MediaStatusForm(FlaskForm):
    status = SelectField(
        "Status",
        choices=[(status, status.replace("_", " ").title()) for status in MEDIA_STATUSES],
        validators=[DataRequired()],
    )
    submit = SubmitField("Update status")
