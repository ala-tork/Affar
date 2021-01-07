from flask_wtf import FlaskForm
from wtforms import StringField ,PasswordField 
from wtforms.validators import DataRequired , Length, Email ,ValidationError

class adminlogin(FlaskForm):
    email=StringField(label="email :", validators=[DataRequired()])
    password = PasswordField(label="password :", validators=[DataRequired()])
