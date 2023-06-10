import os

from flask import Flask, render_template, redirect, request, abort, jsonify
from data import db_session
from data.loginfrom import LoginForm
from werkzeug.security import check_password_hash, generate_password_hash
from data.users import User
from data.summaries import SummariesForm, Summaries
from data.vacansys import VacansiesForm, Vacansies
from flask_login import LoginManager, login_required, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, EmailField
from wtforms.validators import DataRequired
from flask_login import login_user
from data.users import RegisterForm
import requests
from flask_restful import reqparse, abort, Api, Resource
from flask import make_response
from flask import url_for
from werkzeug.utils import secure_filename
from PIL import Image
import random
import smtplib

UPLOAD_FOLDER = 'static/uploads/'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])

app = Flask(__name__)
api = Api(app)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
login_manager = LoginManager()
login_manager.init_app(app)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024


# Проверка, на расширение файла #
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


# Вспомогательная функция для загрузки пользователей #
@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


# Начальная Страница #
@app.route("/")
def index():
    db_sess = db_session.create_session()
    summaries = db_sess.query(Summaries)
    if current_user.is_authenticated:
        summaries = db_sess.query(Summaries).filter(
            (Summaries.user == current_user))
    return render_template("test.html")


# Вход в аккаунт #
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/redirect-people")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)


# РЕГИСТРАЦИЯ ОРГАНИЗАЦИИ #
@app.route('/register-organiz', methods=['GET', 'POST'])
def reqister_organiz():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пользователь с таким адресом электронной почты уже зарегистрирован")
        user = User(
            email=form.email.data,
            number=form.number.data,
            name=form.name.data,
            surname=form.surname.data,
            patronymic=form.patronymic.data,
            organiz=form.organiz.data,
            avatar='static/img/profile.jpg',
            role='organiz',
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form,
                           title2='Регистрация для представителя организации')


# РЕГИСТРАЦИЯ ДЛЯ УЧИТЕЛЯ #
@app.route('/register-teacher', methods=['GET', 'POST'])
def reqister_teacher():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пользователь с таким адресом электронной почты уже зарегистрирован")
        user = User(
            email=form.email.data,
            number=form.number.data,
            name=form.name.data,
            surname=form.surname.data,
            patronymic=form.patronymic.data,
            avatar='static/img/profile.jpg',
            role='teacher',
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form,
                           title2='Регистрация для учителя')


# Выход из аккаунта #
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/login")


# ///////////////////// #
### Блок про резюме ## #
# /////////////////////#
@app.route('/add-summary', methods=['GET', 'POST'])
@login_required
def add_summary():
    db_sess = db_session.create_session()
    form = SummariesForm()
    user = db_sess.query(User)
    user_status = user.filter((User.email == current_user.email)).first()
    user_status = user_status.role
    if user_status == 'organiz':
        return render_template('youarenotteacher.html')
    else:
        if form.validate_on_submit():
            db_sess = db_session.create_session()
            summaries = Summaries()
            summaries.data_rozdeniya = form.data_rozdeniya.data
            summaries.semeynoe_polozhenie = form.semeynoe_polozhenie.data
            summaries.adress = form.adress.data
            summaries.obrazovanie = form.obrazovanie.data
            summaries.dop_obrazovanie = form.dop_obrazovanie.data
            summaries.experience = form.experience.data
            summaries.dop_infa = form.experience.data
            summaries.job = form.job.data
            summaries.url_on_files = form.url_on_files.data
            current_user.summaries.append(summaries)
            db_sess.merge(current_user)
            db_sess.commit()
            return redirect('/redirect-people')
        return render_template('add_summary.html', title='Создание Резюме', form=form)


@app.route('/summary/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_summaries(id):
    form = SummariesForm()
    if request.method == "GET":
        db_sess = db_session.create_session()
        summaries = db_sess.query(Summaries).filter(Summaries.id == id,
                                                    Summaries.user_id == current_user.id
                                                    ).first()
        if summaries and summaries is not None:
            form.data_rozdeniya.data = summaries.data_rozdeniya
            form.semeynoe_polozhenie.data = summaries.semeynoe_polozhenie
            form.adress.data = summaries.adress
            form.job.data = summaries.job
            form.obrazovanie.data = summaries.obrazovanie
            form.experience.data = summaries.experience
            form.dop_infa.data = summaries.dop_infa
            form.url_on_files.data = summaries.url_on_files
        else:
            return redirect('/takogo-rezume-net')
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        summaries = db_sess.query(Summaries).filter(Summaries.id == id,
                                                    Summaries.user_id == current_user.id
                                                    ).first()
        if summaries and summaries is not None:
            summaries.data_rozdeniya = form.data_rozdeniya.data
            summaries.semeynoe_polozhenie = form.semeynoe_polozhenie.data
            summaries.adress = form.adress.data
            summaries.obrazovanie = form.obrazovanie.data
            summaries.experience = form.experience.data
            summaries.dop_infa = form.dop_infa.data
            summaries.job = form.job.data
            db_sess.commit()
            return redirect('/redirect-people')
        else:
            return redirect('/takogo-rezume-net')
    return render_template('add_summary.html',
                           title='Редактирование Резюме',
                           form=form
                           )


@app.route('/obzor-summary/<int:id>', methods=['GET', 'POST'])
@login_required
def obzor_summary(id):
    db_sess = db_session.create_session()
    item = db_sess.query(Summaries).filter(Summaries.id == id).first()
    user = db_sess.query(User).filter(User.id == item.user_id).first()
    avatar = user.avatar[7:]
    return render_template('obzor_summary.html', user=user, item=item, avatar=avatar, current_user1=current_user)


@app.route('/summaries-delete/<int:id>', methods=['GET', 'POST'])
@login_required
def summaries_delete(id):
    db_sess = db_session.create_session()
    summaries = db_sess.query(Summaries).filter(Summaries.id == id,
                                                Summaries.user_id == current_user.id
                                                ).first()
    if summaries:
        db_sess.delete(summaries)
        db_sess.commit()
    else:
        return redirect('/redirect-people')
    return redirect('/redirect-people')


# ///////////////////// #
### Конец блока про резюме ## #
# /////////////////////#


# ///////////////////// #
### Блок про вакансии ## #
# /////////////////////#
@app.route('/add-vacancy', methods=['GET', 'POST'])
@login_required
def add_vacansy():
    db_sess = db_session.create_session()
    form = VacansiesForm()
    user = db_sess.query(User)
    user_status = user.filter((User.email == current_user.email)).first()
    user_status = user_status.role
    if user_status == 'teacher':
        return render_template('youarenotteacher.html')
    else:
        if form.validate_on_submit():
            db_sess = db_session.create_session()
            vacansy = Vacansies()
            vacansy.general_info = form.general_info.data
            vacansy.job_responsibilities = form.job_responsibilities.data
            vacansy.candidat_requirements = form.candidat_requirements.data
            vacansy.key_skills = form.key_skills.data
            vacansy.additions_candidat_requirements = form.additions_candidat_requirements.data
            vacansy.url_on_files = form.url_on_files.data
            current_user.vacansy.append(vacansy)
            db_sess.merge(current_user)
            db_sess.commit()
            return redirect('/redirect-people')
        return render_template('add_vacansy.html', title='Создание Вакансии', form=form)


@app.route('/vacansy/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_vacansy(id):
    form = VacansiesForm()
    if request.method == "GET":
        db_sess = db_session.create_session()
        vacansy = db_sess.query(Vacansies).filter(Vacansies.id == id).first()
        if (vacansy and vacansy is not None) and vacansy.user_id == current_user.id:
            form.general_info.data = vacansy.general_info
            form.job_responsibilities.data = vacansy.job_responsibilities
            form.candidat_requirements.data = vacansy.candidat_requirements
            form.key_skills.data = vacansy.key_skills
            form.additions_candidat_requirements.data = vacansy.additions_candidat_requirements
            form.url_on_files.data = vacansy.url_on_files
        else:
            return redirect('/takoy-vacansii-net')
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        vacansy = db_sess.query(Vacansies).filter(Vacansies.id == id,
                                                  Vacansies.user_id == current_user.id
                                                  ).first()
        if vacansy and vacansy is not None:
            vacansy.general_info = form.general_info.data
            vacansy.job_responsibilities = form.job_responsibilities.data
            vacansy.candidat_requirements = form.candidat_requirements.data
            vacansy.key_skills = form.key_skills.data
            vacansy.additions_candidat_requirements = form.additions_candidat_requirements.data
            vacansy.url_on_files = form.url_on_files.data
            db_sess.commit()
            return redirect('/redirect-people')
        else:
            return redirect('/takoy-vacansii-net')
    return render_template('add_vacansy.html',
                           title='Редактирование Вакансии',
                           form=form
                           )


@app.route('/vacansy_delete/<int:id>', methods=['GET', 'POST'])
@login_required
def vacansy_delete(id):
    db_sess = db_session.create_session()
    vacansy = db_sess.query(Vacansies).filter(Vacansies.id == id,
                                              Vacansies.user_id == current_user.id
                                              ).first()
    if vacansy:
        db_sess.delete(vacansy)
        db_sess.commit()
    else:
        return redirect('/redirect-people')
    return redirect('/redirect-people')


@app.route('/obzor-vacansy/<int:id>', methods=['GET', 'POST'])
@login_required
def obzor_vacansy(id):
    db_sess = db_session.create_session()
    item = db_sess.query(Vacansies).filter(Vacansies.id == id).first()
    user = db_sess.query(User).filter(User.id == item.user_id).first()
    avatar = user.avatar[7:]
    return render_template('obzor_vacansy.html', user=user, item=item, avatar=avatar, current_user1=current_user)


# ///////////////////// #
### Конец блока про вакансии ## #
# /////////////////////#


# Страница с контактной информацией #
@app.route('/contacts', methods=['GET'])
def contacts():
    db_sess = db_session.create_session()
    user = db_sess.query(User)
    return render_template('contacts.html')


# Страница, для выбора роли при регистрации #
@app.route('/register-choose', methods=['GET'])
def choose_role():
    if current_user.is_authenticated:
        return redirect('/redirect-people')
    else:
        return render_template('vybor_roli.html')


# Блок проверки на ошибки #
@app.errorhandler(404)
def not_found(error):
    # return make_response(jsonify({'error': 'Not found'}), 404)
    nomer = random.randint(1, 3)
    return render_template('4041.html', nomer=nomer)


# @app.errorhandler(500)
# def oshibka(error):
#     return redirect('/')

@app.errorhandler(401)
def oshibka(error):
    return redirect('/')


@app.errorhandler(400)
def bad_request(_):
    return render_template('badrequetsik.html')


# Конец блока проверки на ошибки #


# Редирект людей по ролям #
@app.route('/redirect-people', methods=['GET'])
@login_required
def redirect_people():
    db_sess = db_session.create_session()
    users = db_sess.query(User).filter(User.id == current_user.id).first()
    if users.role == 'teacher':
        return redirect('/find-job')
    else:
        return redirect('/find-worker')


# Страничка по поиску работиников #
@app.route('/find-worker', methods=['GET'])
@login_required
def find_worker():
    db_sess = db_session.create_session()
    user = db_sess.query(User)
    items = db_sess.query(Summaries).order_by(Summaries.id.desc()).all()
    if current_user.is_authenticated and current_user.role == 'organiz':
        return render_template('list_of_summaries.html', data=items, user=user, User=User, title2='Список Резюме')
    else:
        return render_template('/')


# Страничка по поиску Вакансий #
@app.route('/find-job', methods=['GET'])
@login_required
def find_job():
    db_sess = db_session.create_session()
    user = db_sess.query(User)
    items = db_sess.query(Vacansies).order_by(Vacansies.id.desc()).all()
    if current_user.is_authenticated and current_user.role == 'teacher':
        return render_template('list_of_vacansy.html', data=items, user=user, User=User, title2='Список Вакансий')
    else:
        return render_template('/')


## Мои Резюме и Мои Вакансии ##
@app.route('/my-summary', methods=['GET'])
@login_required
def my_summary():
    db_sess = db_session.create_session()
    user = db_sess.query(User)
    items = db_sess.query(Summaries).order_by(Summaries.id.desc()).filter(Summaries.user_id == current_user.id).all()
    if current_user.is_authenticated and current_user.role == 'teacher':
        return render_template('list_of_summaries.html', data=items, user=user, User=User, title2='Мои резюме')
    else:
        return render_template('/')


@app.route('/my-vacancy', methods=['GET'])
@login_required
def my_vacansy():
    db_sess = db_session.create_session()
    user = db_sess.query(User)
    items = db_sess.query(Vacansies).order_by(Vacansies.id.desc()).filter(Vacansies.user_id == current_user.id).all()
    if current_user.is_authenticated and current_user.role == 'organiz':
        return render_template('list_of_vacansy.html', data=items, user=user, User=User, title2='Мои Вакансии')
    else:
        return render_template('/')


## Конец блока Мои Резюме и Мои Вакансии #


# Профиль пользователя #
@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    db_sess = db_session.create_session()
    users = db_sess.query(User).filter(User.id == current_user.id).first()
    users_fio = users.surname.capitalize() + ' ' + users.name.capitalize() + ' ' + users.patronymic.capitalize()
    users_name = users.name.capitalize()
    users_organiz = ''
    if users.role == 'teacher':
        users_role = 'Преподаватель'
    else:
        users_role = f'Представитель организации:'
        users_organiz = users.organiz.capitalize()
    user_number = users.number
    users_email = users.email
    print(users.avatar)
    avatar = users.avatar
    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            db_sess = db_session.create_session()
            file.save(os.path.join(UPLOAD_FOLDER, str(current_user.id) + '.jpg'))
            db_sess = db_session.create_session()
            users = db_sess.query(User).filter(User.id == current_user.id).first()
            users.avatar = 'static/uploads/' + str(current_user.id) + '.jpg'
            db_sess.commit()
        return redirect('/profile')
    return render_template('profile2.html', fio=users_fio, name=users_name, email=users_email, role=users_role,
                           number=user_number, organiz=users_organiz, avatar=avatar, user=users)


@app.route('/edit-profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = RegisterForm()
    if request.method == "GET":
        db_sess = db_session.create_session()
        users = db_sess.query(User).filter(User.id == current_user.id).first()
        if users and users is not None:
            form.email.data = users.email
            form.number.data = users.number
            form.name.data = users.name
            form.surname.data = users.surname
            form.patronymic.data = users.patronymic
            if users.role != 'teacher':
                form.organiz.data = users.organiz
        else:
            return redirect('/ne-tvoi-profile')
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()
        users = db_sess.query(User).filter(User.id == current_user.id).first()
        if db_sess.query(User).filter(User.email == form.email.data).first() and users.email != form.email.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пользователь с таким адресом электронной почты уже зарегистрирован")
        users.email = form.email.data
        users.number = form.number.data
        users.name = form.name.data
        users.surname = form.surname.data
        users.patronymic = form.patronymic.data
        if users.role != 'teacher':
            users.organiz = form.organiz.data
        password = generate_password_hash(form.password.data)
        users.hashed_password = password
        db_sess.commit()
        return redirect('/profile')
    return render_template('register.html',
                           title='Редактирование Профиля',
                           form=form, url1='/profile')


@app.route('/edit-photo', methods=['GET', 'POST'])
@login_required
def edit_photo():
    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            db_sess = db_session.create_session()
            file.save(os.path.join(UPLOAD_FOLDER, str(current_user.id) + '.jpg'))
        return redirect('/profile')
    return render_template('edit_photo.html')


# Запуск приложения #
if __name__ == '__main__':
    db_session.global_init("db/alldata.db")
    app.run()
