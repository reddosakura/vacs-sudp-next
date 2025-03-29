import datetime
from datetime import date
import wtforms
from flask_wtf import FlaskForm
from wtforms import widgets
from wtforms.fields.simple import StringField, PasswordField, TextAreaField, SubmitField, FileField, HiddenField
from wtforms.fields import DateField, MultipleFileField, FormField, FieldList, BooleanField, TimeField
from wtforms.fields.choices import SelectField, RadioField, SelectMultipleField
from wtforms.validators import DataRequired, Optional, Regexp
from flask_wtf.file import FileAllowed

TIME_INTERVALS = [
    ("1", "С 5:00 ДО 15:00"),
    ("2", "С 5:00 ДО 18:00"),
    ("3", "С 5:00 ДО 21:30"),
    ("4", "C 7:30 ДО 21:00"),
    ("5", "С 9:00 ДО 12:00"),
    ("6", "С 9:00 ДО 17:00"),
    ("7", "С 12:00 ДО 15:00"),
    ("8", "С 15:00 ДО 17:15"),
    ("9", "КРУГЛОСУТОЧНО"),
]

TYPES = [
    ("1", "ОДНОРАЗОВАЯ"),
    ("2", "МНОГОРАЗОВАЯ"),
]

SPECTYPES = [
    ("1", "ДРУГОЕ"),
    ("2", "СКОРАЯ ПОМОЩЬ"),
    ("3", "ПОЖАРНАЯ СЛУЖБА"),
    ("4", "ПОЛИЦИЯ"),
    ("5", "ГАЗОВАЯ СЛУЖБА"),
]

PASSAGE_MODES = [
    ("1", "По всем дням"),
    ("2", "Только по будням"),
    ("3", "Только по выходным"),
]


ROLES = [
    ("0", "ОХРАНА"),
    ("1", "ЗАЯВИТЕЛЬ"),
    ("2", "ОГРАНИЧЕННОЕ АДМИНИСТРИРОВАНИЕ"),
    ("3", "АДМИНИСТРАТОР"),
    ("4", "СУПЕРПОЛЬЗОВАТЕЛЬ"),
]

class MultiCheckboxField(SelectMultipleField):
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()


class AuthForm(FlaskForm):
    login = StringField('name', validators=[DataRequired()])
    password = PasswordField('password', validators=[DataRequired()])


class ProcessRequestForm(FlaskForm):
    # comment = TextAreaField('comment', render_kw={'data-simplebar': None, 'data-simplebar-auto-hide': False})
    comment = TextAreaField('comment')
    request_id = HiddenField("request_id")
    allow = SubmitField('УТВЕРДИТЬ')
    deny = SubmitField('ОТКЛОНИТЬ')
    approve = SubmitField('СОГЛАСОВАТЬ')


class VisitorSubForm(wtforms.Form):
    lastname = StringField('lastname', validators=[DataRequired()])
    name = StringField('name', validators=[DataRequired()])
    patronymic = StringField('patronymic')
    v_id = StringField("id")


class CarSubForm(wtforms.Form):
    carmodel = StringField('model', validators=[DataRequired()])
    govern_num = StringField('govern_num', validators=[DataRequired()])
    c_id = StringField("id")
    # visitor = SelectField("visitor", coerce=int,  validate_choice=False)


class RequestForm(FlaskForm):
    organization = StringField('organisation')
    comment = TextAreaField('comment')
    type = RadioField('type', coerce=str)
    time_interval = SelectField('time_interval',
                                choices=TIME_INTERVALS, default="4")
    passage_mode = SelectField('passage_mode', coerce=str)
    from_date = DateField("from_date", validators=[DataRequired()], default=date.today)
    to_date = DateField("to_date", validators=[DataRequired()], default=date.today)
    contract = StringField('contract')

    visitors_list = FieldList(FormField(VisitorSubForm))
    cars_list = FieldList(FormField(CarSubForm))

    add_files_btn = MultipleFileField(validators=[FileAllowed(['pdf'], 'Только pdf')])
    create_btn = SubmitField('СОЗДАТЬ')


class UploadListForm(FlaskForm):
    list_file = FileField()
    upload = SubmitField('ВЫГРУЗИТЬ ДАННЫЕ')


class VisitorsPassageForm(FlaskForm):
    visitors_check_group = MultiCheckboxField("visitors", coerce=str, validate_choice=False)
    pass_submit = SubmitField("ПРОПУСТИТЬ")

class CarsPassageForm(FlaskForm):
    cars_check_group = MultiCheckboxField("cars", coerce=str, validate_choice=False)
    pass_submit = SubmitField("ПРОПУСТИТЬ")


class SearchForm(FlaskForm):
    search_field = StringField()
    search_submit = SubmitField("ПОИСК")


class ExitForm(FlaskForm):
    cars_on_terr_field = RadioField("cars_on_territory", coerce=str, validate_choice=False)
    exit_submit = SubmitField("ВЫЕЗД")


class SpecTransportForm(FlaskForm):
    model_field = StringField('model', validators=[DataRequired()])
    govern_num_field = StringField('model', validators=[DataRequired()])
    type_field = SelectField('type', coerce=str)
    pass_spec_submit = SubmitField("ПРОПУСТИТЬ")


class FilterSearchForm(FlaskForm):
    search_field = StringField(render_kw={"placeholder": "ВВЕДИТЕ ПОИСКОВОЕ ЗНАЧЕНИЕ"})
    filter_fdate = DateField("filter_fdate", default=date.today)
    filter_tdate = DateField("filter_tdate", default=date.today)
    filter_ftime = TimeField("filter_ftime", default=datetime.datetime.strptime("00:00:00", "%H:%M:%S").time())
    filter_ttime = TimeField("filter_ttime", default=datetime.datetime.strptime("23:59:00", "%H:%M:%S").time())
    apply_button = SubmitField("ПОИСК ПО УКАЗАННЫМ КРИТЕРИЯМ")


class RecallForm(FlaskForm):
    recall_button = SubmitField("ОТОЗВАТЬ")


class DeleteRequestForm(FlaskForm):
    delete_button = SubmitField("УДАЛИТЬ")


class UpdateRequestForm(FlaskForm):
    type = SelectField('type',
                       choices=TYPES)
    organization = StringField('organization')
    comment = TextAreaField('comment')
    from_date = DateField("from_date", validators=[DataRequired()], default=date.today)
    to_date = DateField("to_date", validators=[DataRequired()], default=date.today)
    time_interval = SelectField('time_interval',
                                choices=TIME_INTERVALS)
    contract_name = StringField('contract')
    passage_mode = SelectField('passage_mode',
                               choices=PASSAGE_MODES)
    visitor = FieldList(FormField(VisitorSubForm))
    car = FieldList(FormField(CarSubForm))
    create_btn = SubmitField('СОХРАНИТЬ ИЗМЕНЕНИЯ')
    add_files_btn = MultipleFileField(validators=[FileAllowed(['pdf'], 'Только pdf')])


class CreateUserForm(FlaskForm):
    lastname = StringField('lastname', validators=[DataRequired()])
    name = StringField('name', validators=[DataRequired()])
    patronymic = StringField('patronymic')
    speciality = StringField('specility', validators=[DataRequired()])
    role = SelectField('roles', coerce=str)
    login = StringField('login', validators=[DataRequired()])
    password = StringField('password', validators=[DataRequired()])
    create_btn = SubmitField("СОЗДАТЬ")


class UpdateUserForm(FlaskForm):
    lastname = StringField('lastname', validators=[DataRequired()])
    name = StringField('name', validators=[DataRequired()])
    patronymic = StringField('patronymic')
    speciality = TextAreaField('specility', validators=[DataRequired()])
    role = SelectField('roles', choices=ROLES)
    login = StringField('login', validators=[DataRequired()])
    password = StringField('password', validators=[Optional()])
    selector = BooleanField("ИЗМЕНИТЬ ЛОГИН ИЛИ ПАРОЛЬ")
    edit_btn = SubmitField("СОХРАНИТЬ ИЗМЕНЕНИЯ")
    delete_btn = SubmitField("УДАЛИТЬ ПОЛЬЗОВАТЕЛЯ")
