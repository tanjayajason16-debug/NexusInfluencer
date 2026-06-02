from flask_wtf import FlaskForm
from wtforms import SubmitField, TextAreaField
from wtforms.validators import DataRequired, Optional


class ApproveForm(FlaskForm):
    note = TextAreaField("Approval note", validators=[Optional()])
    submit = SubmitField("Approve")


class RejectForm(FlaskForm):
    note = TextAreaField("Rejection note", validators=[DataRequired()])
    submit = SubmitField("Reject")
