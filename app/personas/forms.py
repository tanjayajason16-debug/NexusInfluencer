from flask_wtf import FlaskForm
from wtforms import BooleanField, StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length, Optional


class PersonaForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired(), Length(max=120)])
    niche = StringField("Niche", validators=[DataRequired(), Length(max=160)])
    bio = TextAreaField("Bio", validators=[Optional()])
    personality = TextAreaField("Personality", validators=[Optional()])
    visual_style = TextAreaField("Visual style", validators=[Optional()])
    caption_tone = TextAreaField("Caption tone", validators=[Optional()])
    reference_notes = TextAreaField("Reference notes", validators=[Optional()])
    reference_image_path = StringField("Reference image path", validators=[Optional(), Length(max=500)])
    is_active = BooleanField("Active", default=True)
    submit = SubmitField("Save persona")
