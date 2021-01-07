from flask_wtf import FlaskForm
#from wtforms import StringField ,PasswordField ,SelectField ,validators,TextAreaField
#from wtforms.validators import DataRequired , Length, Email ,ValidationError,InputRequired
from wtforms import Form ,StringField, TextAreaField, PasswordField, validators, SelectField
from wtforms.validators import InputRequired,DataRequired, Length, Email, AnyOf,ValidationError ,EqualTo
from wtforms.fields import StringField
from wtforms.widgets import TextArea


def my_length_check(form, field):
    if len(field.data) < 5 :
        raise ValidationError('Field must at least 6 caractere')


class RegisterForm(Form):
    pseudo = StringField('pseudo :', [validators.DataRequired(),my_length_check],
                       render_kw={'autofocus': True, 'placeholder': 'Votre pseudo'})
    #username = StringField('', [validators.length(min=3, max=25)], render_kw={'placeholder': 'Username'})
    email = StringField('email :', [validators.DataRequired(),  validators.length(min=4, max=25)],
                       render_kw={'placeholder': 'Votre adresse email'})
    password = PasswordField('password :', [validators.length(min=3)],
                             render_kw={'placeholder': 'Password'})
    confirm = PasswordField('confirm :', [ validators.EqualTo('password',message="must be the same")],
                             render_kw={'placeholder': 'Confirmer votre mot de passe'})
    phone = StringField('Numéro de téléphone :', [validators.length(min=11, max=15)], render_kw={'placeholder': 'Votre Numéro Telephone'})

    msg= StringField('Votre Message : *', [validators.DataRequired()]  ,  widget=TextArea())

    body = StringField('', [validators.DataRequired()], render_kw={'autofocus': True})


       



class MyForm(FlaskForm):
    email=StringField(label="email :", validators=[DataRequired() ] , render_kw={"placeholder": "Votre adresse email"} )
    pseudo=StringField(label="pseudo :", validators=[DataRequired() ], render_kw={"placeholder": "Votre pseudo"})
    phone=StringField(label="Numéro de téléphone :", validators=[DataRequired() ] , render_kw={"placeholder": "Votre Numéro Telephone"})
    password = PasswordField(label="password :", validators=[DataRequired()], render_kw={"placeholder": "Votre mot de passe"})
    confirm = PasswordField(label="confirm :", validators=[DataRequired()], render_kw={"placeholder": "Confirmer votre mot de passe"})
    titre= StringField(label="Titre de l'annonce :", validators=[DataRequired() , Length(min=5) ] )
    categorie = SelectField(label="Categorie : ", validators=[DataRequired()], choices=[('', 'Informatique & Multimedia '),('Telephone','Telephone'),('ordinateur portable','ordinateur portable'),('accessoire informatique','accessoire informatique')] )
    ville = SelectField(label="Ville : ", validators=[DataRequired()], choices=[('', 'Choisir une Ville '),('Ariana','Ariana'),('Ben arous','Ben arous'),('Manouba','Manouba'),('Tunis 1','Tunis 1'),('Tunis 2','Tunis 2'),('Zaghwen','Zaghwen'),('Siliana','Siliana'),('El Kef','El Kef'),('Sidi bouzid','Sidi bouzid'),('Qerwen','Qerwen'),('Benzart','Benzart'),('Jandouba','Jandouba'),('Beja','Beja'),('Tbarka','Tbarka'),('Sousse','Sousse'),('Nabeul','Nabeul'),('Mahdia','Mahdia'),('Tatawin','Tatawin'),('Qasserine','Qasserine'),('Sfax','Sfax'),('Touezer','Touezer'),('Gafsa','Gafsa'),('Jerba','Jerba'),('Medenine','Medenine')] )
    description= TextAreaField(label="Description de l'annonce : ", validators=[DataRequired()])
    prix=StringField(label="Prix :", validators=[DataRequired() ] )