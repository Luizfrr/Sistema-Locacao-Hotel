from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SubmitField, HiddenField
from wtforms.validators import DataRequired, Length

class BookingForm(FlaskForm):
    name = StringField('Nome', validators=[DataRequired(message="O nome é obrigatório"),Length(min=3, max=50, message="O nome deve ter entre 3 e 50 caracteres")])

    telephone = StringField('Telefone', validators=[DataRequired(message="O telefone é obrigatório"),Length(min=10, max=20, message="Telefone inválido")])

    room_type = SelectField('Tipo de Quarto', choices=[], validate_choice=False)

    entry_date = SelectField('Data de Entrada', validators=[DataRequired(message="Selecione a data de entrada")])

    exit_date = SelectField('Data de Saída', validators=[DataRequired(message="Selecione a data de saída")])

    total_value = HiddenField('Valor Total', validators=[DataRequired()])

    submit = SubmitField('Reservar')