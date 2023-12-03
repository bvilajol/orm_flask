from flask_wtf import FlaskForm
from wtforms import (StringField,
                     #TextAreaField,
                     IntegerField,
                     #BooleanField,
                     #RadioField,
                     #FormField,
                     #EmailField,
                     #SubmitField,
                     #SelectMultipleField,
                     validators,
                     )

from wtforms.validators import InputRequired, Length

class EnvironmentForm(FlaskForm):
    name = StringField('Name', validators=[InputRequired(), Length(min=8, max=24)])
    fmg_name = StringField('FMG name', validators=[InputRequired(), Length(min=8, max=16)])
    faz_name = StringField('FAZ name', validators=[InputRequired(), Length(min=8, max=16)])
    az_keyvault = StringField('Azure keyvault', validators=[InputRequired(), Length(min=8, max=16)])
    fmg_keyvault = StringField('FMG keyvault', validators=[InputRequired(), Length(min=8, max=16)])

class NetworkForm(FlaskForm):
    name = StringField('Name', validators=[InputRequired(), Length(min=4, max=8)])
    code = StringField('Site Code', validators=[InputRequired(), Length(min=3, max=3)])
    subnet = StringField('Subnet', validators=[InputRequired(), Length(min=8, max=32)])