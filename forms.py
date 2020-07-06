from flask_babel import lazy_gettext as _l
from flask_wtf import FlaskForm
from wtforms import Form, IntegerField,DateTimeField,SelectField, FieldList, FormField, StringField, PasswordField, BooleanField, SubmitField, SelectMultipleField
from wtforms import validators, ValidationError, widgets
from cyber_role.models import User
from flask import escape, request,current_app
from cyber_role import user_manager
from flask_login import current_user

from wtforms.widgets import html5
from wtforms.fields.html5 import EmailField,IntegerRangeField


#Variables globales para el test_target y search filters

#minimos 2 modulos de LEARNING OBJECT Y MAXIMO 10 
n_min_range = [2,5]
n_max_range = [3,10]

diff_range_nk = 10

t_min = 1
t_max = 24000
c_min = 0
c_max = 10000
r_min = 0
r_max = 50


#Admin forms
class DescriptionKsaForm(FlaskForm):
    description = StringField(
        _l('Description'),
        validators=[
            validators.DataRequired(_l('Description is required')),
            validators.Length(min=1,max=350)
        ]
    )
    submit = SubmitField(_l('Submit'))

class CategoryForm(FlaskForm):

    name = StringField(
        _l('Name'),
        validators=[
            validators.DataRequired(_l('Description is required')),
            validators.Length(min=1,max=50)
        ]
    )
    description = StringField(
        _l('Description'),
        validators=[
            validators.DataRequired(_l('Description is required')),
            validators.Length(min=1,max=255)
        ]
    )
    submit = SubmitField(_l('Submit'))

class SpecialistForm(FlaskForm):
    name = StringField(
        _l('Name'),
        validators=[
            validators.DataRequired(_l('Description is required')),
            validators.Length(min=1,max=50)
        ]
    )
    description = StringField(
        _l('Description'),
        validators=[
            validators.DataRequired(_l('Description is required')),
            validators.Length(min=1,max=255)
        ]
    )

    submit = SubmitField(_l('Submit'))


class WorkRoleForm(FlaskForm):
    name = StringField(
        _l('Name'),
        validators=[
            validators.DataRequired(_l('Description is required')),
            validators.Length(min=1,max=50)
        ]
    )
    description = StringField(
        _l('Description'),
        validators=[
            validators.DataRequired(_l('Description is required')),
            validators.Length(min=1,max=255)
        ]
    )

    ksat = StringField(
        _l('Description'),
        validators=[
            validators.DataRequired(_l('Description is required')),
            validators.Length(min=1,max=255)
        ]
    )
    submit = SubmitField(_l('Submit'))



class UserForm(FlaskForm):
    username = StringField(_l('Username'),
                           validators=[validators.DataRequired(
                               _l('Username is required.'))]
                           )

    email = EmailField(_l('Email'), validators=[
        validators.DataRequired(_l('Email is required')), validators.Email(_l('Invalid Email'))])

    password = PasswordField(_l('Password'), validators=[
                             validators.DataRequired()])

    retype_password = PasswordField(_l('Retype Password'),
                             validators=[validators.DataRequired()])


    is_enabled = BooleanField(_l('Is enable'),validators=[validators.Optional()])

    first_name = StringField(_l('First Name'),
                           validators=[validators.DataRequired(
                               _l('First name is required.'))]
                           )

    last_name = StringField(_l('Last Name'),
                           validators=[validators.DataRequired(
                               _l('Last Name is required.'))]
                           )

    locale = StringField(_l('Locale'),
                           validators=[validators.Optional(
                               _l('Locale is optional.'))]
                           )

    timezone = StringField(_l('Timezone'),
                           validators=[validators.Optional(
                               _l('Timezone is optional.'))]
                           )

    roles = SelectMultipleField(_l('Roles'), validators=[validators.Optional()])


    submit = SubmitField(_l('Submit'))

    def validate(self):

        validate_password = True

        if self.password.raw_data[0] != self.retype_password.data:
            self.retype_password.errors = 'Please retype the password.'
            validate_password = False

        if validate_password:
            return True
        else:
            return False


class ChangePasswordForm(FlaskForm):

    old_password = PasswordField(_l('Old_Password'), validators=[
                             validators.DataRequired()])

    password = PasswordField(_l('Password'), validators=[
                             validators.DataRequired()])

    retype_password = PasswordField(_l('Retype Password'),
                             validators=[validators.DataRequired()])

    submit = SubmitField(_l('Submit'))


    def validate(self):

        if not user_manager.verify_password(self.old_password.data,current_user):
            self.old_password.errors = 'Please type the old password'
            validate_old_password = False
            return False

        # Add custom password validator if needed
        has_been_added = False
        for v in self.password.validators:
            if v==user_manager.password_validator:
                has_been_added = True
        if not has_been_added:
            self.password.validators.append(user_manager.password_validator)
        # Validate field-validators
        if not super(ChangePasswordForm, self).validate():
            return False
        # All is welll
        return True



class DropOutForm(FlaskForm):

    submit = SubmitField(_l('Submit'))

class RoleForm(FlaskForm):
    name = StringField(
        _l('Name'),
        validators=[
            validators.DataRequired(_l('Name is required')),
        ]
    )


    submit = SubmitField(_l('Submit'))


#Form for search
class SearchForm(FlaskForm):
    q = StringField(_l('Search by Title...'),  validators=[validators.DataRequired()])

class SearchFilterForm(FlaskForm):

    time = BooleanField(_l('Time Filter'),validators=[validators.Optional()])

    #Porque minimo se puee coger un modulo LO y maximo 10 modulos
    t_max = t_max *diff_range_nk
    time_min = IntegerRangeField(_l('Time min (Minutes)'), render_kw={'min':t_min,'max':t_max},
                            default=t_min,validators=[validators.DataRequired(
                                _l('Minimum time_max is required.'))]
                            )

    time_max = IntegerRangeField(_l('Time max (Minutes)'),render_kw={'min':t_min,'max':t_max},
                             default=t_max,validators=[validators.DataRequired(
                                _l('Minimum time_max is required.'))]
                            )

    cost = BooleanField(_l('Cost Filter'),validators=[validators.Optional()])

    c_max = c_max*diff_range_nk
    cost_min = IntegerRangeField(_l('Cost min (€)'),render_kw={'min':c_min,'max':c_max},
                             default=c_min,validators=[validators.DataRequired(
                                _l('Minimum cost_min is required.'))]
                            )

    cost_max = IntegerRangeField(_l('Cost max (€)'),render_kw={'min':c_min,'max':c_max},
                             default=c_max,validators=[validators.DataRequired(
                                _l('Minimum cost_max is required.'))]
                            )


    reput = BooleanField(_l('Reputation Filter'),validators=[validators.Optional()])


    reput_min = IntegerRangeField(_l('Reput min -- 0'),render_kw={'min':r_min,'max':r_max},
                             default=r_min,validators=[validators.DataRequired(
                                _l('Minimum reput_min is required.'))]
                            )

    reput_max = IntegerRangeField(_l('Reput max - 50'),render_kw={'min':r_min,'max':r_max},
                             default=r_max,validators=[validators.DataRequired(
                                _l('Minimum reput_max is required.'))]
                            )

    submit = SubmitField(_l('Submit'))



#Form for search
class SearchFriendForm(FlaskForm):
    friend_user = StringField(_l('Friend Username'),  validators=[validators.DataRequired()])
    submit = SubmitField(_l('Search Friend'))


class LoginForm(FlaskForm):
    """Application login form."""
    username = StringField(
        _l('Username'),
        validators=[
            validators.DataRequired(_l('Username is required')),
        ]
    )

    email = StringField(
        _l('email'),
        validators=[
            validators.DataRequired(_l('Email is required')),
        ]
    )

    password = PasswordField(
        _l('Password'),
        validators=[
            validators.DataRequired(_l('Password is required')),
        ]
    )

    remember_me = BooleanField(_l('Remember me'))

    submit = SubmitField(_l('Sign in'))



class RegistrationForm(FlaskForm):
    username = StringField(_l('Username'),
                           validators=[validators.DataRequired(
                               _l('Username is required.'))]
                           )

    email = StringField(_l('Email'), validators=[
        validators.DataRequired(), validators.Email()])

    password = PasswordField(_l('Password'), validators=[
                             validators.DataRequired()])

    retype_password = PasswordField(
        _l('Retype Password'), validators=[validators.DataRequired()])

    submit = SubmitField(_l('Register'))

    def validate(self):
        user_manager =  current_app.user_manager
        if not user_manager.enable_username:
            delattr(self, 'username')
        if not user_manager.enable_email:
            delattr(self, 'email')
        if not user_manager.enable_retype_password:
            delattr(self, 'retype_password')
        # Add custom username validator if needed
        if user_manager.enable_username:
            has_been_added = False
            for v in self.username.validators:
                if v==user_manager.username_validator:
                    has_been_added = True
            if not has_been_added:
                self.username.validators.append(user_manager.username_validator)
        # Add custom password validator if needed
        has_been_added = False
        for v in self.password.validators:
            if v==user_manager.password_validator:
                has_been_added = True
        if not has_been_added:
            self.password.validators.append(user_manager.password_validator)
        # Validate field-validators
        if not super(RegistrationForm, self).validate():
            return False
        # All is well
        return True


class KsaForm(Form):
    """Subform."""
    levelK = SelectField(
        'LevelK', choices=[(0, '0'), (1, '1'), (2, '2'), (3, '3'), (4, '4'), (5, '5')])
    levelS = SelectField(
        'LevelS', choices=[(0, '0'), (1, '1'), (2, '2'), (3, '3'), (4, '4'), (5, '5')])
    levelA = SelectField(
        'LevelA', choices=[(0, '0'), (1, '1'), (2, '2'), (3, '3'), (4, '4'), (5, '5')])


class TargetKsaForm(Form):
    """Subform."""
    levelK_req = SelectField(
        'LevelK_req',choices=[(-1,'-1'),(0, '0'), (1, '1'), (2, '2'), (3, '3'), (4, '4'), (5, '5')],
        validators=[validators.DataRequired()]
    )
    levelK_goal = SelectField(
        'LevelK_goal', choices=[(-1,'-1'),(0, '0'), (1, '1'), (2, '2'), (3, '3'), (4, '4'), (5, '5')],
        validators=[validators.DataRequired()])
    levelS_req = SelectField(
        'LevelS_req', choices=[(-1,'-1'),(0, '0'), (1, '1'), (2, '2'), (3, '3'), (4, '4'), (5, '5')],
        validators=[validators.DataRequired()])
    levelS_goal = SelectField(
        'LevelS_goal', choices=[(-1,'-1'),(0, '0'), (1, '1'), (2, '2'), (3, '3'), (4, '4'), (5, '5')],
        validators=[validators.DataRequired()])
    levelA_req = SelectField(
        'LevelA_req', choices=[(-1,'-1'),(0, '0'), (1, '1'), (2, '2'), (3, '3'), (4, '4'), (5, '5')],
        validators=[validators.DataRequired()])
    levelA_goal = SelectField(
        'LevelA_goal', choices=[(-1,'-1'),(0, '0'), (1, '1'), (2, '2'), (3, '3'), (4, '4'), (5, '5')],
        validators=[validators.DataRequired()])

    def validate(self, *args, **kwargs):

        krpass = False
        kgpass = False
        srpass = False
        sgpass = False
        arpass = False
        agpass = False

        not_existKreq_out = False
        not_existSreq_out = False
        not_existAreq_out = False

        message1_is = False
        message2_is = False
        message2 = "Choose a level above the prerequisite or equal to zero."

        # Verificar que el subform existe
        if not self.levelK_req or not self.levelK_goal:
            krpass = True
            Kgpass = True
            not_existKreq_out = True
        elif self.levelK_req.data == "None" or self.levelK_goal.data == "None":
            krpass = True
            Kgpass = True

        # Cuando un goal es igual 0, significa que no hay aprendizaje, se queda tal cual
        elif int(self.levelK_req.data) >= 0 and int(self.levelK_goal.data)==0 :
            krpass = True
            kgpass = True
        elif int(self.levelK_req.data) >= 0 and\
         (int(self.levelK_goal.data)==-1 or int(self.levelK_goal.data) <= int(self.levelK_req.data)):
            krpass = False
            message2_is = True

            self.levelK_req.errors = (super().errors, message2)
            self.levelK_goal.errors = (super().errors, message2)

        #Se permite todo despues de la restriccion anterior
        else: 
            krpass = True
            kgpass = True

        if not self.levelS_req or not self.levelS_goal:
            srpass = True
            sgpass = True
            not_existSreq_out = True

        elif self.levelS_req.data == "None" or self.levelS_goal.data == "None":
            srpass = True
            sgpass = True
        elif int(self.levelS_req.data) >= 0 and int(self.levelS_goal.data)==0:
            srpass = True
            sgpass = True
        elif int(self.levelS_req.data) >= 0 and\
         (int(self.levelS_goal.data)==-1 or int(self.levelS_goal.data) <= int(self.levelS_req.data)):
            srpass = False
            message2_is = True

            self.levelS_req.errors = (super().errors, message2)
            self.levelS_goal.errors = (super().errors, message2)

        elif int(self.levelS_req.data) >= -1 or int(self.levelS_goal.data) >= -1:
            srpass = True
            sgpass = True

        if not self.levelA_req or not self.levelA_goal:
            arpass = True
            agpass = True
            not_existAreq_out = True

        elif self.levelA_req.data == "None" or self.levelA_goal.data == "None":
            arpass = True
            agpass = True
        elif int(self.levelA_req.data) >= 0 and int(self.levelA_goal.data) == 0:
            arpass = True
            agpass = True
        elif int(self.levelA_req.data) >= 0 and\
         (int(self.levelA_goal.data) == -1 or int(self.levelA_goal.data) <= int(self.levelA_req.data)):
            arpass = False
            message2_is = True

            self.levelA_req.errors = (super().errors, message2)
            self.levelA_goal.errors = (super().errors, message2)

        elif int(self.levelA_req.data) >= -1 or int(self.levelA_goal.data) >= -1:
            arpass = True
            agpass = True

        if (krpass or kgpass) and (srpass or sgpass) and (arpass or agpass):
            return True
        else:
            message1 = "Choose a pair of Prerequisite and Outcome."

            if message2_is:
                return False

            if not not_existKreq_out or not not_existSreq_out or not not_existAreq_out:
                if not not_existKreq_out:
                    self.levelK_req.errors = (super().errors, message1)
                    self.levelK_goal.errors = (super().errors, message1)
                    if not not_existSreq_out:
                        self.levelS_req.errors = (super().errors, message1)
                        self.levelS_goal.errors = (super().errors, message1)
                    if not not_existAreq_out:
                        self.levelA_req.errors = (super().errors, message1)
                        self.levelA_goal.errors = (super().errors, message1)

                elif not not_existSreq_out:
                    self.levelS_req.errors = (super().errors, message1)
                    self.levelS_goal.errors = (super().errors, message1)
                    if not not_existKreq_out:
                        self.levelK_req.errors = (super().errors, message1)
                        self.levelK_goal.errors = (super().errors, message1)
                    if not not_existAreq_out:
                        self.levelA_req.errors = (super().errors, message1)
                        self.levelA_goal.errors = (super().errors, message1)

                else:
                    self.levelA_req.errors = (super().errors, message1)
                    self.levelA_goal.errors = (super().errors, message1)
                    if not not_existSreq_out:
                        self.levelS_req.errors = (super().errors, message1)
                        self.levelS_goal.errors = (super().errors, message1)
                    if not not_existKreq_out:
                        self.levelK_req.errors = (super().errors, message1)
                        self.levelK_goal.errors = (super().errors, message1)

            return False


def Validation_MultiSelect(FlaskForm, field):
    if not field.data:
        raise ValidationError('Choose at least one.')


class TestForm(FlaskForm):
    ksas = FieldList(FormField(KsaForm))
    # tasks = SelectMultipleField('Tasks',  validators=[
    #                             Validation_MultiSelect])
    tasks = SelectMultipleField(_l('Tasks'))
    submit = SubmitField('Next')


class TargetForm(FlaskForm):

    time_min = IntegerField(_l('Time min (Minutes)'), widget=html5.NumberInput(min=t_min,max=t_max),
                            validators=[validators.DataRequired(
                                _l('Minimum time is required.'))]
                            )
    time_max = IntegerField(_l('Time max (Minutes)'), widget=html5.NumberInput(min=t_min,max=t_max),
                            validators=[validators.DataRequired(
                                _l('Maximum time is required.'))]
                            )
    cost_min = IntegerField(_l('Cost min (€)'), widget=html5.NumberInput(min=c_min,max=c_max),
                            validators=[validators.DataRequired(
                                _l('Minimum cost is required.'))]
                            )
    cost_max = IntegerField(_l('Cost max (€)'), widget=html5.NumberInput(min=c_min,max=c_max),
                            validators=[validators.DataRequired(
                                _l('Maximum cost is required.'))]
                            )
    reput_average = IntegerField(_l('Reput average (?/50)'), widget=html5.NumberInput(min=r_min,max=r_max),
                                 validators=[validators.DataRequired(
                                     _l('Reput average is required.'))]
                                 )
    reput_min = IntegerField(_l('Reput min (?/50)'), widget=html5.NumberInput(min=r_min,max=r_max),
                             validators=[validators.DataRequired(
                                 _l('Reput Minimum is required.'))]
                             )


    nk_min = IntegerField(_l('Minimum module number (?/5)'), widget=html5.NumberInput(min=n_min_range[0],max=n_min_range[1]),
                             validators=[validators.DataRequired(
                                 _l('Minimum module number is required.'))]
                             )

    nk_max = IntegerField(_l('Maximum number of modules (?/10)'), widget=html5.NumberInput(min=n_max_range[0],max=n_max_range[1]),
                             validators=[validators.DataRequired(
                                 _l('Maximum number of modules. is required.'))]
                             )

    selectWroles = SelectField(_l('selectWroles'), validators=[
                               validators.DataRequired()])

    ksas = FieldList(FormField(TargetKsaForm))
    submit = SubmitField('Next')

    def validate(self, **kwargs):

        if self.time_min.data < t_min or self.time_min.data > t_max:
            #Volvemos al estado base, porque la modificacion dinamica de la selecion de wk roles se hace en el javascript
            # y este vuelve a un estado base cuando hay una validacion incorrecta
            message_error = f'{"Choose a value greater or equal than Time min: "}{t_min}{"or less or equal than Time max: "}{t_max}'
            self.selectWroles.data='Default'
            self.time_min.errors = (super().errors, message_error)
            return False

        if self.time_max.data < t_min or self.time_max.data > t_max:
            message_error = f'{"Choose a value greater or equal than Time min: "}{t_min}{"or less or equal than Time max: "}{t_max}'
            self.selectWroles.data='Default'
            self.time_max.errors = (super().errors, message_error)
            return False

        if self.time_max.data < self.time_min.data:
            self.selectWroles.data='Default'
            self.time_max.errors = (super().errors, "Choose a value greater than Time min.")
            return False


        if self.cost_min.data < c_min or self.cost_min.data > c_max:
            message_error = f'{"Choose a value greater or equal than Cost min: "}{c_min}{"or less or equal than Cost max: "}{c_max}'
            self.selectWroles.data='Default'
            self.cost_min.errors = (super().errors, message_error)
            return False


        if self.cost_max.data < c_min or self.cost_max.data > c_max:
            message_error = f'{"Choose a value greater or equal than Cost min: "}{c_min}{"or less or equal than Cost max: "}{c_max}'
            self.selectWroles.data='Default'
            self.cost_max.errors = (super().errors, message_error)
            return False

        if self.cost_max.data < self.cost_min.data:
            #Volvemos al estado base
            self.selectWroles.data='Default'
            self.cost_max.errors = (super().errors, "Choose a value greater than Cost min.")
            return False


        if (self.reput_min.data < r_min or self.reput_min.data > r_max) or\
            (self.reput_average.data < r_min or self.reput_average.data > r_max):
            #Volvemos al estado base
            self.selectWroles.data='Default'
            self.reput_min.errors = (super().errors, f'{"Choose a value between "}{r_min}{"and "}{r_max}')
            self.reput_average.errors = (super().errors, f'{"Choose a value between "}{r_min}{"and "}{r_max}')
            return False


        if (self.nk_min.data < n_min_range[0] or self.nk_min.data > n_min_range[1]) or\
            (self.nk_max.data < n_max_range[0] or self.nk_max.data > n_max_range[1]):
            #Volvemos al estado base
            self.selectWroles.data='Default'
            self.nk_min.errors = (super().errors,f'{"Choose a value between "}{n_min_range[0]}{"and "}{n_min_range[1]}')
            self.nk_max.errors = (super().errors,f'{"Choose a value between "}{n_max_range[0]}{"and "}{n_max_range[1]}')
            return False

        if self.nk_max.data < self.nk_min.data:
            #Volvemos al estado base
            self.selectWroles.data='Default'
            self.nk_max.errors = (super().errors, "Choose a value greater than Minimum module number.")
            return False

        return True