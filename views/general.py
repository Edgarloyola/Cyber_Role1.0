# -*- coding: utf-8 -*-

"""This file contains general views."""

import datetime
import requests
import json
import os
from os.path import isfile, join
from flask import Blueprint, jsonify, session, render_template, flash, redirect, url_for, request, current_app
from flask_babel import _

from flask_user import login_required, roles_required
from flask_login import current_user, login_user

from cyber_role import db, user_manager,hashids_hasher
from cyber_role.models import User, Ksat, Category, Specialist, WorkRole, Knowledge, Skill, Ability, Task, Course
from cyber_role.forms import RegistrationForm, TestForm, KsaForm, TargetForm, TargetKsaForm,SearchForm


bp_general = Blueprint('general', __name__)


@bp_general.route('/', methods=['GET'])
@login_required
@roles_required(['User','Admin'])
def show_dash():

    """ Metodo que nos servirá para mostrar el dashboard principal una ves se haya iniciado sesión."""

    # session.clear()
    # Si hemos dado al boton cambio de modo user activaremos ese modo, solo cuando seamos Admin
    if not request.args.get('change_user'):
        userMode = False
    else:
        userMode = request.args.get('change_user')


    # Entramos si el usuario es un Admin xq en el caso que el usuario tenga todos los roles,
    # empezara por el que tiene mayor privilegio
    if current_user.has_roles('Admin') and not userMode:
        if current_user.ksat:
            existKSAT_user = True
            return render_template('manage/dashboard_admin.html', title='Dashboard Admin', exist_KSAT=existKSAT_user)

        return render_template('manage/dashboard_admin.html', title='Dashboard Admin')

    # Si es usuario normal entra por aqui
    elif current_user.has_roles(['User','Admin']):
        existKSAT_user = False

        if current_user.ksat:
            existKSAT_user = True
            change_admin=True
            if 'task_id' in session:
                return render_template('general/dashboard.html', title='Dashboard',
                    exist_KSAT=existKSAT_user,change_admin=change_admin)
            else:
                courses = True
                return render_template('general/dashboard.html', title='Dashboard', courses = courses,
                    exist_KSAT=existKSAT_user,change_admin=change_admin)

        if not 'task_id' in session:
            change_admin=True
            courses = True
            return render_template('general/dashboard.html', title='Dashboard',courses=courses,change_admin=change_admin)
        else:
            change_admin=True
            return render_template('general/dashboard.html', title='Dashboard',change_admin=change_admin)

        change_admin=True
        return render_template('general/dashboard.html', title='Dashboard',change_admin=change_admin)


@bp_general.route('/show_category_specialist')
@login_required
@roles_required(['User','Admin'])
def show_category_specialist():

    """ Metodo para mostrar la informacion de los Categories & Specialists segun el NICE."""

    categories = Category.query.order_by(Category.id.asc())
    specialists = Specialist.query.order_by(Specialist.id.asc())
    return render_template('general/category_specialist.html', title='Categories-Specialists', 
        categories=categories, specialists=specialists)


@bp_general.route('/show_work_role')
@login_required
@roles_required(['User','Admin'])
def show_work_role():

    """ Metodo para mostrar la informacion de los Work-Roles segun el NICE."""

    work_roles = WorkRole.query.order_by(WorkRole.id.asc())
    return render_template('general/work_role.html', title='Work Roles', work_roles=work_roles)


@bp_general.route('/k')
@login_required
@roles_required(['User','Admin'])
def show_k():

    """ Metodo para mostrar la informacion de los Knowledges segun el NICE."""

    page = request.args.get('page', 1, type=int)
    knowledges_ids = Knowledge.query.order_by(Knowledge.id.asc()).paginate(
        page, current_app.config['PAGE_ITEMS'], False)

    k = "myK000"

    knowledges_list = [(f'{k}{i.id}' if (i.id < 10) else f'{"myK00"}{i.id}'
                        if(i.id < 100) else f'{"myK0"}{i.id}', i.description) for i in knowledges_ids.items]

    verK = True
    fileDir = os.path.dirname(os.path.realpath('__file__'))

    # me tengo que meter a la ruta base/cyber_role y ejecutar este endpoint
    file_json = 'cyber_role/KSAT_JSON/Knowledges.json'

    if not isfile(join(fileDir, file_json)):
        file_json = 'KSAT_JSON/Knowledges.json'

    with open(file_json) as file:
        # Obtenemos el json del fichero
        data = json.load(file)

        equivalencia_nist = {}
        # ya tenemos el diccionario del nist, original
        values = list(data.values())
        keys = list(data.keys())

        for i in knowledges_ids.items:
            if i.description in values:
                equivalencia_nist[i.id] = keys[values.index(i.description)]


    return render_template('general/ksat.html', title='Knowledges',
                           lista_K=knowledges_ids, l_K=knowledges_list,
                           l_eq=list(equivalencia_nist.values()), verK=verK)


@bp_general.route('/s')
@login_required
@roles_required(['User','Admin'])
def show_s():

    """ Metodo para mostrar la informacion de los Skills segun el NICE."""

    page = request.args.get('page', 1, type=int)
    skills_ids = Skill.query.order_by(Skill.id.asc()).paginate(
        page, current_app.config['PAGE_ITEMS'], False)

    s = "myS000"
    skills_list = [(f'{s}{i.id}' if (i.id < 10) else f'{"myS00"}{i.id}'
                    if (i.id < 100) else f'{"S0"}{i.id}', i.description) for i in skills_ids.items]
    verS = True

    fileDir = os.path.dirname(os.path.realpath('__file__'))
    # me tengo que meter a la ruta base/cyber_role y ejecutar este endpoint
    file_json = 'cyber_role/KSAT_JSON/Skills.json'

    if not isfile(join(fileDir, file_json)):
        file_json = 'KSAT_JSON/Skills.json'

    with open(file_json) as file:
        # Obtenemos el json del fichero
        data = json.load(file)

        equivalencia_nist = {}

        # ya tenemos el diccionario del nist, original
        values = list(data.values())
        keys = list(data.keys())

        for i in skills_ids.items:
            if i.description in values:
                equivalencia_nist[i.id] = keys[values.index(i.description)]


    return render_template('general/ksat.html', title='Skills',
                           lista_S=skills_ids, l_S=skills_list, verS=verS,
                            l_eq=list(equivalencia_nist.values()))


@bp_general.route('/a')
@login_required
@roles_required(['User','Admin'])
def show_a():

    """ Metodo para mostrar la informacion de los abilities segun el NICE."""

    page = request.args.get('page', 1, type=int)
    abilities_ids = Ability.query.order_by(Ability.id.asc()).paginate(
        page, current_app.config['PAGE_ITEMS'], False)

    a = "myA000"
    abilities_list = [(f'{a}{i.id}' if (i.id < 10) else f'{"myA00"}{i.id}'
                       if (i.id < 100) else f'{"myA0"}{i.id}', i.description) for i in abilities_ids.items]
    verA = True

    fileDir = os.path.dirname(os.path.realpath('__file__'))
    # me tengo que meter a la ruta base/cyber_role y ejecutar este endpoint
    file_json = 'cyber_role/KSAT_JSON/Abilities.json'

    if not isfile(join(fileDir, file_json)):
        file_json = 'KSAT_JSON/Abilities.json'

    with open(file_json) as file:
        # Obtenemos el json del fichero
        data = json.load(file)

        equivalencia_nist = {}

        # ya tenemos el diccionario del nist, original
        values = list(data.values())
        keys = list(data.keys())

        for i in abilities_ids.items:
            if i.description in values:
                equivalencia_nist[i.id] = keys[values.index(i.description)]


    return render_template('general/ksat.html', title='Abilities',
                           lista_A=abilities_ids, l_A=abilities_list, verA=verA,
                           l_eq=list(equivalencia_nist.values()))


@bp_general.route('/t')
@login_required
@roles_required(['User','Admin'])
def show_t():

    """ Metodo para mostrar la informacion de los Tasks segun el NICE."""

    page = request.args.get('page', 1, type=int)
    tasks_ids = Task.query.order_by(Task.id.asc()).paginate(
        page, current_app.config['PAGE_ITEMS'], False)

    t = "myT000"
    tasks_list = [(f'{t}{i.id}' if (i.id < 10) else f'{"myT00"}{i.id}' if (i.id < 100)
                   else f'{"myT0"}{i.id}' if (i.id < 1000) else f'{"myT"}{i.id}', i.description) for i in tasks_ids.items]
    verT = True

    fileDir = os.path.dirname(os.path.realpath('__file__'))
    # me tengo que meter a la ruta base/cyber_role y ejecutar este endpoint
    file_json = 'cyber_role/KSAT_JSON/Tasks.json'

    if not isfile(join(fileDir, file_json)):
        file_json = 'KSAT_JSON/Tasks.json'

    with open(file_json) as file:
        # Obtenemos el json del fichero
        data = json.load(file)

        equivalencia_nist = {}

        # ya tenemos el diccionario del nist, original
        values = list(data.values())
        keys = list(data.keys())

        for i in tasks_ids.items:
            if i.description in values:
                equivalencia_nist[i.id] = keys[values.index(i.description)]


    return render_template('general/ksat.html', title='Tasks',
                           lista_T=tasks_ids, l_T=tasks_list, verT=verT,
                           l_eq=list(equivalencia_nist.values()))


@bp_general.route('/test_ksat', methods=['GET', 'POST'])
@login_required
@roles_required(['User','Admin'])
def test_ksat():

    """ Metodo que sirve para que un usuario realice un test en conocimientos en KSATs.

    Este metodo consistira en que un usuario, tendra un formulario en el que 
    podra elegir unos identificadores con unos niveles del 0-5 en Knowledges, Skills
    Abilities y Tasks segun el NICE.

    """

    knowledges_ids = Knowledge.query.order_by(Knowledge.id.asc())
    skills_ids = Skill.query.order_by(Skill.id.asc())
    abilities_ids = Ability.query.order_by(Ability.id.asc())
    tasks_ids = Task.query.order_by(Task.id.asc())

    k = "myK000"
    knowledges_list = [f'{k}{i.id}' if (i.id < 10) else f'{"myK00"}{i.id}'
                        if (i.id < 100) else f'{"myK0"}{i.id}' for i in knowledges_ids]
    s = "myS000"
    skills_list = [f'{s}{i.id}' if (i.id < 10) else f'{"myS00"}{i.id}'
                    if (i.id < 100) else f'{"myS0"}{i.id}' for i in skills_ids]
    a = "myA000"
    abilities_list = [f'{a}{i.id}' if (i.id < 10) else f'{"myA00"}{i.id}'
                       if (i.id < 100) else f'{"myA0"}{i.id}' for i in abilities_ids]
    t = "myT000"
    tasks_list = []
    for i in tasks_ids:
        clave = f'{t}{i.id}' if (i.id < 10) else f'{"myT00"}{i.id}' if (i.id < 100)\
            else f'{"myT0"}{i.id}' if (i.id < 1000) else f'{"myT"}{i.id}'
        tasks_list.append((clave, clave))

    form = TestForm(request.form)

    # Hacemos un for por tamaños
    # primero tenemos que saber que lista es la mas larga max_lenListKSa
    max_lenListKSa = max(
        [len(knowledges_list), len(skills_list), len(abilities_list)])

    dictksa = {}

    for i in range(max_lenListKSa):
        # Vamos creando segun lo vamos utilizando
        lapfor = KsaForm()
        if i < len(knowledges_list):
            lapfor.levelK.label = knowledges_list[i]

        if i < len(skills_list):
            lapfor.levelS.label = skills_list[i]

        if i < len(abilities_list):
            lapfor.levelA.label = abilities_list[i]

        dictksa[i] = lapfor

    form.ksas = dictksa
    form.tasks.choices = tasks_list

    if form.validate_on_submit():
        """Pasos para la asignacion de un KSAT en un user,
        # Debo crear primero un objecto KSAt y meterlo en su JSON
        Una vez creado el KSAT con su id, este valor será asignado al usuario y listo.
        """
        L_levelsK = request.form.getlist('levelK')
        L_levelsS = request.form.getlist('levelS')
        L_levelsA = request.form.getlist('levelA')
        x = 0
        w = 0
        y = 0
        k_id_level = {}
        s_id_level = {}
        a_id_level = {}

        for i in range(max_lenListKSa):

            if i < len(knowledges_list):
                # Si un level es mayor que cero sera un id KSA valido
                if(int(L_levelsK[i]) > 0):
                    # Recuerda la clave de este dict  es tipo myK0001...
                    k_id_level[knowledges_list[i]] = {
                        "id_number": knowledges_ids[i].id,
                        "level": int(L_levelsK[i]),
                        "description": knowledges_ids[i].description
                    }

            if i < len(skills_list):
                if(int(L_levelsS[i]) > 0):
                    # Recuerda la clave de este dict  es tipo myS0001...
                    s_id_level[skills_list[i]] = {
                        "id_number": skills_ids[i].id,
                        "level": int(L_levelsS[i]),
                        "description": skills_ids[i].description
                    }

            if i < len(abilities_list):
                if(int(L_levelsA[i]) > 0):
                    # Recuerda la clave de este dict  es tipo myA0001...
                    a_id_level[abilities_list[i]] = {
                        "id_number": abilities_ids[i].id,
                        "level": int(L_levelsA[i]),
                        "description": abilities_ids[i].description
                    }

        dictT = {}

        for i in form.tasks.data:
            Lista = [int(i)
                     for i in i.split("myT") if i.isdigit()]
            # t = Task.query.filter_by(id=Lista[0]).first()
            # Restamos uno a Lista[0] ya que los id-simbolicos empiezan en 1, y
            # una lista en 0
            dictT[i] = tasks_ids[Lista[0]-1].description


        # COMPROBACION SI UN USER TIENE UNoS KSA CON UN NIVEL, EXISTIRA ESE KSA
        # SI ES MAYOR QUE 0

        idd = session['user_id']
        nameUser_id = f'{"User"}{"_"}{idd}'

        # Caso cuando no exista ningun KSAT para el usuario en uso
        if(not current_user.ksat):
            new_ksat = Ksat(
                user_id=idd,
                name=nameUser_id,
                date=datetime.datetime.utcnow(),
                ksat_ids={
                    "knowledges_ids": k_id_level,
                    "skills_ids":     s_id_level,
                    "abilities_ids":  a_id_level,
                    "tasks_ids":      dictT
                }
            )
            try:
                correct = True
                db.session.add(new_ksat)
                db.session.commit()
            except Exception as e:
                # Catch anything unknown
                print(e)
                correct = False
            finally:
                if not correct:
                    # Cleanup and show error
                    db.session.rollback()
                    Flash('Error creating KSAT atribute.','error')
                else:
                    flash('Congratulations, We can start work now.','success')
                    return redirect(url_for('general.test_target_ksat'))

        # Modificacion de un kSAT
        else:

            #Borramos los KSAts old en caso de que el usuario haya hecho pruebas antes(realizado cursos)
            if "finished_courses" in current_user.ksat.ksat_ids:
                for i in current_user.ksat.ksat_ids["finished_courses"]:
                    name=f'{current_user.username}{"_old_ksa_"}{i}'
                    ksat_old= Ksat.query.filter_by(name=name).first()
                    db.session.delete(ksat_old)

            current_user.ksat.date = datetime.datetime.utcnow(),
            current_user.ksat.ksat_ids = {
                "knowledges_ids": k_id_level,
                "skills_ids":     s_id_level,
                "abilities_ids":  a_id_level,
                "tasks_ids":      dictT
            }

            try:
                correct = True
                db.session.commit()
            except Exception as e:
                print(e)
                correct = False
            finally:
                if not correct:
                    # Cleanup and show error
                    db.session.rollback()
                    flash('Error when modifying the KSAT attribute.','error')
                else:
                    flash('Our ksat was modified.','success')
                    return redirect(url_for('general.show_ksat_user'))

    else:
        # Si no se ha validado el testKSAT
        return render_template('general/test_ksat.html', title='Test', form=form, list_K=knowledges_list,list_S=skills_list,
                                list_A= abilities_list)

    return render_template('general/test_ksat.html', title='Test', form=form, list_K=knowledges_list,list_S=skills_list,
                                list_A= abilities_list)


@bp_general.route('/select_wk_role/<path:name>', methods=['GET'])
@login_required
@roles_required(['User','Admin'])
def select_wk_role(name):

    """ Metodo que sirve para obtener info de los KSAs de un determinado work-role.

    Args:
        name: Nombre del work-role que se buscara en la DB.

    """

    wk_roles_ksas = WorkRole.query.filter_by(name=name).first()
    user_ksat=current_user.ksat
    noexist_ksat = False
    # Si no existe ksat para el usuario
    if(not user_ksat):
        noexist_ksat = True
        flash("The user does not have KSAT.","warn")
        return redirect(url_for('general.test_ksat'))

    return jsonify(wk_roles_ksas.ksat_ids, user_ksat.ksat_ids)


@bp_general.route('/test_target_ksat', methods=['GET', 'POST'])
@login_required
@roles_required(['User','Admin'])
def test_target_ksat():

    """ Metodo que sirve para obtener los cursos optimos, mediante una seleccion de restricciones de learning objects."""

    form = TargetForm(request.form)

    # Obtenemos los KSA para meter los labels(ID-simbolicos) en los form
    knowledges_ids = Knowledge.query.order_by(Knowledge.id.asc())
    skills_ids = Skill.query.order_by(Skill.id.asc())
    abilities_ids = Ability.query.order_by(Ability.id.asc())

    k = "myK000"
    knowledges_list = [f'{k}{i.id}' if (i.id < 10) else f'{"myK00"}{i.id}'
                        if (i.id < 100) else f'{"myK0"}{i.id}' for i in knowledges_ids]
    s = "myS000"
    skills_list = [f'{s}{i.id}' if (i.id < 10) else f'{"myS00"}{i.id}'
                    if (i.id < 100) else f'{"myS0"}{i.id}' for i in skills_ids]
    a = "myA000"
    abilities_list = [f'{a}{i.id}' if (i.id < 10) else f'{"myA00"}{i.id}'
                       if (i.id < 100) else f'{"myA0"}{i.id}' for i in abilities_ids]

    # Obtenemmos los work roles para meter los names a elegir
    wroles_choices = [(i.name, i.name) for i in WorkRole.query.all()]
    # Introducimos en la primera posicion el valor por default
    wroles_choices.insert(0, (('Default', 'Default')))
    # Lo metemos en el formulario
    form.selectWroles.choices = wroles_choices


    list_IdsK = []
    list_IdsS = []
    list_IdsA = []

    #Obtenemos la lista mas larga de los KSA de la DB
    max_lenListKSa_init = max(len(knowledges_list), len(skills_list), len(abilities_list))

    dictksa = {}

    # Info ksa de un usuario, para saber sus labels y sus levels
    user_ksat =current_user.ksat
    noexist_ksat = False
    # Si no existe ksat para el usuario
    if(not user_ksat):
        noexist_ksat = True
        return redirect(url_for('general.test_ksat'))

    #Aqui recorremos todas las listas para rellenar los subformularios KSA
    for i in range(max_lenListKSa_init):
        lapfor = TargetKsaForm()
        if i < len(knowledges_list):
            lapfor.levelK_req.label = knowledges_list[i]
            lapfor.levelK_goal.label = knowledges_list[i]
            #Si el label de knowledges pertenece al diccionario Knowledges del usuario se introduce su level(del User)
            if knowledges_list[i] in user_ksat.ksat_ids['knowledges_ids']:
                value = user_ksat.ksat_ids['knowledges_ids'][knowledges_list[i]]['level']
                lapfor.levelK_req.choices = [(value, str(value))]

        if i < len(skills_list):
            lapfor.levelS_req.label = skills_list[i]
            lapfor.levelS_goal.label = skills_list[i]
            #Si el label de skills pertenece al diccionario Skills del usuario se introduce su level(del User)
            if skills_list[i] in user_ksat.ksat_ids['skills_ids']:
                value = user_ksat.ksat_ids['skills_ids'][skills_list[i]]['level']
                lapfor.levelS_req.choices = [(value, str(value))]

        if i < len(abilities_list):
            lapfor.levelA_req.label = abilities_list[i]
            lapfor.levelA_goal.label = abilities_list[i]
            #Si el label de abilities pertenece al diccionario Abilities del usuario se introduce su level(del User)
            if abilities_list[i] in user_ksat.ksat_ids['abilities_ids']:
                value = user_ksat.ksat_ids['abilities_ids'][abilities_list[i]]['level']
                lapfor.levelA_req.choices = [(value, str(value))]

        #Anadimos al diccionario auxiliar los subformularios
        dictksa[i] = lapfor
    #Metemos el dict ksa que acumulo los subformularios KSA en el formulario principal
    form.ksas = dictksa

    # Cuando hagamos una peticion POST y se valide el formulario entrara por este if
    if form.validate_on_submit():
        # Obtenemos los datos del formulario(sus levels que ha seleccionado el usuario)
        L_levelsKreq = request.form.getlist('levelK_req')
        L_levelsKgoal = request.form.getlist('levelK_goal')
        L_levelsSreq = request.form.getlist('levelS_req')
        L_levelsSgoal = request.form.getlist('levelS_goal')
        L_levelsAreq = request.form.getlist('levelA_req')
        L_levelsAgoal = request.form.getlist('levelA_goal')

        # Diccionarios para almacenar el id-simbolico(K0001) & level
        kreq_id_level = {}
        kgoal_id_level = {}
        sreq_id_level = {}
        sgoal_id_level = {}
        areq_id_level = {}
        agoal_id_level = {}

        # Obtenemos el tamano maximo de las listas principales de levels obtenidas al dar submit
        max_lenListKSa = max(len(L_levelsKreq), len(L_levelsSreq), len(L_levelsAreq))

        # Vemos que work role ha sido seleccionado y se busca en la db
        name_wk = request.form['selectWroles']
        wk_roles_ksas = WorkRole.query.filter_by(name=name_wk).first()

        # Nos servira para saber si un valor KSA ( level) es mayor que 0
        k_level_upperZero=False
        s_level_upperZero= False
        a_level_upperZero= False

        # Se obtiene el numero maximo de la lista de los KSAs para iterarlo de una sola vez en un for
        for i in range(max_lenListKSa):
            #Recorremos la lista de los levels de Knowledges
            if i < len(L_levelsKreq):
                #Reiniciamos esta variable, porque sera distinta en cada iteracion
                k_level_upperZero= False

                # SOLO EN EL CASO DE QUE SELECT WK ROLES SEA DISTINTO DE DEFAULT
                if name_wk != 'Default':

                    # Este seria el primer label de wkRole
                    label_wkrole = list(
                        wk_roles_ksas.ksat_ids[name_wk]['knowledges_ids'].keys())[i]

                    # Compararemos los KSAS del formulario con los que posee el usuario.
                    # BUSQUEDA UNO POR UNO SETEANDO EL LABEL Y EL VALUE DEL FORMULARIO
                    for k in user_ksat.ksat_ids['knowledges_ids']:
                        # Obtenemos el level del label de un knowledges
                        value = user_ksat.ksat_ids['knowledges_ids'][k]['level']
                        # Si el label de un usuario y de un workRole (knowledges) son iguales y el level del user 
                        # es mayor que -1 se transmite ese level al formulario y su label
                        if k == label_wkrole and value >-1:
                            k_level_upperZero = True
                            form.ksas[i]['levelK_req'].choices = [(value, str(value))]

                    # Si no hay un Knowledges del usuario se establece por default el select level del subform
                    if not k_level_upperZero:
                        form.ksas[i]['levelK_req'].choices = [(-1,'-1'),(0, '0'), (1, '1'), (2, '2'), (3, '3'), (4, '4'), (5, '5')]

                    # PREREQUISITES and OUTCOMES
                    form.ksas[i]['levelK_req'].label = label_wkrole
                    form.ksas[i]['levelK_goal'].label = label_wkrole
                    # Seteamos el data de cada subformulario knowledges para que pueda ser validado posteriormente
                    form.ksas[i]['levelK_req'].data = L_levelsKreq[i]
                    form.ksas[i]['levelK_goal'].data = L_levelsKgoal[i]

                    # Si un level es mayor que cero sera un id KSA valido y level
                    # PREREQUISITES
                    if(int(L_levelsKreq[i]) > -1):
                        # Recuerda la clave de este dict es tipo K001...
                        kreq_id_level[label_wkrole] = int(L_levelsKreq[i])
                    # OUTCOMES
                    if(int(L_levelsKgoal[i]) > -1):
                        # Recuerda la clave de este dict es tipo K001...
                        kgoal_id_level[label_wkrole] = int(L_levelsKgoal[i])

                else:# cuando es por default no hemos elegido ningun name de wk roles
                    # Esto sirve para que pueda ser validado, recuerda los data son valores que se tiene que validar
                    # En el estado por default no hace falta modificar los labels o choices (KSA de los user), xq ya se
                    # hicieron antes del submit (Post)
                    form.ksas[i].levelK_req.data = L_levelsKreq[i]
                    form.ksas[i].levelK_goal.data = L_levelsKgoal[i]

                    # Si un level es mayor que -1 sera un id KSA valido y level
                    if(int(L_levelsKreq[i]) > -1):
                        # Recuerda la clave de este dict  es tipo myK001...
                        kreq_id_level[knowledges_list[i]] = int(L_levelsKreq[i])
                    if(int(L_levelsKgoal[i]) > -1):
                        # Recuerda la clave de este dict  es tipo myK001...
                        kgoal_id_level[knowledges_list[i]] = int(L_levelsKgoal[i])

            # Recorremos la lista de los levels de Skills
            if i < len(L_levelsSreq):
                # COMO ESTO ES SUCESIVO ,METE VALORES DE FORMA SUCESIVA
                # COMO LOS NIVELES EXISTENTES ANTERIORMENTE

                s_level_upperZero= False

                if name_wk != 'Default':
                    label_wkrole = list(
                        wk_roles_ksas.ksat_ids[name_wk]['skills_ids'].keys())[i]

                    # CUANDO OBTENEMOS LOS VALORES L_levelsKreq ,.... ES EL
                    # FORMULARIO ANTIGUO YA PREDEFINIDO CON KSA DEL USUARIO
                    # INCLUIDO

                    # BUSQUEDA UNO POR UNO SETEANDO EL LABEL Y EL VALUE DEL FORMULARIO
                    for s in user_ksat.ksat_ids['skills_ids']:
                        value = user_ksat.ksat_ids['skills_ids'][s]['level']

                        if s == label_wkrole and value > -1:
                            s_level_upperZero= True
                            form.ksas[i]['levelS_req'].choices = [(value, str(value))]

                    # Cuando es por default es decir los labels no coinciden y el value no es mayor que 0
                    if not s_level_upperZero:
                        form.ksas[i]['levelS_req'].choices = [(-1,'-1'),(0, '0'), (1, '1'), (2, '2'), (3, '3'), (4, '4'), (5, '5')]

                    # PREREQUISITES AND OUTCOMES
                    form.ksas[i]['levelS_req'].label = label_wkrole
                    form.ksas[i]['levelS_goal'].label = label_wkrole
                    form.ksas[i]['levelS_req'].data = L_levelsSreq[i]
                    form.ksas[i]['levelS_goal'].data = L_levelsSgoal[i]

                    # Si un level es mayor que -1 sera un id KSA valido y level
                    # PREREQUISITES
                    if(int(L_levelsSreq[i]) > -1):
                        # Recuerda la clave de este dict  es tipo K001...
                        sreq_id_level[label_wkrole] = int(L_levelsSreq[i])
                    # OUTCOMES
                    if(int(L_levelsSgoal[i]) > -1):
                        # Recuerda la clave de este dict  es tipo K001...
                        sgoal_id_level[label_wkrole] = int(L_levelsSgoal[i])

                else:
                    # Cuando es por default no hemos elegigo ningun name de wk roles
                    # Esto sirve para que pueda ser validado, recuerda los data son valores que se tiene que validar
                    form.ksas[i]['levelS_req'].data = L_levelsSreq[i]
                    form.ksas[i]['levelS_goal'].data = L_levelsSgoal[i]

                    # Si un level es mayor que cero sera un id KSA valido y level
                    if(int(L_levelsSreq[i]) > -1):
                        # Recuerda la clave de este dict  es tipo K001...
                        sreq_id_level[skills_list[i]] = int(L_levelsSreq[i])
                    if(int(L_levelsSgoal[i]) > -1):
                        # Recuerda la clave de este dict  es tipo K001...
                        sgoal_id_level[skills_list[i]] = int(L_levelsSgoal[i])

            # Recorremos la lista de los levels de Abilities
            if i < len(L_levelsAreq):
                a_level_upperZero= False

                if name_wk != 'Default':
                    label_wkrole = list(
                        wk_roles_ksas.ksat_ids[name_wk]['abilities_ids'].keys())[i]

                    for a in user_ksat.ksat_ids['abilities_ids']:
                        value = user_ksat.ksat_ids['abilities_ids'][a]['level']

                        if a == label_wkrole and value > -1:
                            a_level_upperZero = True
                            form.ksas[i]['levelA_req'].choices = [(value, str(value))]

                    #Cuando es por default es decir los labels no coinciden y el value no es mayor que 0, es como un reset
                    if not a_level_upperZero:
                        form.ksas[i]['levelA_req'].choices = [(-1,'-1'),(0, '0'), (1, '1'), (2, '2'), (3, '3'), (4, '4'), (5, '5')]

                    #PREREQUISITES and OUTCOMES
                    form.ksas[i]['levelA_req'].label = label_wkrole
                    form.ksas[i]['levelA_goal'].label = label_wkrole
                    form.ksas[i]['levelA_req'].data = L_levelsAreq[i]
                    form.ksas[i]['levelA_goal'].data = L_levelsAgoal[i]

                    # Si un level es mayor que -1 sera un id KSA valido y level
                    # PREREQUISITES
                    if(int(L_levelsAreq[i]) > -1):
                        # Recuerda la clave de este dict  es tipo A001...
                        areq_id_level[label_wkrole] = int(L_levelsAreq[i])
                    # OUTCOMES
                    if(int(L_levelsAgoal[i]) > -1):
                        # Recuerda la clave de este dict  es tipo A001...
                        agoal_id_level[label_wkrole] = int(L_levelsAgoal[i])

                else:

                    form.ksas[i]['levelA_req'].data = L_levelsAreq[i]
                    form.ksas[i]['levelA_goal'].data = L_levelsAgoal[i]

                    # Si un level es mayor que -1 sera un id KSA valido y level
                    if(int(L_levelsAreq[i]) > -1):
                        # Recuerda la clave de este dict  es tipo K001...
                        areq_id_level[abilities_list[i]] = int(L_levelsAreq[i])
                    if(int(L_levelsAgoal[i]) > -1):
                        # Recuerda la clave de este dict  es tipo K001...
                        agoal_id_level[abilities_list[i]] = int(L_levelsAgoal[i])


        # Validamos solo el tamano maximo de las tres tuplas KSA que existen en el momento que damos submit
        for i in range(max_lenListKSa):
            # Validamos cada subform de KSA ( Tripleta con Prerequisites and
            # Outcomes)
            if form.ksas[i].validate() == False:
                # Se vuelve al estado default una vez que no se ha validado un subformulario y
                # se pasan los siguientes parametros
                return render_template('general/targeted_ksat.html', title='Targeted KSAT', form=form,
                        listK=knowledges_list,listS=skills_list,listA=abilities_list,ksa_user=user_ksat.ksat_ids,
                        sizeK=len(L_levelsKreq), sizeS=len(L_levelsSreq), sizeA=len(L_levelsAreq))

        # Commprobacion si no existe ningun KSA, se debe elegir minimo un KSA.
        if not kreq_id_level and not kgoal_id_level and not sreq_id_level and not sgoal_id_level \
                and not areq_id_level and not agoal_id_level:
            flash("You must choose at least one KSA!","warn")
            return render_template('general/targeted_ksat.html', title='Targeted KSAT', form=form, notKSA=True)

        t_min = request.form['time_min']
        t_max = request.form['time_max']
        c_min = request.form['cost_min']
        c_max = request.form['cost_max']
        r_min = request.form['reput_min']
        r_average = request.form['reput_average']

        # El rango de valores de los modulos de un curso de LO
        nk_min = request.form['nk_min']
        nk_max = request.form['nk_max']

        format_ksa_req = {}
        format_ksa_goal = {}

        lista_ids = []
        count = 0
        tam_max_dict_ksa = max(len(kreq_id_level),len(sreq_id_level),len(areq_id_level))

        # Este for nos servirá para darle un formato adecuado a los datos recibidos por el formulario,
        # y poderselos enviar al microservicio
        for x in range(tam_max_dict_ksa):
            lista_ksa_req = []
            lista_ksa_out = []

            # EN TODO MOMENTO SABEMOS QUE IDENTIFICADOR TIENE CADA REQ AND OUT
            if list(kreq_id_level.keys()):

                name_k_req = list(kreq_id_level.keys())[0]
                lista_ids.append(name_k_req)
                name_k_goal = list(kgoal_id_level.keys())[0]

                value_preq = kreq_id_level.pop(str(name_k_req))
                if value_preq == 0:
                    lista_ksa_req.append(0)
                    lista_ksa_req.append(0)
                    lista_ksa_req.append(0)
                else:
                    lista_ksa_req.append(1)
                    lista_ksa_req.append(1)
                    lista_ksa_req.append(value_preq)

                value_goal = kgoal_id_level.pop(str(name_k_goal))
                if value_goal == 0:
                    lista_ksa_out.append(0)
                    lista_ksa_out.append(0)
                    lista_ksa_out.append(0)
                else:
                    lista_ksa_out.append(1)
                    lista_ksa_out.append(value_preq+1)
                    lista_ksa_out.append(value_goal)

            if lista_ksa_req:
                format_ksa_req[str(count)] = lista_ksa_req
                format_ksa_goal[str(count)] = lista_ksa_out
                lista_ksa_req = []
                lista_ksa_out = []
            count+=1

            if list(sreq_id_level.keys()):

                name_s_req = list(sreq_id_level.keys())[0]
                lista_ids.append(name_s_req)
                name_s_goal = list(sgoal_id_level.keys())[0]

                value_preq = sreq_id_level.pop(str(name_s_req))
                if value_preq == 0:
                    lista_ksa_req.append(0)
                    lista_ksa_req.append(0)
                    lista_ksa_req.append(0)
                else:
                    lista_ksa_req.append(1)
                    lista_ksa_req.append(1)
                    lista_ksa_req.append(value_preq)

                value_goal = sgoal_id_level.pop(str(name_s_goal))
                if value_goal == 0:
                    lista_ksa_out.append(0)
                    lista_ksa_out.append(0)
                    lista_ksa_out.append(0)
                else:
                    lista_ksa_out.append(1)
                    lista_ksa_out.append(value_preq+1)
                    lista_ksa_out.append(value_goal)


            if lista_ksa_req:
                format_ksa_req[str(count)] = lista_ksa_req
                format_ksa_goal[str(count)] =  lista_ksa_out
                lista_ksa_req = []
                lista_ksa_out = []
            count+=1

            if list(areq_id_level.keys()):

                name_a_req = list(areq_id_level.keys())[0]
                name_a_goal = list(agoal_id_level.keys())[0]
                lista_ids.append(name_a_req)

                value_preq = areq_id_level.pop(str(name_a_req))
                if value_preq == 0:
                    lista_ksa_req.append(0)
                    lista_ksa_req.append(0)
                    lista_ksa_req.append(0)
                else:
                    lista_ksa_req.append(1)
                    lista_ksa_req.append(1)
                    lista_ksa_req.append(value_preq)

                value_goal = agoal_id_level.pop(str(name_a_goal))
                if value_goal == 0:
                    lista_ksa_out.append(0)
                    lista_ksa_out.append(0)
                    lista_ksa_out.append(0)
                else:
                    lista_ksa_out.append(1)
                    lista_ksa_out.append(value_preq+1)
                    lista_ksa_out.append(value_goal)

            if lista_ksa_req:
                format_ksa_req[str(count)] = lista_ksa_req
                format_ksa_goal[str(count)] =  lista_ksa_out
                lista_ksa_req = []
                lista_ksa_out = []
            count+=1

        # Una vez tengamos todo los valores formateados segun el algoritmo del microservicio
        # Procedemos a llamarlo a continuacion.

        # Tenemos los labels ordenados, recuerda que cuando haya un valor de format_ksa_re
        # que sea 0, no habra label ID-KSA, es decir, la comprobacion se hará primeramente 
        # desde el forma_ksa_req, para ver si existe el ID-KSA

        send_dictKSA = {
            "Prerequisites": format_ksa_req,
            "Outcomes": format_ksa_goal
        }
        # Obtenemos el numero de learning object
        num_learning_concept = len(format_ksa_req)
        return redirect(url_for('lo.create_optimal_course', nk_min=nk_min, nk_max=nk_max, t_min=t_min, t_max=t_max, c_min=c_min,
                        c_max=c_max,r_min=r_min, r_average=r_average,num_learning_concept=num_learning_concept,
                        dictksa=str(send_dictKSA),list_label_ids=lista_ids))

    return render_template('general/targeted_ksat.html', title='Targeted KSAT', form=form,
        listK=knowledges_list,listS=skills_list,listA=abilities_list,ksa_user=user_ksat.ksat_ids)



@bp_general.route('/show_ksat_user')
@login_required
@roles_required(['User','Admin'])
def show_ksat_user():

    """ Metodo para motrar los KSAT que tiene un usuario."""

    noexist_ksat = False
    # Si no existe ksat para el usuario
    if(not current_user.ksat):
        noexist_ksat = True
        return render_template('general/my_ksat.html', title='MyKSAT', noexist_ksat=noexist_ksat)

    return render_template('general/my_ksat.html', title='MyKSAT', myksats=current_user.ksat.ksat_ids)




# Listaremos los objetivos para llegar un WRole que tiene un usuario !
@bp_general.route('/show_top10_wk_role')
@login_required
@roles_required(['User','Admin'])
def show_top10_wk_role():

    """ METODO QUE SERVIRÁ PARA HACER UNA LISTA DE LOS 10 WORK ROLES MÁS SEMEJANTES AL USUARIO
     ACTUAL, CON RESPECTO A SUS KSAs, ES DECIR, UNA COMPARACION DE LOS KSAS DE LOS WK ROLES CON LOS
     DEL USUARIO. 

     Y EL ALGORITMO DE CALCULO SERÁ EL SIGUIENTE: SI UN WK ROLE TIENE X KSAS ESTOS SE MULTIPLICARAN 
     POR 5(LEVEL max) Y ESTO REPRESENTARA EL 100% DEL WorkRole, POR LO TANTO HAREMOS UNA REGLA DE 3.
     ADEMÁS TAMBIÉN MOSTRAREMOS A QUE WK ROLE SE PARECE MÁS EL USUARIO A LA DERECHA.

         POR EJEMPLO:

            WK_ ANALISTA : 20 KSAS * 5 = 100 --------> 1
            KSAS_USER: 5 DE ESTOS WK_ANALISTAS * CADA LEVEL ------> X

            NIVEL_PORCENTUAL_USER = (WK_ANALISTAS * CADA LEVEL) /(20 KSAS * 5)

    """

    #Cargar el KSAT actual del usuario
    if not current_user.ksat:
        flash('You do not have KSAs to get a top 10 work role.','warn')
        return redirect(url_for('general.show_dash'))

    workRoles = WorkRole.query.all()

    ksas_user={}
    knowledges_user = {}
    skills_user = {}
    abilities_user = {}

    if current_user.ksat:
        knowledges_user = current_user.ksat.ksat_ids['knowledges_ids']
        skills_user = current_user.ksat.ksat_ids['skills_ids']
        abilities_user = current_user.ksat.ksat_ids['abilities_ids']
        for x in knowledges_user:
            ksas_user[x]=knowledges_user[x]["level"]
        for x in skills_user:
            ksas_user[x] = skills_user[x]["level"]
        for x in abilities_user:
            ksas_user[x] = abilities_user[x]["level"]


    # YA ESTARIAN ORDENADOS EN FECHAS XQ SIEMPRE AÑADIMOS EL ULTIMO CURSO,
    # ES DECIR CON APPEND SIEMPRE ESCRIBIMOS EL ULTIMO CURSO

    # Lista donde almacenaremos los valores maximos que puede alcanzar un usuario
    lwk_value_max = []
    # Lista de valor maximo que alcanza un usuario por wkrole
    luser_value_max = []
    lista_wk_names = []
    pertence_ksa = False

    for i in workRoles:
        res = list(i.ksat_ids.keys())[0]
        # Obtenemos el nombre del work role
        firstkey = str(res)
        lista_wk_names.append(i.name)
        knowledges_wk = i.ksat_ids[firstkey]['knowledges_ids']
        skills_wk = i.ksat_ids[firstkey]['skills_ids']
        abilities_wk = i.ksat_ids[firstkey]['abilities_ids']
        # Almacenamos el valor maximo por cada wkrole
        lwk_value_max.append(len(knowledges_wk)*5+len(skills_wk)*5+len(abilities_wk)*5)

        #Nos servira para almacenar el valor maximo de un usuario con respecto al Wkrole
        value_ksa_user = 0

        for j in knowledges_wk:
            if j in ksas_user:
                pertence_ksa = True
                #Sumamos los levels que tiene el user con respecto al wkrole
                value_ksa_user += ksas_user[j]

        for j in skills_wk:
            if j in ksas_user:
                pertence_ksa = True
                value_ksa_user += ksas_user[j]

        for j in abilities_wk:
            if j in ksas_user:
                pertence_ksa = True
                value_ksa_user += ksas_user[j]

        #Significa que no tiene ningun ksa del wk role, el usuario actual
        if not pertence_ksa:
            luser_value_max.append(0)
        else:
            luser_value_max.append(value_ksa_user)



    #lista de calculos porcentuales al 100% como maximo
    lista_values = []

    for i,j in zip(luser_value_max,lwk_value_max):
        lista_values.append((i*100)/j)

    # Invertimos el diccionario clave:valor --> j:i
    dict_final_top10 = { j:i for i,j in zip(lista_wk_names,lista_values)}

    # Ordenamos la lista completa, de mayor a menor!
    lista_sort=sorted(dict_final_top10.items(), reverse=True)
    # Y elegimos solo los 10 primeros
    valores_ord = dict(lista_sort[0:10])

    return render_template('general/top10_wk_role.html', title='Top 10 Work Roles', top10_wkname=list(valores_ord.values()),
        top10_values=list(valores_ord.keys()))
