from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import StringField, PasswordField, SelectField, TextAreaField, SubmitField, HiddenField
from wtforms.validators import DataRequired, Email, Length


class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Sign in")


class ImportForm(FlaskForm):
    kind = SelectField(
        "Dataset type",
        choices=[("results", "Assessment results"), ("attendance", "Attendance")],
        validators=[DataRequired()],
    )
    file = FileField("CSV file", validators=[FileRequired(), FileAllowed(["csv"], "CSV only")])
    submit = SubmitField("Preview")


class ConfirmImportForm(FlaskForm):
    job_id = HiddenField(validators=[DataRequired()])
    submit = SubmitField("Commit import")


class InterventionForm(FlaskForm):
    category = SelectField(
        "Category",
        choices=[
            ("attendance", "Attendance support"),
            ("academic", "Academic tutoring"),
            ("wellbeing", "Wellbeing check-in"),
            ("assignment", "Assignment completion"),
        ],
        validators=[DataRequired()],
    )
    notes = TextAreaField("Plan / notes", validators=[DataRequired(), Length(max=2000)])
    submit = SubmitField("Create intervention")


class FollowUpForm(FlaskForm):
    observation = TextAreaField("Observation", validators=[DataRequired(), Length(max=2000)])
    status = SelectField(
        "Status",
        choices=[("open", "Open"), ("in_progress", "In progress"), ("completed", "Completed")],
        validators=[DataRequired()],
    )
    outcome = SelectField(
        "Outcome",
        choices=[
            ("", "Not recorded"),
            ("improved", "Indicators improved"),
            ("stable", "Stable"),
            ("declined", "Indicators declined"),
            ("unknown", "Insufficient data"),
        ],
    )
    submit = SubmitField("Add follow-up")


class StudentSearchForm(FlaskForm):
    class Meta:
        csrf = False
    q = StringField("Search")
    class_id = SelectField("Class", choices=[], validate_choice=False)
    risk = SelectField(
        "Risk",
        choices=[("", "All"), ("high", "Predicted at risk"), ("low", "Predicted not at risk")],
        validate_choice=False,
    )
    submit = SubmitField("Filter")
