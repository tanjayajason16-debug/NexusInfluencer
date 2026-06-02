from flask_wtf import FlaskForm
from wtforms import DateTimeLocalField, SelectField, StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length, Optional

from app.models import POST_STATUSES


class CaptionForm(FlaskForm):
    persona_id = SelectField("Persona", coerce=int, validators=[DataRequired()])
    media_asset_id = SelectField("Media asset", coerce=int, validators=[Optional()])
    prompt = TextAreaField("AI prompt", validators=[Optional()])
    text = TextAreaField("Caption", validators=[DataRequired()])
    tone = StringField("Tone", validators=[Optional(), Length(max=120)])
    hashtags = TextAreaField("Hashtags", validators=[Optional()])
    submit = SubmitField("Save caption")


class PostForm(FlaskForm):
    persona_id = SelectField("Persona", coerce=int, validators=[DataRequired()])
    media_asset_id = SelectField("Media asset", coerce=int, validators=[Optional()])
    caption_id = SelectField("Caption", coerce=int, validators=[Optional()])
    platform = StringField("Platform", validators=[DataRequired(), Length(max=80)])
    scheduled_for = DateTimeLocalField("Scheduled for", format="%Y-%m-%dT%H:%M", validators=[Optional()])
    status = SelectField(
        "Status",
        choices=[(status, status.replace("_", " ").title()) for status in POST_STATUSES],
        validators=[DataRequired()],
    )
    manual_posting_notes = TextAreaField("Manual posting notes", validators=[Optional()])
    submit = SubmitField("Save post")
