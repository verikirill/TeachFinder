import datetime
import sqlalchemy
from flask_login import UserMixin
from sqlalchemy import orm
from sqlalchemy_serializer import SerializerMixin

from .db_session import SqlAlchemyBase
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, DateField
from wtforms import BooleanField, SubmitField
from wtforms.validators import DataRequired


class Vacansies(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = 'vacansies'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    user_id = sqlalchemy.Column(sqlalchemy.Integer,
                                sqlalchemy.ForeignKey("users.id"))
    general_info = sqlalchemy.Column(sqlalchemy.Text)
    job_responsibilities = sqlalchemy.Column(sqlalchemy.Text)
    candidat_requirements = sqlalchemy.Column(sqlalchemy.Text)
    key_skills = sqlalchemy.Column(sqlalchemy.Text)
    additions_candidat_requirements = sqlalchemy.Column(sqlalchemy.Text)
    url_on_files = sqlalchemy.Column(sqlalchemy.Text, default='Пользователь не оставил ссылку на файлы')
    user = orm.relationship('User')


class VacansiesForm(FlaskForm):
    general_info = TextAreaField('Основная информация о вакансии', validators=[DataRequired()])
    job_responsibilities = TextAreaField('Должностная информация', validators=[DataRequired()])
    candidat_requirements = TextAreaField('Требования к кандидату', validators=[DataRequired()])
    key_skills = TextAreaField('Ключевые навыки', validators=[DataRequired()])
    additions_candidat_requirements = TextAreaField('Дополнительные требования к кандидату', default='Не имеются')
    url_on_files = StringField(
        'Вставьте сюда ссылку на дополнительные файлы, которые необходимы для вакансии, если такие имеются.',
        validators=[DataRequired()])
    submit = SubmitField('Опубликовать вакансию')
