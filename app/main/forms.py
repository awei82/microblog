from flask import request
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, FileField
from wtforms.validators import ValidationError, DataRequired, Length
from app.models import User
import os


class EditProfileForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired()])
    about_me = TextAreaField('About me', validators=[Length(min=0, max=140)])
    profile_photo = FileField('Profile Photo (please keep to no larger than 256px x 256px)')
    submit = SubmitField('Submit')

    def __init__(self, original_username, original_email, *args, **kwargs):
        super(EditProfileForm, self).__init__(*args, **kwargs)
        self.original_username = original_username
        self.original_email = original_email

    def validate_username(self, username):
        if username.data != self.original_username:
            user = User.query.filter_by(username=self.username.data).first()
            if user is not None:
                raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        print('### validate_email ###')
        if email.data != self.original_email:
            user = User.query.filter_by(email=self.email.data).first()
            if user is not None:
                raise ValidationError('Please use a different email.')

    def validate_profile_photo(self, profile_photo):
        print('### vaildate_profile_photo ###')

        ALLOWED_EXTENSIONS = {'jpg', 'jpeg'}
        if profile_photo.data.filename.rsplit('.', 1)[-1].lower() not in ALLOWED_EXTENSIONS:
            raise ValidationError(f'Only allowed extensions are: {ALLOWED_EXTENSIONS}.')

        file = profile_photo.data
        file.seek(0, os.SEEK_END)
        file_length = file.tell()
        file.seek(0,0)
        if file_length > 100000:
            raise ValidationError('Image too large. Must be under 100KB')

class EmptyForm(FlaskForm):
    submit = SubmitField('Submit')


class PostForm(FlaskForm):
    post = TextAreaField('Say something', validators=[DataRequired(), Length(min=1, max=140)])
    submit = SubmitField('Submit')


class EditPostForm(FlaskForm):
    post = TextAreaField('Edit post', validators=[DataRequired(), Length(min=1, max=140)])
    submit = SubmitField('Submit')
    delete = SubmitField('Delete Post', render_kw={'onclick': "return confirm('Confirm delete?');"})
    # cancel = SubmitField('Cancel Editing')


class SearchForm(FlaskForm):
    q = StringField('Search', validators=[DataRequired()])

    def __init__(self, *args, **kwargs):
        if 'formdata' not in kwargs:
            kwargs['formdata'] = request.args
        if 'csrf_enabled' not in kwargs:
            kwargs['csrf_enabled'] = False
        super(SearchForm, self).__init__(*args, **kwargs)


class MessageForm(FlaskForm):
    message = TextAreaField('Message', validators=[
        DataRequired(), Length(min=0, max=140)])
    submit = SubmitField('Submit')
