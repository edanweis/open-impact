from flask.ext.wtf import Form
from wtforms import TextField, TextAreaField, BooleanField, SelectField,\
    SubmitField
from wtforms.validators import Required, Email, Regexp
from wtforms import ValidationError
from flask.ext.pagedown.fields import PageDownField
from ..models import Role, User


class NameForm(Form):
    name = TextField('What is your name?', validators=[Required()])
    submit = SubmitField('Submit')


class EditProfileForm(Form):
    name = TextField('Real name')
    location = TextField('Location')
    about_me = TextAreaField('About me')
    submit = SubmitField('Submit')


class EditProfileAdminForm(Form):
    email = TextField('Email', validators=[Required(), Email()])
    username = TextField('Username', validators=[
        Required(), Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0, 'Usernames must \
        have only letters, numbers, dots or underscores')])
    confirmed = BooleanField('Confirmed')
    role = SelectField('Role', coerce=int)
    name = TextField('Real name')
    location = TextField('Location')
    about_me = TextAreaField('About me')
    submit = SubmitField('Submit')

    def __init__(self, user, *args, **kwargs):
        super(EditProfileAdminForm, self).__init__(*args, **kwargs)
        self.role.choices = [(role.id, role.name)
                             for role in Role.query.order_by(Role.name).all()]
        self.user = user

    def validate_email(self, field):
        if field.data != self.user.email and \
                User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered.')

    def validate_username(self, field):
        if field.data != self.user.username and \
                User.query.filter_by(username=field.data).first():
            raise ValidationError('Username already in use.')


class PostForm(Form):
    body = PageDownField("What's on your mind?", validators=[Required()])
    submit = SubmitField('Submit')


class CommentForm(Form):
    body = TextField('Enter your comment', validators=[Required()])
    submit = SubmitField('Submit')
