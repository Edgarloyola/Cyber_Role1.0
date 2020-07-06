# -*- coding: utf-8 -*-
# control supr elimina una lineapñ
"""This file contains general views."""

import datetime
import requests
import json
import random
import time
from flask import Blueprint,g,app, session,jsonify, render_template, flash, redirect, url_for, request,current_app
from flask_babel import _
from flask_user import login_required, roles_required
from flask_login import current_user, login_user
from sqlalchemy import and_,or_

from cyber_role import db, user_manager,celery,hashids_hasher
from celery.task import task
from cyber_role.models import User, Ksat, Knowledge, Skill, Ability, Task, LearningObject, Course
from cyber_role.forms import RegistrationForm, TestForm,SearchForm,SearchFilterForm
from psycopg2.errors import UniqueViolation


bp_lo = Blueprint('lo', __name__)


@celery.task(bind=True)
def long_task_course(self, target,user_id):

    payload = {'t_min': target['t_min'],
               't_max': target['t_max'],
               'c_min': target['c_min'],
               'c_max': target['c_max'],
               'r_min': target['r_min'],
               'r_average': target['r_average'],
               'nk_min': target['nk_min'],
               'nk_max': target['nk_max'],
               'num_learning_concept':target['num_learning_concept'],
               'dictksa': target['dictksa']}
    try:
        correct = True
        var = requests.get(
            "http://localhost:11025/create_optimal_lo", params=payload).json()
    except Exception as e:
        correct = False
        print(e)
    finally:
        if not correct:
            print("Failure to connect to the restful microservice.","error")
            return {'current': 100, 'total': 100, 'status': 'FAILURE','result': -2}


        #Eliminamos solo los cursos de un usuario, en el caso de que tenga cursos optimos
        delete_courses = Course.__table__.delete().where(Course.user_id == user_id)
        if delete_courses is not None:
            db.session.execute(delete_courses)
            db.session.commit()

        knowledges_ids = Knowledge.query.order_by(Knowledge.id.asc())
        skills_ids = Skill.query.order_by(Skill.id.asc())
        abilities_ids = Ability.query.order_by(Ability.id.asc())
        tasks_ids = Task.query.order_by(Task.id.asc())

        #Lista de labels que se eligieron en el test target de KSAs
        target_labels_ids = target['list_label_ids']

        k = "myK000"
        knowledges_list = [f'{k}{i.id}' if (i.id < 10) else f'{"myK00"}{i.id}'
                            if (i.id < 100) else f'{"myK0"}{i.id}' for i in knowledges_ids]
        s = "myS000"
        skills_list = [f'{s}{i.id}' if (i.id < 10) else f'{"myS00"}{i.id}'
                        if (i.id < 100) else f'{"myS0"}{i.id}' for i in skills_ids]
        a = "myA000"
        abilities_list = [f'{a}{i.id}' if (i.id < 10) else f'{"myA00"}{i.id}'
                           if (i.id < 100) else f'{"myA0"}{i.id}' for i in abilities_ids]

        idd = 0
        id_lo=0

        for i in var['list_courses']:

            #Vamos cargando el proceso
            self.update_state(state='PROGRESS',
                          meta={'current': idd, 'total': len(var['list_courses']),
                                'status': "En progreso..."})

            idd += 1
            total_time = 0
            total_cost = 0
            average_reputation = 0

            #Creamos el nuevo curso
            new_course = Course(
                user_id=user_id,
                name=f'{"Course_Optimal_"}{user_id}{"_"}{idd}',
                description=f'{"Descripcion_Optimal_"}{user_id}{"_"}{idd}',
                create_date=datetime.datetime.utcnow(),
                total_time = 0,
                total_cost = 0,
                average_reputation = 0,
                fitness_learning_goal = i['fitness_learning_goal'],
                fitness_time = i['fitness_time'],
                fitness_cost = i['fitness_cost'],
                fitness_reputation = i['fitness_reputation'],
                fitness_total = i['fitness_learning_goal']+i['fitness_time']+i['fitness_cost']+i['fitness_reputation']
            )

            for j in i['los']:
                try:
                    id_lo+=1

                    # Creamos un LO
                    new_lo = LearningObject(
                        time=j['time'],
                        cost=j['cost'],
                        reputation=j['reputation']
                    )

                    total_time += j['time']
                    total_cost += j['cost']
                    average_reputation += j['reputation']

                    list_preq = j['prerequisites'].split(" ")

                    # En este dict ira {"K001":"level"....}
                    kreq_id_level = {}
                    sreq_id_level = {}
                    areq_id_level = {}

                    # Creamos la lista de outcomes
                    list_out = j['outcomes'].split(" ")

                    # En este dict ira {"K001":"level"....}
                    kout_id_level = {}
                    sout_id_level = {}
                    aout_id_level = {}

                    count = 0

                    for x in range(2, len(list_preq), 3):

                        #Verificamos los labels
                        if target_labels_ids[count] in knowledges_list:

                            # Obtenemos el indice correspondiente de la lista de ID-simbolicos, para obtener su info
                            index = knowledges_list.index(target_labels_ids[count])

                            kreq_id_level[target_labels_ids[count]] = {
                            "id_number": knowledges_ids[index].id,
                            "level": int(list_preq[x]),
                            "description": knowledges_ids[index].description
                            }

                            kout_id_level[target_labels_ids[count]] = {
                            "id_number": knowledges_ids[index].id,
                            "level": int(list_out[x]),
                            "description": knowledges_ids[index].description
                            }

                        if target_labels_ids[count] in skills_list:

                            index = skills_list.index(target_labels_ids[count])

                            sreq_id_level[target_labels_ids[count]] = {
                                "id_number": skills_ids[index].id,
                                "level": int(list_preq[x]),
                                "description": skills_ids[index].description
                            }

                            sout_id_level[target_labels_ids[count]] = {
                                "id_number": skills_ids[index].id,
                                "level": int(list_out[x]),
                                "description": skills_ids[index].description
                            }


                        if target_labels_ids[count] in abilities_list:

                            index = abilities_list.index(target_labels_ids[count])

                            areq_id_level[target_labels_ids[count]] = {
                                "id_number": abilities_ids[index].id,
                                "level": int(list_preq[x]),
                                "description": abilities_ids[index].description
                            }

                            aout_id_level[target_labels_ids[count]] = {
                                "id_number": abilities_ids[index].id,
                                "level": int(list_out[x]),
                                "description": abilities_ids[index].description
                            }

                        #Counter of list label targetKSA
                        count += 1

                    # Creamos un KSAT para requisitos del LO
                    new_ksat_req = Ksat(
                        # El name podria ser la concatenacion de username + id del usuario
                        # + la hora que se creo
                        name=f'{"Learning_object_"}{user_id}{"_"}{id_lo}{"_requirements"}',
                        date=datetime.datetime.utcnow(),
                        ksat_ids={
                            "knowledges_ids": kreq_id_level,
                            "skills_ids":     sreq_id_level,
                            "abilities_ids":  areq_id_level,
                        }
                    )

                    # Creamos un KSAT para los outcomes de un LO
                    new_ksat_out = Ksat(
                        # El name sera la concatenacion de un LO + identificador de un usuario + el identificador de un LO.
                        name=f'{"Learning_object_"}{user_id}{"_"}{id_lo}{"_outcomes"}',
                        date=datetime.datetime.utcnow(),
                        ksat_ids={
                            "knowledges_ids": kout_id_level,
                            "skills_ids":     sout_id_level,
                            "abilities_ids":  aout_id_level,
                        }
                    )

                    #anadimos los ksas al new Learning Object
                    new_lo.ksats.extend([new_ksat_req,new_ksat_out])

                    correct = True
                    #anadimos el nuevo LO con sus respectivos req an out
                    db.session.add_all([new_lo, new_ksat_req, new_ksat_out])

                # except UniqueViolation as e:
                #     # get error code
                #     print(e)
                #     correct = False
                except Exception as e:
                    print(e)
                    correct = False
                finally:
                    if not correct:
                        print("Error when creating a Learning object with requirements and outcomes.")
                        return {'current': 100, 'total': 100, 'status': 'FAILURE','result': -1}
                    else:
                        #añadimos los learning objects a un curso
                        new_course.los.add(new_lo)

            new_course.total_time = total_time
            new_course.total_cost = total_cost
            new_course.average_reputation = average_reputation/len(i['los'])
            try:
                correct = True
                #Añadimos a la DB el curso con sus atributos
                db.session.add(new_course)

                user = User.query.filter_by(id=user_id).first()
                user.course.append(new_course)
            except Exception as e:
                print(e)
                correct = False
            finally:
                if not correct:
                    print("Error when adding the course with its attributes to the DB.")
                    return {'current': 100, 'total': 100, 'status': 'FAILURE','result': -1}
                else:
                    print("We add to the DB the course with its LOs modules and its attributes.")

        try:
            correct = True
            db.session.commit()
        except Exception as e:
            print(e)
            correct = False
        finally:
            if not correct:
                # Limpiamos y mostrarmos el error
                db.session.rollback()
                print('Error when creating a course list.')
                return {'current': 100, 'total': 100, 'status': 'FAILURE','result': -1}
            else:
                print("All courses were created with their Learning Objects.")

        return {'current': 100, 'total': 100, 'status': 'Task completed!',
            'result': 200}


@bp_lo.route('/create_optimal_course', methods=['GET'])
@login_required
@roles_required(['User','Admin'])
def create_optimal_course():

    target = {
        "t_min":request.args['t_min'],
        "t_max":request.args['t_max'],
        "c_min":request.args['c_min'],
        "c_max":request.args['c_max'],
        "r_min":request.args['r_min'],
        "r_average":request.args['r_average'],
        "num_learning_concept":request.args['num_learning_concept'],
        "dictksa":request.args['dictksa'],
        "nk_min":request.args['nk_min'],
        "nk_max":request.args['nk_max'],
        "list_label_ids":request.args.getlist('list_label_ids')
        }

    try:
        user_id = current_user.id
        task = long_task_course.delay(target,user_id)
        correct=True
    except Exception as e:
        print(e)
        correct=False
    finally:
        if not correct:
            flash('Broker-celery connection failure.','error')
            return render_template('lo/show_optimal_course.html', conectionFailed=True, title='LOS')
        else:
            session['task_id'] = task.id
            flash('The Optimal Courses are being created!','success')
            return render_template('lo/progress_optimal_course.html', title='Optimal LOS - Progress',
                            task_id=task.id)

    return render_template('lo/progress_optimal_course.html', title='Optimal LOS - Progress')

@bp_lo.route('/status/<task_id>')
def taskstatus(task_id):
    task = long_task_course.AsyncResult(task_id)
    if task.state == 'PENDING':
        response = {
            'state': task.state,
            'current': 0,
            'total': 1,
            'status': 'Pending...'
        }
    elif task.state != 'FAILURE':
        response = {
            'state': task.state,
            'current': task.info.get('current', 0),
            'total': task.info.get('total', 1),
            'status': task.info.get('status', '')
        }
        if 'result' in task.info:
            response['result'] = task.info['result']

            if response['result'] == -2:
                session['TimeoutMS'] = True
            else:
                session.pop('TimeoutMS', None)
            #Seteamos por defecto el task_id
            session.pop('task_id', None)
    else:
        # si algo salio mal
        response = {
            'state': task.state,
            'current': 1,
            'total': 1,
            'status': str(task.info),  # aqui se mostrara el error
        }


    return jsonify(response)


@bp_lo.route('/manage_optimal_course', methods=['GET','POST'])
@login_required
@roles_required('Admin')
def manage_optimal_course():
    page = request.args.get('page', 1, type=int)
    course_ids = Course.query.order_by(Course.id.asc()).paginate(
        page, current_app.config['PAGE_ITEMS'], False)

    search_form = SearchForm(request.form)

    if not course_ids.items:
        flash('There are not Optimal Courses.','error')
        return render_template('lo/manage_optimal_course.html',search_form=search_form,
                                 title='Courses')


    # Course.reindex()
    # current_app.elasticsearch.indices.delete('courses')

    if search_form.validate_on_submit():
        page = request.args.get('page', 1, type=int)
        courses, total = Course.search(request.form['q'], page,current_app.config['PAGE_ITEMS'])

        #Pues habria que hacer una paginacion manual conforme a los resultados de elastisearch
        next_url = url_for('lo.manage_optimal_course.html', q=request.form['q'], page=page+1) \
            if total > page * current_app.config['PAGE_ITEMS'] else None
        prev_url = url_for('lo.manage_optimal_curso.html', q=request.form['q'], page=page-1) \
            if page > 1 else None

        return render_template('lo/manage_optimal_course.html', title=_('Courses'),
            search_form=search_form,courses=courses,next_url=next_url, prev_url=prev_url)

    if not request.args.get('delete'):
        return render_template('lo/manage_optimal_course.html', title='Courses',
            search_form=search_form,lista_courses=course_ids)
    else:#Remove an ability
        id_hash = request.args.get('id')
        if not id_hash or id_hash=='':
            flash("There is no ID.","error")
            return render_template('lo/manage_optimal_course.html', title='Courses',
                search_form=search_form,lista_courses=course_ids)

        remove_course = Course.query.filter_by(id=hashids_hasher.decode(id_hash)).first()
        try:
            correct = True
            db.session.delete(remove_course)
            db.session.commit()
        except Exception as e:
            # Catch anything unknown
            print(e)
            correct = False
        finally:
            if not correct:
                # Cleanup and show error
                db.session.rollback()
                flash('Error when deleting Optimal Course','error')
            else:
                flash("An optimal course was erased.","success")
                return redirect(url_for('manage.manage_optimal_course'))

    return render_template('lo/manage_optimal_course.html', title='Courses',
        search_form=search_form,lista_courses=course_ids)


@bp_lo.route('/manage_learning_object', methods=['GET','POST'])
@login_required
@roles_required('Admin')
def manage_learning_object():
    page = request.args.get('page', 1, type=int)
    los_ids = LearningObject.query.order_by(LearningObject.id.asc()).paginate(
        page, current_app.config['PAGE_ITEMS'], False)

    search_form = SearchForm(request.form)

    if not los_ids.items:
        return render_template('lo/manage_learning_object.html',search_form=search_form,
                                 title='LOs')
    # LearningObject.reindex()
    # current_app.elasticsearch.indices.delete('los')

    if search_form.validate_on_submit():
        page = request.args.get('page', 1, type=int)
        los, total = LearningObject.search(request.form['q'], page,current_app.config['PAGE_ITEMS'])

        #Pues habria que hacer una paginacion manual conforme a los resultados de elastisearch
        next_url = url_for('lo.manage_learning_object', q=request.form['q'], page=page+1) \
            if total > page * current_app.config['PAGE_ITEMS'] else None
        prev_url = url_for('lo.manage_learning_object', q=request.form['q'], page=page-1) \
            if page > 1 else None

        return render_template('lo/manage_learning_object.html', title=_('LOs'),
            search_form=search_form,los=los,next_url=next_url, prev_url=prev_url)

    if not request.args.get('delete'):
        return render_template('lo/manage_learning_object.html', title='LOs',
            search_form=search_form,lista_lo=los_ids)
    else:#Remove an ability
        id_hash = request.args.get('id')
        if not id_hash or id_hash=='':
            flash("There is no ID.","error")
            return render_template('lo/manage_learning_object.html', title='LOs',
                search_form=search_form,lista_lo=los_ids)

        remove_lo = LearningObject.query.filter_by(id=hashids_hasher.decode(id_hash)).first()

        try:
            correct = True
            db.session.delete(remove_lo)
            db.session.commit()
        except Exception as e:
            # Catch anything unknown
            print(e)
            correct = False
        finally:
            if not correct:
                # Cleanup and show error
                db.session.rollback()
                flash('Error when deleting a learning object.','error')
            else:
                flash("A learning object was deleted.","success")
                return redirect(url_for('lo.manage_learning_object'))

    return render_template('lo/manage_learning_object.html', title='LOs',
        search_form=search_form,lista_lo=los_ids)



@bp_lo.before_app_request
def before_request():
    #Almacenamos de forma global el form de filtros
    g.filter_form = SearchFilterForm(request.args)



@bp_lo.route('/show_lo_optimal',methods=['GET'])
@login_required
@roles_required(['User','Admin'])
def show_lo_optimal():
    page = request.args.get('page', 1, type=int)
    #ORDENADO  LOS CUROS SEGUN UN FITNESS DEL CONJUNTO DE LOS OTROS FINTESS
    courses_pages = current_user.course.order_by(Course.fitness_total.asc()).paginate(page, 100, False)

    if 'TimeoutMS' in session:
        flash('Failure of the java microservice.','error')
        return render_template('lo/show_optimal_course.html', conectionFailed=True, title='Optimal LOS')

    if not courses_pages.items:
        flash('There are not Courses','error')
        return render_template('lo/show_optimal_course.html', notCourses=True, title='Optimal LOS')

    search_form = SearchForm()

    # Course.reindex()
    # current_app.elasticsearch.indices.delete('courses')


    return render_template('lo/show_optimal_course.html', title='Optimal LOS',
                     search_form=search_form,list_courses= courses_pages)


@bp_lo.route('/search')
@login_required
@roles_required(['User','Admin'])
def search():

    page = request.args.get('page', 1, type=int)

    search_form = SearchForm()

    time_filter = request.args.get('time')
    cost_filter = request.args.get('cost')
    reput_filter = request.args.get('reput')


    #Si hacemos un filtrado entraremos por aqui
    if time_filter or cost_filter or reput_filter:

        if time_filter and cost_filter and reput_filter:

            value_min_time= request.args.get('time_min')
            value_max_time= request.args.get('time_max')

            value_min_cost= request.args.get('cost_min')
            value_max_cost= request.args.get('cost_max')

            value_min_reput= request.args.get('reput_min')
            value_max_reput= request.args.get('reput_max')

            courses_filters = (
                    Course.query
                    .filter(
                        and_(
                            Course.total_time.between(value_min_time,value_max_time),
                            Course.total_cost.between(value_min_cost,value_max_cost),
                            Course.average_reputation.between(value_min_reput,value_max_reput)
                        )
                    )
                ).paginate(page, 20, False)

            total=courses_filters.total

                #Pues habria que hacer una paginacion manual conforme a los resultados de elastisearch
            next_url = url_for('lo.search',time=time_filter,cost=cost_filter,reput=reput_filter,
                time_min=value_min_time, time_max=value_max_time,cost_min=value_min_cost,
                cost_max=value_max_cost,reput_min=value_min_reput,reput_max=value_max_reput,
                 page=page+1) \
                if total > page * current_app.config['PAGE_ITEMS'] else None

            prev_url = url_for('lo.search',time=time_filter,cost=cost_filter,reput=reput_filter,
                time_min=value_min_time, time_max=value_max_time,cost_min=value_min_cost,
                cost_max=value_max_cost,reput_min=value_min_reput,reput_max=value_max_reput,
                 page=page-1) \
                if page > 1 else None

        elif time_filter and cost_filter:
            value_min_time= request.args.get('time_min')
            value_max_time= request.args.get('time_max')

            value_min_cost= request.args.get('cost_min')
            value_max_cost= request.args.get('cost_max')


            courses_filters = (
                    Course.query
                    .filter(
                        and_(
                            Course.total_time.between(value_min_time,value_max_time),
                            Course.total_cost.between(value_min_cost,value_max_cost)
                        )
                    )
                ).paginate(page, 20, False)

            total=courses_filters.total
                #Se hace una paginacion manual conforme a los resultados de elastisearch
            next_url = url_for('lo.search',time=time_filter,cost=cost_filter,
                time_min=value_min_time, time_max=value_max_time,cost_min=value_min_cost,
                cost_max=value_max_cost,page=page+1) \
                if total > page * current_app.config['PAGE_ITEMS'] else None

            prev_url = url_for('lo.search',time=time_filter,cost=cost_filter,
                time_min=value_min_time, time_max=value_max_time,cost_min=value_min_cost,
                cost_max=value_max_cost,page=page-1) \
                if page > 1 else None

        elif time_filter and reput_filter:
            value_min_time= request.args.get('time_min')
            value_max_time= request.args.get('time_max')

            value_min_reput= request.args.get('reput_min')
            value_max_reput= request.args.get('reput_max')


            courses_filters = (
                    Course.query
                    .filter(
                        and_(
                            Course.total_time.between(value_min_time,value_max_time),
                            Course.average_reputation.between(value_min_reput,value_max_reput)
                        )
                    )
                ).paginate(page, 20, False)

            total=courses_filters.total

            #Se hace una paginacion manual conforme a los resultados de elastisearch
            next_url = url_for('lo.search',time=time_filter,reput=reput_filter,
                time_min=value_min_time, time_max=value_max_time,reput_min=value_min_reput,
                reput_max=value_max_reput,page=page+1) \
                if total > page * current_app.config['PAGE_ITEMS'] else None

            prev_url = url_for('lo.search',time=time_filter,reput=reput_filter,
                time_min=value_min_time, time_max=value_max_time,reput_min=value_min_reput,
                reput_max=value_max_reput,page=page-1) \
                if page > 1 else None

        elif cost_filter and reput_filter:

            value_min_cost= request.args.get('cost_min')
            value_max_cost= request.args.get('cost_max')

            value_min_reput= request.args.get('reput_min')
            value_max_reput= request.args.get('reput_max')

            courses_filters = (
                    Course.query
                    .filter(
                        and_(
                            Course.total_cost.between(value_min_cost,value_max_cost),
                            Course.average_reputation.between(value_min_reput,value_max_reput)
                        )
                    )
                ).paginate(page, 20, False)

            total=courses_filters.total

            next_url = url_for('lo.search',cost=cost_filter,reput=reput_filter,
                cost_min=value_min_cost,cost_max=value_max_cost,reput_min=value_min_reput,
                reput_max=value_max_reput,page=page+1) \
                if total > page * current_app.config['PAGE_ITEMS'] else None

            prev_url = url_for('lo.search',cost=cost_filter,reput=reput_filter,
                cost_min=value_min_cost,cost_max=value_max_cost,reput_min=value_min_reput,
                reput_max=value_max_reput,page=page-1) \
                if page > 1 else None


        elif time_filter:
            value_min_time= request.args.get('time_min')
            value_max_time= request.args.get('time_max')

            courses_filters = (
                    Course.query
                    .filter(Course.total_time.between(value_min_time,value_max_time))
                    ).paginate(page, 20, False)

            total=courses_filters.total

            next_url = url_for('lo.search',time=time_filter,time_min=value_min_time,
                time_max=value_max_time, page=page+1) \
                if total > page * current_app.config['PAGE_ITEMS'] else None

            prev_url = url_for('lo.search',time=time_filter,time_min=value_min_time,
                time_max=value_max_time, page=page-1) \
                if page > 1 else None

        elif cost_filter:

            value_min_cost= request.args.get('cost_min')
            value_max_cost= request.args.get('cost_max')

            courses_filters = (
                    Course.query
                    .filter(Course.total_cost.between(value_min_cost,value_max_cost))
                ).paginate(page, 20, False)

            total=courses_filters.total

            next_url = url_for('lo.search',cost=cost_filter,cost_min=value_min_cost,
                cost_max=value_max_cost, page=page+1) \
                if total > page * current_app.config['PAGE_ITEMS'] else None

            prev_url = url_for('lo.search',cost=cost_filter,cost_min=value_min_cost,
                cost_max=value_max_cost, page=page-1) \
                if page > 1 else None


        elif reput_filter:

            value_min_reput= request.args.get('reput_min')
            value_max_reput= request.args.get('reput_max')

            courses_filters = (
                    Course.query
                    .filter(Course.average_reputation.between(value_min_reput,value_max_reput))
                ).paginate(page, 20, False)

            total=courses_filters.total

            next_url = url_for('lo.search',reput=reput_filter,reput_min=value_min_reput,
                reput_max=value_max_reput, page=page+1) \
                if total > page * current_app.config['PAGE_ITEMS'] else None

            prev_url = url_for('lo.search',reput=reput_filter,reput_min=value_min_reput,
                reput_max=value_max_reput, page=page-1) \
                if page > 1 else None


        if total>0: 
            return render_template('lo/show_optimal_course.html', next_url=next_url,prev_url=prev_url,
                title='Optimal LOS',search_form=search_form,search = courses_filters)
        else:
            #Comprobacion de errores
            flash('There are no courses for these selected ranges.','warn')
            return redirect(url_for('lo.show_lo_optimal'))



    #HACEMOS UN BUSQUEDA FULL-TEXT-SEARCH CON ELASTICSEARCH

    if request.args.get('q'):
        courses, total = Course.search(request.args.get('q'), page,current_app.config['PAGE_ITEMS'])
    else:
        flash('Please enter any filters.','warn')
        return redirect(url_for('lo.show_lo_optimal'))
    #estos cursos con elastisearch no tiene paginate , comprobacion en el html con jinja

    next_url = url_for('lo.search',q=request.args.get('q'), page=page+1) \
        if total > page * current_app.config['PAGE_ITEMS'] else None
    prev_url = url_for('lo.search', q=request.args.get('q'), page=page-1) \
        if page > 1 else None


    if not courses.all():
        flash('There are no courses by that name.','warn')
        return render_template('lo/show_optimal_course.html', title=_('Courses Search'),
                search_form=search_form,next_url=next_url, prev_url=prev_url, not_courses_elastic=True)


    return render_template('lo/show_optimal_course.html', title=_('Courses Search'),
        search_form=search_form,search=courses,next_url=next_url, prev_url=prev_url)

@bp_lo.route('/show_progress_optimal')
@login_required
@roles_required(['User','Admin'])
def show_progress_optimal():

    if 'task_id' in session:
        return render_template('lo/progress_optimal_course.html', title='Optimal LOS - Progress',
            task_id=session['task_id'])
    else:
        #No hay ningun Taskkk.....
        return render_template('lo/progress_optimal_course.html', title='Optimal LOS - Progress')



@celery.task(bind=True)
def long_task_los(self):

    try:
        correct = True
        var = requests.get("http://localhost:11025/createRandomLO").json()
    except Exception as e:
        correct = False
        print(e)
        print("Fallo en la conexion con el microservicio restful")
    finally:
        if not correct:
            print("No hay conexion con el microservicio!")
            return {'current': 100, 'total': 100, 'status': 'FAILURE','result': -1}

        # Eliminamos nuesta tabla para luego rellenarla
        # some_col IS NULL OR some_col = ''
        sql = '''DELETE FROM los WHERE course_id IS NULL'''
        db.engine.execute(sql)


        # En estas listas estaran los IDS descritivos de los KSAT
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

        cantidad_labels = 7
        target_labels_ids = []

        tam_Know = len(knowledges_list)
        tam_Skill = len(skills_list)
        tam_Abily = len(abilities_list)

        #Primero conseguimos los labels randoms
        l=0
        count=0
            # Decidimos que cada level de KSAT va ser asignado un id (
            # K001,S001,A001, T0001) de forma aleatoria

        while count < cantidad_labels:
            if (l % 3) == 0:
                l = 0

            if l == 0:
                numrndK = random.randrange(tam_Know)
                target_labels_ids.append(knowledges_list[numrndK])
            if l== 1:
                numrndS = random.randrange(tam_Skill)
                target_labels_ids.append(skills_list[numrndS])
            if l==2:
                numrndA = random.randrange(tam_Abily)
                target_labels_ids.append(abilities_list[numrndA])

            l+=1
            count+=1

        # ya tengo cada LO
        idd = 0
        for i in var['losSuccess']:
            # Cada i es un diccionario  de LO!!
            # print(i)
            idd += 1
            # PARA LA SEGUNDA VUELTA SE REPITEN LOS ID NUMERICOS !

            # Creamos un LO
            new_lo = LearningObject(
                time=i['time'],
                cost=i['cost'],
                reputation=i['reputation']
            )

            list_preq = i['prerequisites'].split(" ")
            # En este dict ira {"K001":"level"....}
            kreq_id_level = {}
            sreq_id_level = {}
            areq_id_level = {}

            # Creamos la lista de outcomes
            list_out = i['outcomes'].split(" ")
            # En este dict ira {"K001":"level"....}
            kout_id_level = {}
            sout_id_level = {}
            aout_id_level = {}


            count = 0
            for x in range(2, len(list_preq), 3):

                #Verificamos los labels
                if target_labels_ids[count] in knowledges_list:
                    index = knowledges_list.index(target_labels_ids[count])
                    kreq_id_level[target_labels_ids[count]] = {
                        "id_number": knowledges_ids[index].id,
                        "level": int(list_preq[x]),
                        "description": knowledges_ids[index].description
                    }

                    kout_id_level[target_labels_ids[count]] = {
                        "id_number": knowledges_ids[index].id,
                        "level": int(list_out[x]),
                        "description": knowledges_ids[index].description
                    }

                if target_labels_ids[count] in skills_list:
                    index = skills_list.index(target_labels_ids[count])
                    sreq_id_level[target_labels_ids[count]] = {
                        "id_number": skills_ids[index].id,
                        "level": int(list_preq[x]),
                        "description": skills_ids[index].description
                    }

                    sout_id_level[target_labels_ids[count]] = {
                        "id_number": skills_ids[index].id,
                        "level": int(list_out[x]),
                        "description": skills_ids[index].description
                    }


                if target_labels_ids[count] in abilities_list:
                    index = abilities_list.index(target_labels_ids[count])
                    areq_id_level[target_labels_ids[count]] = {
                        "id_number": abilities_ids[index].id,
                        "level": int(list_preq[x]),
                        "description": abilities_ids[index].description
                    }

                    aout_id_level[target_labels_ids[count]] = {
                        "id_number": abilities_ids[index].id,
                        "level": int(list_out[x]),
                        "description": abilities_ids[index].description
                    }

                #Counter of list label targetKSA
                count += 1

            # Creamos un KSAT para requisitos del LO
            new_ksat_req = Ksat(
                name=f'{"Random_"}{"_requirements_"}{idd}',
                date=datetime.datetime.utcnow(),
                ksat_ids={
                    "knowledges_ids": kreq_id_level,
                    "skills_ids":     sreq_id_level,
                    "abilities_ids":  areq_id_level
                }
            )

            # Creamos un KSAT para los outcomes de un LO
            new_ksat_out = Ksat(
                name=f'{"Random_"}{"_outcomes_"}{idd}',
                date=datetime.datetime.utcnow(),
                ksat_ids={
                    "knowledges_ids": kout_id_level,
                    "skills_ids":     sout_id_level,
                    "abilities_ids":  aout_id_level
                }
            )


            new_lo.ksats.extend([new_ksat_req,new_ksat_out])
            #Se almacena el nuevo LO y los KSA req and out
            db.session.add_all([new_lo, new_ksat_req, new_ksat_out])

        try:
            correct = True
            db.session.commit()
        except Exception as e:
            # capturamos el error
            print(e)
            correct = False
        finally:
            if not correct:
                # limpiamos y mostramos el error
                db.session.rollback()
                print('Error creating KSAT atribute')
                return {'current': 100, 'total': 100, 'status': 'FAILURE','result': -1}
            else:
                print("Se crearon todos los Learning objects con requisitos and outcomes")
                return {'current': 100, 'total': 100, 'status': 'Task completed!','result': 200}

        return {'current': 100, 'total': 100, 'status': 'Task completed!','result': 200}




@bp_lo.route('/create_rnd_lo', methods=['GET'])
@login_required
@roles_required(['Admin'])
def create_rnd_lo():
    try:
        task = long_task_los.delay()
        correct=True
    except Exception as e:
        print(e)
        correct=False
    finally:
        if not correct:
            flash('Error in the connection with the broker-celery.','error')
            return render_template('manage/dashboard_admin.html', title='Dashboard Admin')
        else:
            flash('The Learnin Object Random is being created!','success')
            return render_template('manage/dashboard_admin.html', title='Dashboard Admin')

    return render_template('manage/dashboard_admin.html', title='Dashboard Admin')


@bp_lo.route('/show_lo_general')
@login_required
@roles_required(['User','Admin'])
def show_lo_general():

    page = request.args.get('page', 1, type=int)
    los = LearningObject.query.order_by(LearningObject.id.asc()).paginate(
        page, 100, False)

    if not los.items:
        return render_template('lo/show_lo.html', title='Learning Objects')
    return render_template('lo/show_lo.html', title='Learning Objects', los=los)


@bp_lo.route('/do_course')
@login_required
@roles_required(['User','Admin'])
def do_course():

    course_id = request.args.get('id')

    if not course_id or course_id=='':
        flash('There is no ID.','error')
        return redirect(url_for('lo.show_lo_optimal'))

    course = Course.query.filter_by(id=hashids_hasher.decode(course_id)).first()
    if not course:
        flash('There is no course!','error')
        return redirect(url_for('lo.show_lo_optimal'))

    if "finished_courses" in current_user.ksat.ksat_ids:
        if course.id in current_user.ksat.ksat_ids["finished_courses"]:
            flash('You have already taken this course!','warn')
            return redirect(url_for('lo.show_lo_optimal'))

    # En estas listas estaran los IDS descritivos de los KSAT
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



    #Formatearemos los ksas_user, adquiriendo nuevos ksas, niveles mayores
    for i in course.los:
        #Outcomes del Learning Object
        ksat_lo = i.ksats[1]

        knowledges_lo = ksat_lo.ksat_ids['knowledges_ids']
        skills_lo = ksat_lo.ksat_ids['skills_ids']
        abilities_lo = ksat_lo.ksat_ids['abilities_ids']

        for x in knowledges_lo:
            #Reemplazaremos un ksa solo en el caso de que haya un nivel supeior en los
            #outcomes
            if x in ksas_user:
                if knowledges_lo[x]["level"] > ksas_user[x]:
                    ksas_user[x] = knowledges_lo[x]["level"]

            #Agregaremos solo en caso de que se mayor que 0, porque si es igual,
            # no interesa.
            elif knowledges_lo[x]["level"] > 0:
                ksas_user[x] = knowledges_lo[x]["level"]

        for x in skills_lo:
            if x in ksas_user:
                if skills_lo[x]["level"] > ksas_user[x]:
                    ksas_user[x] = skills_lo[x]["level"]
            elif skills_lo[x]["level"] > 0:
                ksas_user[x] = skills_lo[x]["level"]
        for x in abilities_lo:
            if x in ksas_user:
                if abilities_lo[x]["level"] > ksas_user[x]:
                    ksas_user[x] = abilities_lo[x]["level"]
            elif abilities_lo[x]["level"] > 0:
                ksas_user[x] = abilities_lo[x]["level"]

    #Ya tenemos el nuevo KSA del usuario

    # Y creamos un ksa viejo con los datos del antiguo ksa del usuario
    if current_user.ksat:
        new_ksat_out = Ksat(
                # Este name lo usaremos para obtener los antiguos ksa de un user
                # gracias al id del curso se mando este ksa como viejo
                # tambien gracias  a la fecha podremos filtrarlo fenomenalmente !
                name=f'{current_user.username}{"_old_ksa_"}{course.id}',
                date=current_user.ksat.date,
                ksat_ids={
                    "knowledges_ids": knowledges_user,
                    "skills_ids":     skills_user,
                    "abilities_ids":  abilities_user,
                    "tasks_ids":      current_user.ksat.ksat_ids["tasks_ids"]
                }
        )

    #Variables para la modificacion
    k_id_level = {}
    s_id_level = {}
    a_id_level = {}
    #Actualizacion de los ksas del usuario
    for i in ksas_user:
        if i in knowledges_list:
            index = knowledges_list.index(i)

            k_id_level[i] = {
                "id_number": knowledges_ids[index].id,
                "level": int(ksas_user[i]),
                "description": knowledges_ids[index].description
            }
        if i in skills_list:
            index = skills_list.index(i)

            s_id_level[i] = {
                "id_number": skills_ids[index].id,
                "level": int(ksas_user[i]),
                "description": skills_ids[index].description
            }
        if i in abilities_list:
            index = abilities_list.index(i)

            a_id_level[i] = {
                "id_number": abilities_ids[index].id,
                "level": int(ksas_user[i]),
                "description": abilities_ids[index].description
            }



    if "finished_courses" in current_user.ksat.ksat_ids:
        list_finished_courses = current_user.ksat.ksat_ids["finished_courses"].copy()
        list_finished_courses.append(course.id)
    else:
        list_finished_courses = [course.id]

    #Modificamos el ksat del usuario actual
    current_user.ksat.date = datetime.datetime.utcnow(),
    current_user.ksat.ksat_ids = {
        "knowledges_ids": k_id_level,
        "skills_ids":     s_id_level,
        "abilities_ids":  a_id_level,
        "tasks_ids":      current_user.ksat.ksat_ids["tasks_ids"],
        #Agregamos info extra, del curso que se ha hecho
        "finished_courses": list_finished_courses
    }


    try:
        correct = True
        #añadimos el ksa old
        db.session.add(new_ksat_out)
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
            flash('Congratulations, you have acquired new KSAs!','success')
            # print(current_user.ksat.ksat_ids["finished_courses"])

    return render_template('lo/do_course.html', title=course.name,course=course)


@bp_lo.route('/evolution')
@login_required
@roles_required(['User','Admin'])
def show_evolution():


    if not current_user.ksat:
        flash('You do not have KSAs so you can see your evolution.','warn')
        return redirect(url_for('general.show_dash'))
    #Cargar el KSAT actual del usuario
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

    #YA ESTARIAN ORDENADOS EN FECHAS XQ SIEMPRE AÑADIMOS EL ULTIMO CURSO
    # HECHO, ES DECIR CON APPEND SIEMPRE ESCRIBIMOS EL ULTIMO CURSO

    dates= []
    ksat_old_dict={}
    matrix = []
    #Añadimos los IDs - simbolicos
    #PRIMERO METEMOS LOS IDS
    matrix.append(list(ksas_user.keys()))

#EJEMPLOS DE POSIBLES KJSA
#     ++++++++++++Ksas actual++++++++++++
# {'myK0001': 5, 'myK0002': 4, 'myS0001': 2, 'myS0002': 2, 'myS0011': 5, 'myS0012': 5, 'myA0001': 2, 'myA0002': 5}
# ++++++++++++Ksas actual++++++++++++
# --------------Ksat old---------
# {'myK0001': 5, 'myK0002': 4, 'myS0001': 2, 'myS0002': 2, 'myA0001': 2, 'myA0002': 5, 'myS0011': 5, 'myS0012': 5}
# --------------Ksat old---------


    if "finished_courses" in current_user.ksat.ksat_ids:
        for i in current_user.ksat.ksat_ids["finished_courses"]:
            name_ksat_old = f'{current_user.username}{"_old_ksa_"}{i}'
            ksat_old = Ksat.query.filter_by(name=name_ksat_old).first()
            #Metemos los dates old primero, ya estan ordenadas porque segun se hace se meten
            dates.append(str(ksat_old.date.strftime("%d/%m/%Y, %H:%M:%S")))

            if ksat_old:
                knowledges_old = ksat_old.ksat_ids['knowledges_ids']
                skills_old = ksat_old.ksat_ids['skills_ids']
                abilities_old = ksat_old.ksat_ids['abilities_ids']

                #ordenamos segun el ksa actual - current
                for x in knowledges_user:
                    if x in knowledges_old:
                        ksat_old_dict[x]=knowledges_old[x]["level"]
                    else:

                        ksat_old_dict[x]=0

                for x in skills_user:
                    if x in skills_old:
                        ksat_old_dict[x] = skills_old[x]["level"]
                    else:
                        ksat_old_dict[x]=0

                for x in abilities_user:
                    if x in abilities_old:
                        ksat_old_dict[x]= abilities_old[x]["level"]
                    else:
                        ksat_old_dict[x]=0

            matrix.append(list(ksat_old_dict.values()))


    # y la añadimos el ultimo ksa, que es el ACTUAL DEL USUARIO!
    matrix.append(list(ksas_user.values()))
    dates.append(str(current_user.ksat.date.strftime("%d/%m/%Y, %H:%M:%S")))


    #TRANSPONEMOS LOS ARRYAS
    rez = [[matrix[j][i] for j in range(len(matrix))] for i in range(len(matrix[0]))] 

    dict_matrix = {0:rez}

    return render_template('lo/evolution.html', title='Evolution KSA', data=dict_matrix,dates=dates)