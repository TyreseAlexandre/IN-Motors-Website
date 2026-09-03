from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed
from wtforms import (
    BooleanField,
    DecimalField,
    IntegerField,
    MultipleFileField,
    PasswordField,
    SelectField,
    StringField,
    TextAreaField,
)
from wtforms.fields import EmailField
from wtforms.validators import DataRequired, Email, InputRequired, Length, NumberRange, Optional

from models import VEHICLE_STATUSES

CURRENT_YEAR_MAX = 2027
ALLOWED_IMAGE_EXTENSIONS = ["jpg", "jpeg", "png", "webp"]


class LoginForm(FlaskForm):
    email = EmailField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Palavra-passe", validators=[DataRequired()])


class VehicleForm(FlaskForm):
    brand = StringField("Marca", validators=[DataRequired(message="A marca é obrigatória."), Length(max=100)])
    model = StringField("Modelo", validators=[DataRequired(message="O modelo é obrigatório."), Length(max=100)])
    year = IntegerField(
        "Ano",
        validators=[InputRequired(message="O ano é obrigatório."), NumberRange(min=1980, max=CURRENT_YEAR_MAX)],
    )
    price = DecimalField(
        "Preço (MZN)",
        validators=[InputRequired(message="O preço é obrigatório."), NumberRange(min=0)],
        places=2,
    )
    mileage = IntegerField("Quilometragem (km)", validators=[Optional(), NumberRange(min=0)])
    transmission = SelectField(
        "Transmissão",
        choices=[("", "Selecione"), ("Automática", "Automática"), ("Manual", "Manual")],
        validators=[Optional()],
    )
    fuel_type = SelectField(
        "Combustível",
        choices=[
            ("", "Selecione"),
            ("Gasolina", "Gasolina"),
            ("Gasóleo", "Gasóleo"),
            ("Híbrido", "Híbrido"),
            ("Elétrico", "Elétrico"),
        ],
        validators=[Optional()],
    )
    engine = StringField("Motor", validators=[Optional(), Length(max=100)])
    color = StringField("Cor", validators=[Optional(), Length(max=50)])
    location = StringField("Localização", validators=[Optional(), Length(max=100)])
    description = TextAreaField("Descrição", validators=[Optional(), Length(max=4000)])

    status = SelectField(
        "Estado",
        choices=[(s, s) for s in VEHICLE_STATUSES],
        validators=[DataRequired()],
    )
    is_featured = BooleanField("Destaque na página inicial")
    is_visible = BooleanField("Publicado (visível no site)")

    photos = MultipleFileField(
        "Fotos",
        validators=[FileAllowed(ALLOWED_IMAGE_EXTENSIONS, "Apenas imagens JPG, PNG ou WEBP são permitidas.")],
    )


class DeleteImageForm(FlaskForm):
    pass


class ActionForm(FlaskForm):
    """Empty form used purely to carry a CSRF token on quick-action buttons."""
    pass
