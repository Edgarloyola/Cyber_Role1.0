# -*- coding: utf-8 -*-
# control supr elimina una lineapñ
"""This file contains general views."""

import datetime
from flask import Blueprint, session, render_template, flash, redirect, url_for, request, current_app
from flask_babel import _
from flask_user import login_required, roles_required
from flask_login import current_user, login_user
from flask_mail import Message

from cyber_role import db, user_manager,mail,hashids_hasher
from cyber_role.models import User,Role, Ksat, Knowledge, Skill, Ability, Task
from cyber_role.forms import RegistrationForm, ChangePasswordForm,DropOutForm,TestForm, LoginForm,\
                            SearchForm, RoleForm, UserForm,SearchFriendForm

bp_user_ksat = Blueprint('user_ksat', __name__)


@bp_user_ksat.route('/register', methods=['GET', 'POST'])
def register():


#EJEMPLO DE DOCSTRINGS
    """Show a form to request a password reset token.

    This does not tell the user whether the emails is valid or not. In
    addition, if the user already had a password reset token, it will be
    overwritten.
    
     Args:
        token (str): Random token mailed to the user.
    """

    if current_user.is_authenticated:
        return redirect(url_for('general.show_dash'))

    form = RegistrationForm()

    if form.validate_on_submit():
        #Continua con la creacion de un usuario

        hashed_password = user_manager.hash_password(form.password.data)
        new_user = User(
            username=form.username.data,
            email=form.email.data,
            password=hashed_password,
            confirmed_at=datetime.datetime.utcnow(),
            is_enabled=True,
        )


        role='User'
        role_default = Role.query.filter_by(name=role).first()

        if not role_default:
            new_role_default = Role(name = 'User')
            new_user.roles.add(new_role_default)
        else:
            new_user.roles.add(role_default)

        try:
            correct = True
            db.session.add(new_user)
            db.session.commit()

        except Exception as e:
            # Catch anything unknown
            print(e)
            correct = False

        finally:
            if not correct:
                # Cleanup and show error
                db.session.rollback()
                flash('Error creating user, make sure username and email are unique','error')

            else:
                flash('Congratulations, you are now a registered user!','success')
                return redirect(url_for('user.login'))
    return render_template('extensions/flask_user/register.html', title='Register', form=form)



#zona admmin
@bp_user_ksat.route('/manage_user', methods=['GET','POST'])
@login_required
@roles_required('Admin')
def manage_user():
    page = request.args.get('page', 1, type=int)
    users_ids = User.query.order_by(User.id.asc()).paginate(
        page, current_app.config['PAGE_ITEMS'], False)

    search_form = SearchForm(request.form)
    # Ksat.reindex()

    if search_form.validate_on_submit():
        page = request.args.get('page', 1, type=int)
        users, total = User.search(request.form['q'], page,current_app.config['PAGE_ITEMS'])

        #Pues habria que hacer una paginacion manual conforme a users resultados de elastisearch
        next_url = url_for('user/manage_user.html', q=request.form['q'], page=page+1) \
            if total > page * current_app.config['PAGE_ITEMS'] else None
        prev_url = url_for('user/manage_user.html', q=request.form['q'], page=page-1) \
            if page > 1 else None

        return render_template('user/manage_user.html', title=_('Users'),
            search_form=search_form,users=users,next_url=next_url, prev_url=prev_url)

    if not request.args.get('delete'):
        return render_template('user/manage_user.html', title='Users',search_form=search_form,
            lista_user=users_ids)
    else:#Remove an users
        id_hash = request.args.get('id')
        if not id_hash or id_hash=='':
            flash("No null or empty values are allowed.","error")
            return render_template('user/manage_user.html', title='Users',search_form=search_form,
                lista_user=users_ids)

        remove_user = User.query.filter_by(id=hashids_hasher.decode(id_hash)).first()
        try:
            correct = True
            db.session.delete(remove_user)
            db.session.commit()
        except Exception as e:
            # Catch anything unknown
            print(e)
            correct = False
        finally:
            if not correct:
                # Cleanup and show error
                db.session.rollback()
                flash('Error when deleting User.','error')
            else:
                flash("Our User was deleted!","success")
                return redirect(url_for('user_ksat.manage_user'))

    return render_template('user/manage_user.html', title='Users',search_form=search_form,
        lista_user=users_ids)


@bp_user_ksat.route('/add_user', methods=['GET','POST'])
@login_required
@roles_required('Admin')
def add_user():
    roles = Role.query.all()

    user_form = UserForm(request.form)
    user_form.roles.choices = [(i.name,i.name) for i in roles]

    if user_form.validate_on_submit():

        if not request.form['username'] or request.form['username'] == '' :
            flash("No null or empty values are allowed.","warn")
            return render_template('user/add_edit_user.html', title='Add User',add=True,
                user_form=user_form)
        if not request.form['email'] or request.form['email'] == '' :
            flash("No null or empty values are allowed.","warn")
            return render_template('user/add_edit_user.html', title='Add User',add=True,
                user_form=user_form)
        if not request.form['password'] or request.form['password'] == '' :
            flash("No null or empty values are allowed.","warn")
            return render_template('user/add_edit_user.html', title='Add User',add=True,
                user_form=user_form)
        if request.form['password'] != request.form['retype_password']:
            flash("Passwords are not the same!","warn")
            return render_template('user/add_edit_user.html', title='Add User',add=True,
                user_form=user_form)

        hashed_password = user_manager.hash_password(user_form.password.data)
        new_user = User(
            username=user_form.username.data,
            email=user_form.email.data,
            password=hashed_password,
            confirmed_at=datetime.datetime.utcnow(),
            is_enabled=user_form.is_enabled.data,
            first_name=user_form.first_name.data,
            last_name=user_form.last_name.data,
            locale=user_form.locale.data,
            timezone=user_form.timezone.data
        )

        #Si existe la lista de roles que hemos elegido se anadira al usuario
        if user_form.roles.data:
            for rol in roles:
                if rol.name in user_form.roles.data:
                    new_user.roles.add(rol)
        try:
            correct = True
            db.session.add(new_user)
            db.session.commit()

        except Exception as e:
            # Catch anything unknown
            print(e)
            correct = False

        finally:
            if not correct:
                # Cleanup and show error
                db.session.rollback()
                flash('Error creating user, make sure username and email are unique','error')

            else:
                flash('Congratulations, you have created a new user!','success')
                return redirect(url_for('user_ksat.manage_user'))


    return render_template('user/add_edit_user.html', title='Add User',add=True,user_form=user_form)

@bp_user_ksat.route('/modify_user', methods=['GET','POST'])
@login_required
@roles_required('Admin')
def modify_user():

    id_hash = request.args.get('id')

    if not id_hash or id_hash=='':
        flash('There is no id.','error')
        return redirect(url_for('user_ksat.manage_user'))

    modify_user = User.query.filter_by(id=hashids_hasher.decode(id_hash)).first()

    if not modify_user:
        flash('There is no user to be changed.','error')
        return redirect(url_for('user_ksat.manage_user'))

    roles = Role.query.all()

    user_form = UserForm(
        username=modify_user.username,
        email=modify_user.email,
        password=modify_user.password,
        retype_password=modify_user.password,
        is_enabled=modify_user.is_enabled,
        first_name=modify_user.first_name,
        last_name=modify_user.last_name,
        locale=modify_user.locale,
        timezone=modify_user.timezone
        )
    # Metemos los valores actuales de los roles y los roles que no se añadieron anteriormente
    user_form.roles.choices = [(i.name,i.name) for i in roles]
    user_form.roles.data = [i for i in modify_user.role_names]

    if user_form.validate_on_submit():

        if not request.form['username'] or request.form['username'] == '' :
            flash("No null or empty values are allowed.","warn")
            return render_template('user/add_edit_user.html', title='Modify User',
                user_form=user_form)
        if not request.form['email'] or request.form['email'] == '' :
            flash("No null or empty values are allowed.","warn")
            return render_template('user/add_edit_user.html', title='Modify User',
                user_form=user_form)
        if not request.form['password'] or request.form['password'] == '' :
            flash("No null or empty values are allowed.","warn")
            return render_template('user/add_edit_user.html', title='Modify User',
                user_form=user_form)
        if request.form['password'] != request.form['retype_password']:
            flash("Passwords are not the same!","warn")
            return render_template('user/add_edit_user.html', title='Modify User',
                user_form=user_form)

        hashed_password = user_manager.hash_password(request.form['password'])

        modify_user.username=request.form['username']
        modify_user.email=request.form['email']
        modify_user.password=hashed_password
        modify_user.confirmed_at=datetime.datetime.utcnow()

        if 'is_enabled' in request.form:
            modify_user.is_enabled=True
        else:
            modify_user.is_enabled=False

        modify_user.first_name=request.form['first_name']
        modify_user.last_name=request.form['last_name']
        modify_user.locale=request.form['locale']
        modify_user.timezone=request.form['timezone']

        #Si existe la lista de roles que hemos elegido se anadira al usuario
        if request.form.getlist('roles'):
            for rol in roles:
                if rol.name in request.form.getlist('roles'):
                    modify_user.roles.add(rol)
        else:
            modify_user.roles = set()

        try:
            correct = True
            db.session.commit()

        except Exception as e:
            # Catch anything unknown
            print(e)
            correct = False

        finally:
            if not correct:
                # Cleanup and show error
                db.session.rollback()
                flash('Error modifying user, make sure username and email are unique','error')
            else:
                flash('Congratulations, you have modified a user!','success')
                return redirect(url_for('user_ksat.manage_user'))


    return render_template('user/add_edit_user.html', title='Modify User',user_form=user_form)


@bp_user_ksat.route('/manage_role', methods=['GET','POST'])
@login_required
@roles_required('Admin')
def manage_role():
    page = request.args.get('page', 1, type=int)
    roles_ids = Role.query.order_by(Role.id.asc()).paginate(
        page, current_app.config['PAGE_ITEMS'], False)

    search_form = SearchForm(request.form)
    # Ksat.reindex()

    if search_form.validate_on_submit():
        page = request.args.get('page', 1, type=int)
        roles, total = Role.search(request.form['q'], page,current_app.config['PAGE_ITEMS'])

        #Pues habria que hacer una paginacion manual conforme a users resultados de elastisearch
        next_url = url_for('user/manage_role.html', q=request.form['q'], page=page+1) \
            if total > page * current_app.config['PAGE_ITEMS'] else None
        prev_url = url_for('user/manage_role.html', q=request.form['q'], page=page-1) \
            if page > 1 else None

        return render_template('user/manage_role.html', title=_('Roles'),search_form=search_form,
         roles=roles,next_url=next_url, prev_url=prev_url)

    if not request.args.get('delete'):
        return render_template('user/manage_role.html', title='Roles',search_form=search_form,
            lista_role=roles_ids)
    else:#Remove an role
        id_hash = request.args.get('id')
        if not id_hash or id_hash=='':
            flash("No null or empty values are allowed.","error")
            return render_template('user/manage_role.html', title='Roles',search_form=search_form,
                lista_role=roles_ids)

        remove_rol = Role.query.filter_by(id=hashids_hasher.decode(id_hash)).first()

        try:
            correct = True
            db.session.delete(remove_rol)
            db.session.commit()
        except Exception as e:
            # Catch anything unknown
            print(e)
            correct = False
        finally:
            if not correct:
                # Cleanup and show error
                db.session.rollback()
                flash('Error when deleting Role.','error')
            else:
                flash("Our Role was deleted!","success")
                return redirect(url_for('user_ksat.manage_role'))

    return render_template('user/manage_role.html', title='Roles',search_form=search_form,
        lista_role=roles_ids)

@bp_user_ksat.route('/add_role', methods=['GET','POST'])
@login_required
@roles_required('Admin')
def add_role():
    role_form = RoleForm(request.form)

    if role_form.validate_on_submit():

        name = request.form['name']

        if not name or name == '' :
            flash("No null or empty values are allowed.","warn")
            return render_template('user/add_edit_role.html', title='Add Role',
                add=True,form=role_form)

        else:
            new_role = Role(name = name)
            try:
                correct = True
                db.session.add(new_role)
                db.session.commit()
            except Exception as e:
                # Catch anything unknown
                print(e)
                correct = False
            finally:
                if not correct:
                    # Cleanup and show error
                    db.session.rollback()
                    flash('Error when creating a Role.','error')
                else:
                    flash("Our Role was created!","success")
                    return redirect(url_for('user_ksat.manage_role'))

    return render_template('user/add_edit_role.html', title='Add Role',add=True,form=role_form)

@bp_user_ksat.route('/modify_role', methods=['GET','POST'])
@login_required
@roles_required('Admin')
def modify_role():
    id_hash = request.args.get('id')

    if not id_hash or id_hash=='':
        flash('There is no id.','error')
        return redirect(url_for('user_ksat.manage_role'))
    #Localizamos el role y luego lo modificamos
    modify_role = Role.query.filter_by(id=hashids_hasher.decode(id_hash)).first()

    if not modify_role:
        flash('There is no role.','error')
        return redirect(url_for('user_ksat.manage_role'))

    role_form = RoleForm(name=modify_role.name)

    if role_form.validate_on_submit():
        new_name = request.form['name']
        if not new_name or new_name == '' :
            flash("No null or empty values are allowed.","warn")
            return render_template('user/add_edit_role.html', title='Modify Role',form=role_form)
        else:
            
            modify_role.name = new_name

            try:
                correct = True
                db.session.commit()
            except Exception as e:
                # Catch anything unknown
                print(e)
                correct = False
            finally:
                if not correct:
                    # Cleanup and show error
                    db.session.rollback()
                    flash('Error when modifying a Role.','error')
                else:
                    flash("Our Role was modified!","success")
                    return redirect(url_for('user_ksat.manage_role'))

    return render_template('user/add_edit_role.html', title='Role',form=role_form)






@bp_user_ksat.route('/show_user', methods=['GET'])
@login_required
@roles_required(['User','Admin'])
def show_user():
    #Mostraremos los datos esenciales del usuario
    #CUANDO SACAMOS EL PASSWORD DIRECTAMENTE DEL CURREN_USER OBTENEMOS UN PASSWORD HASHEADO
    #MIENTRAS QUE SI LO METEMOS EN UN FORMULARIO
    # Y LUEGO DE ESE CAMPO SACAMOS SU DESCRIPTION, OBTENEMOS EL PASSWORD EN TEXTO PLANO

    return render_template('user/show_by_user.html', title='Show Profile', user = current_user)



@bp_user_ksat.route('/modify_by_user', methods=['GET', 'POST'])
@login_required
@roles_required(['User','Admin'])
def modify_by_user():

    user_form = UserForm(request.form)

    user_form.username.data = current_user.username
    user_form.email.data = current_user.email
    #AQUI ESTAMOS METIENDO EL PASSWORD EN TEXTO PLANO CUANDO ACCEDEMOS A DESCRIPTION
    # DE ESTE ATRIBUTO, ESTO ES FALSO
    user_form.password.data = current_user.password
    user_form.first_name.data = current_user.first_name
    user_form.last_name.data = current_user.last_name


    if user_form.validate_on_submit():

        if not request.form['username'] or request.form['username'] == '' :
            flash("No null or empty values are allowed.","warn")
            return render_template('user/modify_by_user.html', title='Modify Profile',
                user_form=user_form)
        if not request.form['email'] or request.form['email'] == '' :
            flash("No null or empty values are allowed.","warn")
            return render_template('user/modify_by_user.html', title='Modify Profile',
                user_form=user_form)
        if not request.form['password'] or request.form['password'] == '' :
            flash("No null or empty values are allowed.","warn")
            return render_template('user/modify_by_user.html', title='Modify Profile',
                user_form=user_form)
        if request.form['password'] != request.form['retype_password']:
            flash("Passwords are not the same!","warn")
            return render_template('user/modify_by_user.html', title='Modify Profile',
                user_form=user_form)


        hashed_password = user_manager.hash_password(request.form['password'])

        current_user.username = request.form['username']
        current_user.email = request.form['email']
        current_user.password = hashed_password
        current_user.first_name = request.form['first_name']
        current_user.last_name = request.form['last_name']
        current_user.confirmed_at = datetime.datetime.utcnow()

        try:
            correct = True
            db.session.commit()
        except Exception as e:
            # Catch anything unknown
            print(e)
            correct = False
        finally:
            if not correct:
                # Cleanup and show error
                db.session.rollback()
                flash('Error modifying user, make sure username and email are unique','error')
                return render_template('user/modify_by_user.html', title='Modify Profile',
                    user_form=user_form)
            else:
                flash('The user was successfully modified.','success')
                return redirect(url_for('user_ksat.show_user'))

    return render_template('user/modify_by_user.html', title='Modify Profile',user_form=user_form)


#Esta ya la tenemos arriba en este mismo codigo
@bp_user_ksat.route('/change_password_user', methods=['GET', 'POST'])
@login_required
@roles_required(['User','Admin'])
def change_password_user():

    form = ChangePasswordForm(request.form)

    if form.validate_on_submit():

        if not request.form['old_password'] or request.form['old_password'] == '' :
            flash("No null or empty values are allowed.","warn")
            return render_template('user/change_password_user.html', title='Change Password', form=form)

        if not request.form['password'] or request.form['password'] == '' :
            flash("No null or empty values are allowed.","warn")
            return render_template('user/change_password_user.html', title='Change Password', form=form)

        if request.form['password'] != request.form['retype_password']:
            flash("Passwords are not the same!","warn")
            return render_template('user/change_password_user.html', title='Change Password', form=form)


        hashed_password = user_manager.hash_password(request.form['password'])

        #modificamos el password del usuario
        current_user.password = hashed_password

        try:
            correct = True
            db.session.commit()
        except Exception as e:
            # Catch anything unknown
            print(e)
            correct = False
        finally:
            if not correct:
                # Cleanup and show error
                db.session.rollback()
                flash('Error modifying password of user, make sure username and email are unique','error')
                return render_template('user/change_password_user.html', title='Change Password', form=form)
            else:
                flash('Congratulations, update your password!','success')
                return redirect(url_for('user_ksat.show_user'))


    return render_template('user/change_password_user.html', title='Change Password', form=form)

@bp_user_ksat.route('/drop_out_user', methods=['GET', 'POST'])
@login_required
@roles_required(['User','Admin'])
def drop_out_user():

    #Lo que se hara aqui, basicamente será desabilitar el usuario y se le notoficara su baja

    form = DropOutForm(request.form)

    if form.validate_on_submit():

        current_user.is_enabled = False
        ok = send_email(current_user.username,current_user.email)
        if ok =='ok':
            correct=True

        try:
            db.session.commit()
        except Exception as e:
            # Catch anything unknown
            print(e)
            correct = False
        finally:
            if not correct:
                # Cleanup and show error
                db.session.rollback()
                flash('Error Drop Out to user','error')
                return render_template('user/drop_out_user.html', title='Drop Out',form=form)
            else:
                flash('You have been dropped =(','success')
                return redirect(url_for('user.logout'))

    return render_template('user/drop_out_user.html', title='Drop Out',form=form)




def send_email(username,email):

    msg = Message('Drop out user',
            sender='noreply@cyber_role.com',
            recipients=['edgaryour25@gmail.com'])

    #ponerlo más bonito
    msg.body = f'''The user: {username} wants to unsubscribe from the Cyber Role platform.'''
    mail.send(msg)

    return 'ok'


@bp_user_ksat.route('/ksa_comparison_friend', methods=['GET', 'POST'])
@login_required
@roles_required(['User','Admin'])
def ksa_comparison_friend():

    search_friend = SearchFriendForm(request.form)

    if search_friend.validate_on_submit():

        friend_user = request.form['friend_user']

        #Buscamos el usuario en cuestion y comparamos sus ksas con el usuario actual
        if friend_user !='' and friend_user:
            friend = User.query.filter_by(username=friend_user).first()

            if not friend:
                flash("Your friend does not exist!","warn")
                return render_template('user/ksa_comparison_friend.html', title='KSA Comparsion',
                    search_friend=search_friend)

            if not current_user.ksat:
                flash("You do not have KSAs to compare!","warn")
                return render_template('user/ksa_comparison_friend.html', title='KSA Comparsion',
                    search_friend=search_friend)

            if not friend.ksat:
                flash("Your friend does not have KSAs to compare","warn")
                return render_template('user/ksa_comparison_friend.html', title='KSA Comparsion',
                    search_friend=search_friend)

            if friend.ksat and current_user.ksat:
                #Cargar el KSAT actual del usuario
                ksas_user_current={}

                knowledges_user = current_user.ksat.ksat_ids['knowledges_ids']
                skills_user = current_user.ksat.ksat_ids['skills_ids']
                abilities_user = current_user.ksat.ksat_ids['abilities_ids']

                for x in knowledges_user:
                    ksas_user_current[x]=knowledges_user[x]["level"]
                for x in skills_user:
                    ksas_user_current[x] = skills_user[x]["level"]
                for x in abilities_user:
                    ksas_user_current[x] = abilities_user[x]["level"]


                ksas_user_friend={}

                #Info KSA del usuario FRIEND++++++++++"
                knowledges_user = friend.ksat.ksat_ids['knowledges_ids']
                skills_user = friend.ksat.ksat_ids['skills_ids']
                abilities_user = friend.ksat.ksat_ids['abilities_ids']

                for x in knowledges_user:
                    ksas_user_friend[x]=knowledges_user[x]["level"]
                for x in skills_user:
                    ksas_user_friend[x] = skills_user[x]["level"]
                for x in abilities_user:
                    ksas_user_friend[x] = abilities_user[x]["level"]


                dates= []
                matrix = []

                #SOLO HABRA DOS FECHAS PORQUE SERAN SOLO 2 USUARIOS KSAS, ordenamos de menor a mayor fecha
                friend_date_mayor = False
                names =[]
                if friend.ksat.date > current_user.ksat.date:
                    friend_date_mayor = True
                    #Añadimos los nombres para que se vea más claro en el grafico
                    names=[current_user.username,friend.username]
                    dates.append(str(current_user.ksat.date.strftime("%d/%m/%Y, %H:%M:%S")))
                    dates.append(str(friend.ksat.date.strftime("%d/%m/%Y, %H:%M:%S")))
                else:
                    names=[friend.username,current_user.username]
                    dates.append(str(friend.ksat.date.strftime("%d/%m/%Y, %H:%M:%S")))
                    dates.append(str(current_user.ksat.date.strftime("%d/%m/%Y, %H:%M:%S")))


                dict_mezcla = {}
                for i in ksas_user_current:
                    if i in ksas_user_friend:
                        dict_mezcla[i]= [ksas_user_current[i],ksas_user_friend[i]]
                    else:
                        dict_mezcla[i]= [ksas_user_current[i],0]
                #añadimos todos los que se encuentren y los que no se encuentren se añaden al final
                for i in ksas_user_friend:
                    #Si aun no se ha añadido se agregara
                    if not i in dict_mezcla:
                        #Significa que no pertenece al usuario
                        dict_mezcla[i] = [0,ksas_user_friend[i]]
                #Donde el primero seria del usuario actual y el segundo del amigo
                # en caso de que no aparezca en el amigo se añadira un 0
                #dict = { "k0001":[2,3]}

                #Añadimos los IDs - simbolicos de los dos mezclados
                matrix.append(list(dict_mezcla.keys()))

                # obtenemos los valores de los diccionarios para su comparación
                lista_values_user = [i[0] for i in list(dict_mezcla.values())]
                lista_values_friend = [i[1] for i in list(dict_mezcla.values())]


                #ordenamos por fechas 
                if friend_date_mayor:
                    matrix.append(lista_values_user)
                    matrix.append(lista_values_friend)
                else:
                    matrix.append(lista_values_friend)
                    matrix.append(lista_values_user)


                #TRANSPONEMOS LOS ARRYAS
                rez = [[matrix[j][i] for j in range(len(matrix))] for i in range(len(matrix[0]))] 


                dict_matrix = {0:rez}
                # dict_matrix[0]=rez

                return render_template('user/ksa_comparison_friend.html', title='KSA Comparsion',
                    search_friend=search_friend,data=dict_matrix,dates=dates, names=names)

        return render_template('user/ksa_comparison_friend.html', title='KSA Comparsion',
            search_friend=search_friend)


    return render_template('user/ksa_comparison_friend.html', title='KSA Comparsion',
        search_friend=search_friend)



