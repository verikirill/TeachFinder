import datetime
import sqlalchemy
from sqlalchemy_serializer import SerializerMixin

from .db_session import SqlAlchemyBase
from sqlalchemy import orm
from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash
from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, TextAreaField, SubmitField, EmailField, FieldList
from wtforms.validators import DataRequired


class RegisterForm(FlaskForm):
    email = EmailField('Почта', validators=[DataRequired()])
    number = StringField('Номер телефона')
    password = PasswordField('Пароль', validators=[DataRequired()])
    password_again = PasswordField('Повторите пароль', validators=[DataRequired()])
    name = StringField('Имя', validators=[DataRequired()])
    surname = StringField('Фамилия', validators=[DataRequired()])
    organiz = StringField('Название организации')
    patronymic = StringField('Отчество', validators=[DataRequired()])
    submit = SubmitField('Войти')


class User(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = 'users'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    email = sqlalchemy.Column(sqlalchemy.String,
                              index=True, unique=True, nullable=True)
    number = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    surname = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    patronymic = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    organiz = sqlalchemy.Column(sqlalchemy.String, nullable=True, default='None')
    hashed_password = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    avatar = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    role = sqlalchemy.Column(sqlalchemy.String)
    modified_date = sqlalchemy.Column(sqlalchemy.DateTime,
                                      default=datetime.datetime.now)
    avatar = sqlalchemy.Column(sqlalchemy.String, nullable=True, default='static/img/profile.jpg')
    summaries = orm.relationship("Summaries", back_populates='user')
    vacansy = orm.relationship("Vacansies", back_populates='user')

    def __repr__(self):
        return f'User(email={self.email})'

    def set_password(self, password):
        self.hashed_password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.hashed_password, password)
