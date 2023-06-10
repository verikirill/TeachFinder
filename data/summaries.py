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


class Summaries(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = 'summaries'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    user_id = sqlalchemy.Column(sqlalchemy.Integer,
                                sqlalchemy.ForeignKey("users.id"))
    data_rozdeniya = sqlalchemy.Column(sqlalchemy.Date)
    semeynoe_polozhenie = sqlalchemy.Column(sqlalchemy.Text)
    adress = sqlalchemy.Column(sqlalchemy.Text)
    job = sqlalchemy.Column(sqlalchemy.Text)
    obrazovanie = sqlalchemy.Column(sqlalchemy.Text)
    dop_obrazovanie = sqlalchemy.Column(sqlalchemy.Text, default='Нет')
    experience = sqlalchemy.Column(sqlalchemy.Text, default='Нет')
    dop_infa = sqlalchemy.Column(sqlalchemy.Text, default='Нет')
    url_on_files = sqlalchemy.Column(sqlalchemy.Text, default='Пользователь не оставил ссылку на файлы')
    user = orm.relationship('User')

    def __repr__(self):
        return self.type_of_cours


class SummariesForm(FlaskForm):
    data_rozdeniya = DateField('Дата рождения', validators=[DataRequired()])
    semeynoe_polozhenie = StringField('Семейное положение', validators=[DataRequired()])
    adress = StringField('Адрес проживания', validators=[DataRequired()])
    job = StringField('Кем вы бы хотели работать', validators=[DataRequired()])
    obrazovanie = StringField('Ваше образование', validators=[DataRequired()])
    dop_obrazovanie = TextAreaField('Дополнительные источники вашей квалификации', default='Нет')
    experience = TextAreaField('Опыт работы', default='Не имеется')
    dop_infa = TextAreaField('Дополнительная информация', default='Не имеется')
    url_on_files = StringField('Ссылка на документы, подтверждающие вашу квалификацию', validators=[DataRequired()])
    submit = SubmitField('Создать Заявление')
