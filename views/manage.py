# -*- coding: utf-8 -*-
"""This file contains manage views."""

import datetime
import requests
import json
from flask import Blueprint, jsonify, session, render_template, flash, redirect, url_for, request,\
 current_app
from flask_babel import _

from flask_user import login_required, roles_required
from flask_login import current_user, login_user

from cyber_role import db, user_manager,hashids_hasher
from cyber_role.models import User, Ksat, Category, Specialist, WorkRole, Knowledge, Skill, Ability, Task
from cyber_role.forms import RegistrationForm, TestForm, KsaForm, TargetForm, TargetKsaForm,SearchForm,\
 DescriptionKsaForm,CategoryForm,SpecialistForm,WorkRoleForm

bp_manage = Blueprint('manage', __name__)

#Area Admin tablas Knowledges , Skills , Abilties, Tasks, Work roles, Categories, Specialist, LOS, Courses

@bp_manage.route('/manage_knowledge', methods=['GET','POST'])
@login_required
@roles_required('Admin')
def manage_knowledge():

    """ Metodo exclusivo del administrador que sirve para gestionar la tabla de Knowledges."""

    # session.clear()
    page = request.args.get('page', 1, type=int)
    knowledges_ids = Knowledge.query.order_by(Knowledge.id.asc()).paginate(
        page, current_app.config['PAGE_ITEMS'], False)

    if not knowledges_ids.items:
        return render_template('manage/manage_knowledge.html', title='Knowledges')

    search_form = SearchForm(request.form)

    # Cuando borramoms la db, la tabla y cuando esten los datos hay que hacer esto
    # Sirve para la creacion de indices de Elasticsearch

    # Knowledge.reindex()
    # current_app.elasticsearch.indices.delete('knowledges')

    if request.args.get('q'):
        q = request.args.get('q')
        page = request.args.get('page', 1, type=int)
        knowledges, total = Knowledge.search(q, page,current_app.config['PAGE_ITEMS'])

        #Pues habria que hacer una paginacion manual conforme a los resultados de elastisearch
        next_url = url_for('manage.manage_knowledge', q=q, page=page+1) \
            if total > page * current_app.config['PAGE_ITEMS'] else None
        prev_url = url_for('manage.manage_knowledge', q=q, page=page-1) \
            if page > 1 else None

        return render_template('manage/manage_knowledge.html', title=_('Knowledges'),
            search_form=search_form,search_knows =knowledges,next_url=next_url, prev_url=prev_url)

    if not request.args.get('delete'):
        return render_template('manage/manage_knowledge.html', title='Knowledges',
            search_form=search_form,lista_K=knowledges_ids)
    else: #Remove knows
        id_hash = request.args.get('id')
        if not id_hash or id_hash=='':
            flash("No null or empty values are allowed.","error")
            return render_template('manage/manage_knowledge.html', title='Knowledges',
                search_form=search_form,lista_K=knowledges_ids)

        remove_k = Knowledge.query.filter_by(id=hashids_hasher.decode(id_hash)).first()

        try:
            correct = True
            db.session.delete(remove_k)
            db.session.commit()
        except Exception as e:
            # Catch anything unknown
            print(e)
            correct = False
        finally:
            if not correct:
                # Cleanup and show error
                db.session.rollback()
                flash('Error when deleting a Knowledge.','error')
            else:
                flash("A Knowlegede was deleted!",'success')
                return redirect(url_for('manage.manage_knowledge'))

    return render_template('manage/manage_knowledge.html', title='Knowledges',
                            search_form=search_form,lista_K=knowledges_ids)

@bp_manage.route('/add_knowledge', methods=['GET','POST'])
@login_required
@roles_required('Admin')
def add_knowledge():

    """ Metodo exclusivo del administrador que sirve para anadir un nuevo knowledge."""

    know_form = DescriptionKsaForm(request.form)

    if know_form.validate_on_submit():

        description = request.form['description']

        if not description or description == '' :
            flash("No null or empty values are allowed.","warn")
            return render_template('manage/add_edit_ksat.html', prev_url='manage.manage_knowledge', 
                title='Add Knowledges',add=True,form=know_form)
        else:
            new_k = Knowledge(
                    description=request.form['description']
                )
            try:
                correct = True
                db.session.add(new_k)
                db.session.commit()
            except Exception as e:
                # Catch anything unknown
                print(e)
                correct = False
            finally:
                if not correct:
                    # Cleanup and show error
                    db.session.rollback()
                    flash('Error when creating a Knowledge','error')
                else:
                    flash("Our knowledge was created.","success")
                    return redirect(url_for('manage.manage_knowledge'))

    return render_template('manage/add_edit_ksat.html', prev_url='manage.manage_knowledge' ,
        title='Add Knowledges',add=True,form=know_form)


@bp_manage.route('/modify_knowledge', methods=['GET','POST'])
@login_required
@roles_required('Admin')
def modify_knowledge():

    """ Metodo exclusivo del administrador que sirve para modificar un knowledge."""

    id_hash = request.args.get('id')

    if not id_hash or id_hash=='':
        flash("There is no ID.","error")
        return redirect(url_for('manage.manage_knowledge'))

    #Localizamos el knowledges y luego lo modificamos
    modify_k = Knowledge.query.filter_by(id=hashids_hasher.decode(id_hash)).first()

    if not modify_k:
        flash("There is no such knowledge.","error")
        return redirect(url_for('manage.manage_knowledge'))

    know_form = DescriptionKsaForm(description=modify_k.description)

    if know_form.validate_on_submit():

        new_description = request.form['description']

        if not new_description or new_description == '' :
            flash("No null or empty values are allowed.","warn")
            return render_template('manage/add_edit_ksat.html', prev_url='manage.manage_knowledge',
                title='Modify Knowledges',form=know_form)
        else:
            modify_k.description = new_description
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
                    flash('Error when modifying a Knowledge','error')
                else:
                    flash("Knowledge was modified!","success")
                    return redirect(url_for('manage.manage_knowledge'))

    return render_template('manage/add_edit_ksat.html',
        prev_url='manage.manage_knowledge', title='Modify Knowledges',form=know_form)


@bp_manage.route('/manage_skill', methods=['GET','POST'])
@login_required
@roles_required('Admin')
def manage_skill():

    """ Metodo exclusivo del administrador que sirve para gestionar la tabla de skill."""

    page = request.args.get('page', 1, type=int)
    skills_ids = Skill.query.order_by(Skill.id.asc()).paginate(
        page, current_app.config['PAGE_ITEMS'], False)

    if not skills_ids.items:
        flash('No existen skills','error')
        return render_template('manage/manage_skill.html', title='Skills')

    search_form = SearchForm(request.form)

    # Skill.reindex()
    # current_app.elasticsearch.indices.delete('skills')

    if request.args.get('q'):
        q = request.args.get('q')
        page = request.args.get('page', 1, type=int)
        skills, total = Skill.search(q, page,current_app.config['PAGE_ITEMS'])

        #Pues habria que hacer una paginacion manual conforme a los resultados de elastisearch
        next_url = url_for('manage.manage_skill', q=q, page=page+1) \
            if total > page * current_app.config['PAGE_ITEMS'] else None
        prev_url = url_for('manage.manage_skill', q=q, page=page-1) \
            if page > 1 else None

        return render_template('manage/manage_skill.html', title=_('Skills'),
                search_form=search_form,search_skills=skills,next_url=next_url, 
                prev_url=prev_url)

    if not request.args.get('delete'):
        return render_template('manage/manage_skill.html', title='Skills',search_form=search_form,
            lista_S=skills_ids)
    else:#Remove knows
        id_hash = request.args.get('id')

        if not id_hash or id_hash=='':
            flash("There is no ID.","error")
            return render_template('manage/manage_skill.html', title='Skills',search_form=search_form,
                lista_S=skills_ids)

        remove_s = Skill.query.filter_by(id=hashids_hasher.decode(id_hash)).first()

        try:
            correct = True
            db.session.delete(remove_s)
            db.session.commit()
        except Exception as e:
            # Catch anything unknown
            print(e)
            correct = False
        finally:
            if not correct:
                # Cleanup and show error
                db.session.rollback()
                flash('Error when deleting a Skill','error')
            else:
                flash("A Skill was deleted!","success")
                return redirect(url_for('manage.manage_skill'))

    return render_template('manage/manage_skill.html', title='Skills',search_form=search_form,
        lista_S=skills_ids)

@bp_manage.route('/add_skill', methods=['GET','POST'])
@login_required
@roles_required('Admin')
def add_skill():

    """ Metodo exclusivo del administrador que sirve para anadir un nuevo skill."""

    skill_form = DescriptionKsaForm(request.form)

    if skill_form.validate_on_submit():

        description = request.form['description']
        #Una cosa muy importante aunque en el form sea validado como required hay que validarlo en la parte del servidor
        #porque en la parte del cliente un ciberdelincuente se lo podria saltar
        if not description or description == '' :
            flash("No null or empty values are allowed.","warn")
            return render_template('manage/add_edit_ksat.html', title='Add Skills',
                prev_url='manage.manage_skill',add=True,form=skill_form)
        else:
            new_s = Skill(
                    description=request.form['description']
                )
            try:
                correct = True
                db.session.add(new_s)
                db.session.commit()
            except Exception as e:
                # Catch anything unknown
                print(e)
                correct = False
            finally:
                if not correct:
                    # Cleanup and show error
                    db.session.rollback()
                    flash('Error when creating a Skill','error')
                else:
                    flash("Our Skill was created!","success")
                    return redirect(url_for('manage.manage_skill'))

    return render_template('manage/add_edit_ksat.html', title='Add Skills',
        prev_url='manage.manage_skill',add=True,form=skill_form)

@bp_manage.route('/modify_skill', methods=['GET','POST'])
@login_required
@roles_required('Admin')
def modify_skill():

    """ Metodo exclusivo del administrador que sirve para modificar un skill."""

    id_hash = request.args.get('id')

    if not id_hash or id_hash =='':
        flash("There is no ID.","error")
        return redirect(url_for('manage.manage_skill'))

    #Localizamos el skill y luego lo modificamos
    modify_s = Skill.query.filter_by(id=hashids_hasher.decode(id_hash)).first()
    if not modify_s:
        flash("There is no Skill.","error")
        return redirect(url_for('manage.manage_skill'))

    skill_form = DescriptionKsaForm(description=modify_s.description)


    if skill_form.validate_on_submit():

        new_description = request.form['description']

        if not new_description or new_description == '' :
            flash("No null or empty values are allowed.","warn")
            return render_template('manage/add_edit_ksat.html', title='Modify Skills',
                                    prev_url='manage.manage_skill',form=skill_form)
        else:
            modify_s.description = new_description
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
                    flash('Error when modifying a Skill','error')
                else:
                    flash("Our skill was modified!","success")
                    return redirect(url_for('manage.manage_skill'))

    return render_template('manage/add_edit_ksat.html',
            prev_url='manage.manage_skill', title='Modify Skills',form=skill_form)


@bp_manage.route('/manage_ability', methods=['GET','POST'])
@login_required
@roles_required('Admin')
def manage_ability():

    """ Metodo exclusivo del administrador que sirve para gestionar la tabla de ability."""

    page = request.args.get('page', 1, type=int)
    abilities_ids = Ability.query.order_by(Ability.id.asc()).paginate(
        page, current_app.config['PAGE_ITEMS'], False)


    if not abilities_ids.items:
        flash('There are not Abilities!','error')
        return render_template('manage/manage_ability.html',title='Abilities')

    search_form = SearchForm(request.form)

    # Ability.reindex()
    # current_app.elasticsearch.indices.delete('abilities')

    if request.args.get('q'):
        q = request.args.get('q')
        page = request.args.get('page', 1, type=int)
        abilities, total = Ability.search(q, page,current_app.config['PAGE_ITEMS'])

        #Pues habria que hacer una paginacion manual conforme a los resultados de elastisearch
        next_url = url_for('manage.manage_ability', q=q, page=page+1) \
            if total > page * current_app.config['PAGE_ITEMS'] else None
        prev_url = url_for('manage.manage_ability', q=q, page=page-1) \
            if page > 1 else None

        return render_template('manage/manage_ability.html', title=_('Abilities'),
            search_form=search_form,search_abilities=abilities,next_url=next_url,
             prev_url=prev_url)

    if not request.args.get('delete'):
        return render_template('manage/manage_ability.html', title='Abilities',
            search_form=search_form,lista_A=abilities_ids)
    else:#Remove an ability
        id_hash = request.args.get('id')

        if not id_hash or id_hash=='':
            flash("There is no ID.","error")
            return render_template('manage/manage_ability.html', title='Abilities',
                search_form=search_form,lista_A=abilities_ids)

        remove_a = Ability.query.filter_by(id=hashids_hasher.decode(id_hash)).first()

        try:
            correct = True
            db.session.delete(remove_a)
            db.session.commit()
        except Exception as e:
            # Catch anything unknown
            print(e)
            correct = False
        finally:
            if not correct:
                # Cleanup and show error
                db.session.rollback()
                flash('Error when deleting an Abiltity','error')
            else:
                flash("Our Ability was deleted!","success")
                return redirect(url_for('manage.manage_ability'))

    return render_template('manage/manage_ability.html', title='Ability',
                            search_form=search_form,lista_A=abilities_ids)

@bp_manage.route('/add_ability', methods=['GET','POST'])
@login_required
@roles_required('Admin')
def add_ability():

    """ Metodo exclusivo del administrador que sirve para anadir un ability."""

    abil_form = DescriptionKsaForm(request.form)

    if abil_form.validate_on_submit():

        description = request.form['description']

        if not description or description == '' :
            flash("No null or empty values are allowed.","warn")
            return render_template('manage/add_edit_ksat.html', title='Add Abilities',
                prev_url='manage.manage_ability',add=True,form=abil_form)
        else:
            new_a = Ability(
                    description=description
                )
            try:
                correct = True
                db.session.add(new_a)
                db.session.commit()
            except Exception as e:
                # Catch anything unknown
                print(e)
                correct = False
            finally:
                if not correct:
                    # Cleanup and show error
                    db.session.rollback()
                    flash('Error when creating an Ability.','error')
                else:
                    flash("Our Ability was created!","success")
                    return redirect(url_for('manage.manage_ability'))

    return render_template('manage/add_edit_ksat.html', title='Add Abilitiess',
        prev_url='manage.manage_ability',add=True,form=abil_form)

@bp_manage.route('/modify_ability', methods=['GET','POST'])
@login_required
@roles_required('Admin')
def modify_ability():

    """ Metodo exclusivo del administrador que sirve para modificar un ability."""

    id_hash = request.args.get('id')

    if not id_hash or id_hash=='':
        flash("There is no ID.","error")
        return redirect(url_for('manage.manage_ability'))

    #Localizamos el knowledges y luego lo modificamos
    modify_a = Ability.query.filter_by(id=hashids_hasher.decode(id_hash)).first()

    if not modify_a:
        flash("There is no Ability","error")
        return redirect(url_for('manage.manage_ability'))

    abil_form = DescriptionKsaForm(description=modify_a.description)

    if abil_form.validate_on_submit():

        new_description = request.form['description']

        if not new_description or new_description == '' :
            flash("No null or empty values are allowed.","warn")
            return render_template('manage/add_edit_ksat.html',prev_url='manage.manage_ability',
             title='Modify Abilities',form=abil_form)
        else:

            modify_a.description = new_description
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
                    flash('Error when modifying an Ability','error')
                else:
                    flash("Our Ability was modified!","success")
                    return redirect(url_for('manage.manage_ability'))

    return render_template('manage/add_edit_ksat.html',prev_url='manage.manage_ability',
         title='Modify Abilities',form=abil_form)


@bp_manage.route('/manage_task', methods=['GET','POST'])
@login_required
@roles_required('Admin')
def manage_task():

    """ Metodo exclusivo del administrador que sirve para gestionar la tabla de tasks."""

    page = request.args.get('page', 1, type=int)
    tasks_ids = Task.query.order_by(Task.id.asc()).paginate(
        page, current_app.config['PAGE_ITEMS'], False)

    if not tasks_ids.items:
        return render_template('manage/manage_task.html', title='Tasks')

    search_form = SearchForm(request.form)

    # Task.reindex()
    # current_app.elasticsearch.indices.delete('tasks')

    if request.args.get('q'):
        q = request.args.get('q')
        page = request.args.get('page', 1, type=int)
        tasks, total = Task.search(q, page,current_app.config['PAGE_ITEMS'])

        #Pues habria que hacer una paginacion manual conforme a los resultados de elastisearch
        next_url = url_for('manage.manage_task', q=q, page=page+1) \
            if total > page * current_app.config['PAGE_ITEMS'] else None
        prev_url = url_for('manage.manage_task', q=q, page=page-1) \
            if page > 1 else None

        return render_template('manage/manage_task.html', title=_('Tasks'),
            search_form=search_form,search_tasks=tasks,next_url=next_url,
            prev_url=prev_url)

    if not request.args.get('delete'):
        return render_template('manage/manage_task.html', title='Tasks',search_form=search_form,
            lista_T=tasks_ids)
    else:#Remove knows
        id_hash = request.args.get('id')
        if not id_hash or id_hash=='':
            flash("There is no ID.","error")
            return render_template('manage/manage_task.html', title='Tasks',search_form=search_form,
                lista_T=tasks_ids)

        remove_t = Task.query.filter_by(id=hashids_hasher.decode(id_hash)).first()

        try:
            correct = True
            db.session.delete(remove_t)
            db.session.commit()
        except Exception as e:
            # Catch anything unknown
            print(e)
            correct = False
        finally:
            if not correct:
                # Cleanup and show error
                db.session.rollback()
                flash('Error when deleting a Task.','error')
            else:
                flash("Our Task was deleted!","success")
                return redirect(url_for('manage.manage_task'))

    return render_template('manage/manage_task.html', title='Tasks',search_form=search_form,
        lista_T=tasks_ids)

@bp_manage.route('/add_task', methods=['GET','POST'])
@login_required
@roles_required('Admin')
def add_task():

    """ Metodo exclusivo del administrador que sirve para anadir un nuevo task."""

    task_form = DescriptionKsaForm(request.form)

    if task_form.validate_on_submit():

        description = request.form['description']

        if not description or description == '' :
            flash("No null or empty values are allowed.","warn")
            return render_template('manage/add_edit_ksat.html', title='Add Tasks',
               prev_url='manage.manage_task', add=True,form=task_form)
        else:
            new_t = Task(
                    description=request.form['description']
                )
            try:
                correct = True
                db.session.add(new_t)
                db.session.commit()
            except Exception as e:
                # Catch anything unknown
                print(e)
                correct = False
            finally:
                if not correct:
                    # Cleanup and show error
                    db.session.rollback()
                    flash('Error when creating a Task','error')
                else:
                    flash("Our Task was created!","success")
                    return redirect(url_for('manage.manage_task'))

    return render_template('manage/add_edit_ksat.html', title='Add Tasks',
        prev_url='manage.manage_task',add=True,form=task_form)

@bp_manage.route('/modify_task', methods=['GET','POST'])
@login_required
@roles_required('Admin')
def modify_task():

    """ Metodo exclusivo del administrador que sirve para modificar un task."""

    id_hash = request.args.get('id')
    if not id_hash or id_hash=='':
        flash('There is no ID.','error')
        return redirect(url_for('manage.manage_task'))
    #Localizamos el task y luego lo modificamos
    modify_t = Task.query.filter_by(id=hashids_hasher.decode(id_hash)).first()

    if not modify_t:
        flash('There is no Task.','error')
        return redirect(url_for('manage.manage_task'))

    task_form = DescriptionKsaForm(description=modify_t.description)

    if task_form.validate_on_submit():

        new_description = request.form['description']

        if not new_description or new_description == '' :
            flash("No null or empty values are allowed.","warn")
            return render_template('manage/add_edit_ksat.html',prev_url='manage.manage_task', 
                title='Modify Tasks',form=task_form)
        else:
            modify_t.description = new_description
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
                    flash('Error when modifying a Task','error')
                else:
                    flash("Our Task was modified!","success")
                    return redirect(url_for('manage.modify_task'))

    return render_template('manage/add_edit_ksat.html',prev_url='manage.manage_task',
         title='Modify Tasks',form=task_form)


@bp_manage.route('/manage_ksat', methods=['GET','POST'])
@login_required
@roles_required('Admin')
def manage_ksat():

    """ Metodo exclusivo del administrador que sirve para gestionar la tabla de ksat."""

    page = request.args.get('page', 1, type=int)
    ksats_ids = Ksat.query.order_by(Ksat.id.asc()).paginate(
        page, current_app.config['PAGE_ITEMS'], False)

    search_form = SearchForm(request.form)
    if not ksats_ids.items:
        flash('There are no KSAT.','error')
        return render_template('manage/manage_ksat.html', search_form=search_form,title='Ksats')

    # Ksat.reindex()

    if request.args.get('q'):
        q = request.args.get('q')
        page = request.args.get('page', 1, type=int)
        ksats, total = Ksat.search(q, page,current_app.config['PAGE_ITEMS'])

        #Pues habria que hacer una paginacion manual conforme a los resultados de elastisearch
        next_url = url_for('manage.manage_ksat', q=q, page=page+1) \
            if total > page * current_app.config['PAGE_ITEMS'] else None
        prev_url = url_for('manage.manage_ksat', q=q, page=page-1) \
            if page > 1 else None

        return render_template('manage/manage_ksat.html', title=_('Ksats'),search_form=search_form,
         search_ksats=ksats,next_url=next_url, prev_url=prev_url)

    if not request.args.get('delete'):
        return render_template('manage/manage_ksat.html', title='Ksats',
            search_form=search_form,lista_ksat=ksats_ids)
    else:#Remove an ksat
        id_hash = request.args.get('id')
        if not id_hash or id_hash=='':
            flash('There is no ID.','error')
            return render_template('manage/manage_ksat.html', title='Ksats',search_form=search_form,
                lista_ksat=ksats_ids)

        remove_ksat = Ksat.query.filter_by(id=hashids_hasher.decode(id_hash)).first()

        try:
            correct = True
            db.session.delete(remove_ksat)
            db.session.commit()
        except Exception as e:
            # Catch anything unknown
            print(e)
            correct = False
        finally:
            if not correct:
                # Cleanup and show error
                db.session.rollback()
                flash('Error when deleting a KSAT','error')
            else:
                flash("Our KSAT was deleted!","success")
                return redirect(url_for('manage.manage_ksat'))

    return render_template('manage/manage_ksat.html', title='Ksats',search_form=search_form,
        lista_ksat=ksats_ids)



@bp_manage.route('/manage_category', methods=['GET','POST'])
@login_required
@roles_required('Admin')
def manage_category():

    """ Metodo exclusivo del administrador que sirve para gestionar la tabla de category."""

    page = request.args.get('page', 1, type=int)
    categories_ids = Category.query.order_by(Category.id.asc()).paginate(
        page, current_app.config['PAGE_ITEMS'], False)

    if not categories_ids.items:
        flash('There are no Categories','error')
        return render_template('manage/manage_category.html', title='Categories')

    search_form = SearchForm(request.form)

    # Category.reindex()
    # current_app.elasticsearch.indices.delete('categories')

    if request.args.get('q'):
        q = request.args.get('q')
        page = request.args.get('page', 1, type=int)
        categories, total = Category.search(q, page,current_app.config['PAGE_ITEMS'])

        #Pues habria que hacer una paginacion manual conforme a los resultados de elastisearch
        next_url = url_for('manage.manage_category', q=q, page=page+1) \
            if total > page * current_app.config['PAGE_ITEMS'] else None
        prev_url = url_for('manage.manage_category', q=q, page=page-1) \
            if page > 1 else None

        return render_template('manage/manage_category.html', title=_('Categories'),
            search_form=search_form,search_cat=categories,next_url=next_url, prev_url=prev_url)

    if not request.args.get('delete'):
        return render_template('manage/manage_category.html', title='Categories',
            search_form=search_form,lista_cat=categories_ids)
    else:#Remove an ability

        id_hash = request.args.get('id')

        if not id_hash or id_hash=='':
            flash('There is no ID.','error')
            return render_template('manage/manage_category.html', title='Categories',
                search_form=search_form,lista_cat=categories_ids)

        remove_cat = Category.query.filter_by(id=hashids_hasher.decode(id_hash)).first()

        try:
            correct = True
            db.session.delete(remove_cat)
            db.session.commit()
        except Exception as e:
            # Catch anything unknown
            print(e)
            correct = False
        finally:
            if not correct:
                # Cleanup and show error
                db.session.rollback()
                flash('Error when deleting a Category','error')
            else:
                flash("Our Category was deleted!","success")
                return redirect(url_for('manage.manage_category'))

    return render_template('manage/manage_category.html', title='Categories',
        search_form=search_form,lista_cat=categories_ids)


@bp_manage.route('/add_category', methods=['GET','POST'])
@login_required
@roles_required('Admin')
def add_category():

    """ Metodo exclusivo del administrador que sirve para anadir un nuevo category."""

    category_form = CategoryForm(request.form)

    if category_form.validate_on_submit():

        name = request.form['name']
        description = request.form['description']

        if not name or name == '' :
            flash("No null or empty values are allowed.","warn")
            return render_template('manage/add_edit_category.html', title='Add Category',
                add=True,form=category_form)
        if not description or description == '' :
            flash("No null or empty values are allowed.","warn")
            return render_template('manage/add_edit_category.html', title='Add Category',
                add=True,form=category_form)
        else:

            new_cat = Category(
                    name= name,
                    description=description
                )
            try:
                correct = True
                db.session.add(new_cat)
                db.session.commit()
            except Exception as e:
                # Catch anything unknown
                print(e)
                correct = False
            finally:
                if not correct:
                    # Cleanup and show error
                    db.session.rollback()
                    flash('Error when creating a Category','error')
                else:
                    flash("Our Category was created!","success")
                    return redirect(url_for('manage.manage_category'))
    return render_template('manage/add_edit_category.html', title='Add Category',
        add=True,form=category_form)


@bp_manage.route('/modify_category', methods=['GET','POST'])
@login_required
@roles_required('Admin')
def modify_category():

    """ Metodo exclusivo del administrador que sirve para modificar un category."""

    id_hash = request.args.get('id')

    if not id_hash or id_hash=='':
        flash('There is no ID.','error')
        return redirect(url_for('manage.manage_category'))

    #Localizamos el knowledges y luego lo modificamos
    modify_cat = Category.query.filter_by(id=hashids_hasher.decode(id_hash)).first()

    if not modify_cat:
        flash('There is no Category.','error')
        return redirect(url_for('manage.manage_category'))

    category_form = CategoryForm(name=modify_cat.name,description=modify_cat.description)

    if category_form.validate_on_submit():

        new_name = request.form['name']
        new_description = request.form['description']

        if not new_name or new_name == '' :
            flash("No null or empty values are allowed.","warn")
            return render_template('manage/add_edit_category.html', title='Modify Category',
                form=category_form)
        elif not new_description or new_description == '' :
            flash("No null or empty values are allowed.","warn")
            return render_template('manage/add_edit_category.html', title='Modify Category',
                form=category_form)
        else:
            
            modify_cat.name = new_name
            modify_cat.description = new_description
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
                    flash('Error when modifying a Category','error')
                else:
                    flash("Our Category was modified!","success")
                    return redirect(url_for('manage.manage_category'))
    return render_template('manage/add_edit_category.html', title='Modify Category',form=category_form)

@bp_manage.route('/manage_specialist', methods=['GET','POST'])
@login_required
@roles_required('Admin')
def manage_specialist():

    """ Metodo exclusivo del administrador que sirve para gestionar la tabla de Specialist."""

    page = request.args.get('page', 1, type=int)
    specialists_ids = Specialist.query.order_by(Specialist.id.asc()).paginate(
        page, current_app.config['PAGE_ITEMS'], False)

    if not specialists_ids.items:
        flash('There are no Specialists!','error')
        return render_template('manage/manage_specialist.html', title='Specialists')

    search_form = SearchForm(request.form)

    # Specialist.reindex()
    # current_app.elasticsearch.indices.delete('specialists')

    if request.args.get('q'):
        q = request.args.get('q')
        page = request.args.get('page', 1, type=int)
        specialists, total = Specialist.search(q, page,current_app.config['PAGE_ITEMS'])

        #Pues habria que hacer una paginacion manual conforme a los resultados de elastisearch
        next_url = url_for('manage.manage_specialist', q=q, page=page+1) \
            if total > page * current_app.config['PAGE_ITEMS'] else None
        prev_url = url_for('manage.manage_specialist', q=q, page=page-1) \
            if page > 1 else None


        return render_template('manage/manage_specialist.html', title=_('Specialists'),
            search_form=search_form,search_spe=specialists,next_url=next_url, prev_url=prev_url)

    if not request.args.get('delete'):
        return render_template('manage/manage_specialist.html', title='Specialists',
            search_form=search_form,lista_spe=specialists_ids)
    else:#Remove an specalist
        id_hash = request.args.get('id')

        if not id_hash or id_hash=='':
            flash('There is no ID.','error')
            return render_template('manage/manage_specialist.html', title='Specialists',
                search_form=search_form,lista_spe=specialists_ids)

        remove_spe = Specialist.query.filter_by(id=hashids_hasher.decode(id_hash)).first()

        try:
            correct = True
            db.session.delete(remove_spe)
            db.session.commit()
        except Exception as e:
            # Catch anything unknown
            print(e)
            correct = False
        finally:
            if not correct:
                # Cleanup and show error
                db.session.rollback()
                flash('Error when deleting a Specialist','error')
            else:
                flash("Our Specialist was deleted!","success")
                return redirect(url_for('manage.manage_specialist'))

    return render_template('manage/manage_specialist.html', title='Specialists',
        search_form=search_form,lista_spe=specialists_ids)


@bp_manage.route('/add_specialist', methods=['GET','POST'])
@login_required
@roles_required('Admin')
def add_specialist():

    """ Metodo exclusivo del administrador que sirve para anadir un nuevo specialist."""

    specialist_form = SpecialistForm(request.form)

    if specialist_form.validate_on_submit():
        name = request.form['name']
        description = request.form['description']
        ksat_ids = request.form['ksat']

        if not name or name == '' :
            flash("No null or empty values are allowed.","warn")
            return render_template('manage/add_edit_specialist.html', 
                title='Add Specialist',add=True,form=specialist_form)
        elif not description or description == '' :
            flash("No null or empty values are allowed.","warn")
            return render_template('manage/add_edit_specialist.html', 
                title='Add Specialist',add=True,form=specialist_form)
        elif not ksat_ids:
            flash("No null or empty values are allowed.","warn")
            return render_template('manage/add_edit_specialist.html', 
                title='Add Specialist',add=True,form=specialist_form)
        else:

            new_spe = Specialist(
                    name=name,
                    description=description,
                    ksat_ids= ksat_ids
                )
            try:
                correct = True
                db.session.add(new_spe)
                db.session.commit()
            except Exception as e:
                # Catch anything unknown
                print(e)
                correct = False
            finally:
                if not correct:
                    # Cleanup and show error
                    db.session.rollback()
                    flash('Error when creating a Specialist','error')
                else:
                    flash("Our Specialist was created!","success")
                    return redirect(url_for('manage.manage_specialist'))
    return render_template('manage/add_edit_specialist.html', title='Add Specialists',form=specialist_form)

@bp_manage.route('/modify_specialist', methods=['GET','POST'])
@login_required
@roles_required('Admin')
def modify_specialist():

    """ Metodo exclusivo del administrador que sirve para modificar un specialist."""

    id_hash = request.args.get('id')
    if not id_hash or id_hash=='':
        flash('There is no ID.','error')
        return redirect(url_for('manage.manage_specialist'))
    #Localizamos el knowledges y luego lo modificamos
    modify_spe = Specialist.query.filter_by(id=hashids_hasher.decode(id_hash)).first()

    if not modify_spe:
        flash('There is no Specialist','error')
        return redirect(url_for('manage.manage_specialist'))

    specialist_form = SpecialistForm(name=modify_spe.name,description=modify_spe.description)

    if specialist_form.validate_on_submit():

        new_name = request.form['name']
        new_description = request.form['description']


        if not new_name or new_name == '' :
            flash("No null or empty values are allowed.","warn")
            return render_template('manage/add_edit_specialist.html',
             title='Modify Specialist',form=specialist_form)
        elif not new_description or new_description == '' :
            flash("No null or empty values are allowed.","warn")
            return render_template('manage/add_edit_specialist.html',
             title='Modify Specialist',form=specialist_form)
        else:
            
            modify_spe.name = new_name
            modify_spe.description = new_description
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
                    flash('Error when modifying a Specialist','error')
                else:
                    flash("Our Specialist was modified!","success")
                    return redirect(url_for('manage.manage_specialist'))
    return render_template('manage/add_edit_specialist.html', title='Modify Specialist',form=specialist_form)

@bp_manage.route('/manage_work_role', methods=['GET','POST'])
@login_required
@roles_required('Admin')
def manage_work_role():

    """ Metodo exclusivo del administrador que sirve para gestionar la tabla de WorkRole."""

    page = request.args.get('page', 1, type=int)
    workRoles_ids = WorkRole.query.order_by(WorkRole.id.asc()).paginate(
        page, 2, False)

    if not workRoles_ids.items:
        flash('There are no Work roles!','error')
        return render_template('manage/manage_work_role.html', title='Work Roles')

    search_form = SearchForm(request.form)

    # WorkRole.reindex()
    # current_app.elasticsearch.indices.delete('work_roles')

    if request.args.get('q'):
        q = request.args.get('q')
        page = request.args.get('page', 1, type=int)
        workRoles, total = WorkRole.search(q, page,3)

        #Pues habria que hacer una paginacion manual conforme a los resultados de elastisearch
        next_url = url_for('manage.manage_work_role', q=q, page=page+1) \
            if total > page * 3 else None
        prev_url = url_for('manage.manage_work_role', q=q, page=page-1) \
            if page > 1 else None

        return render_template('manage/manage_work_role.html', title=_('Work Roles'),
            search_form=search_form,search_wk=workRoles,next_url=next_url, prev_url=prev_url)

    if not request.args.get('delete'):
        return render_template('manage/manage_work_role.html', title='Work Roles',
            search_form=search_form,lista_wk=workRoles_ids)
    else:#Remove an work role

        id_hash = request.args.get('id')

        if not id_hash or id_hash=='':
            flash('There is no ID.','error')
            return render_template('manage/manage_work_role.html', title='Work Roles',
                search_form=search_form,lista_wk=workRoles_ids)

        remove_wk = Work_Role.query.filter_by(id=hashids_hasher.decode(id_hash)).first()

        try:
            correct = True
            db.session.delete(remove_wk)
            db.session.commit()
        except Exception as e:
            # Catch anything unknown
            print(e)
            correct = False
        finally:
            if not correct:
                # Cleanup and show error
                db.session.rollback()
                flash('Error when deleting a Work_Role','error')
            else:
                flash("Our Work Role was deleted!","success")
                return redirect(url_for('manage.manage_work_role'))

    return render_template('manage/manage_work_role.html', title='Work Roles',
        search_form=search_form,lista_wk=workRoles_ids)


@bp_manage.route('/add_work_role', methods=['GET','POST'])
@login_required
@roles_required('Admin')
def add_work_role():

    """ Metodo exclusivo del administrador que sirve para anadir un nuevo work-role."""

    wk_form = WorkRoleForm(request.form)

    if wk_form.validate_on_submit():
        name = request.form['name']
        description = request.form['description']
        ksat = request.form['ksat']

        if not name or name == '' :
            flash("No null or empty values are allowed.","warn")
            return render_template('manage/add_edit_work_role.html', 
                title='Add Work Role',add=True,form=wk_form)
        if not description or description == '' :
            flash("No null or empty values are allowed.","warn")
            return render_template('manage/add_edit_work_role.html', 
                title='Add Work Role',add=True,form=wk_form)
        if not ksat or ksat == '' :
            flash("No null or empty values are allowed.","warn")
            return render_template('manage/add_edit_work_role.html', 
                title='Add Work Role',add=True,form=wk_form)
        else:
            new_wk = WorkRole(
                    name= name,
                    description=description,
                    ksat_ids=ksat
                )
            try:
                correct = True
                db.session.add(new_wk)
                db.session.commit()
            except Exception as e:
                # Catch anything unknown
                print(e)
                correct = False
            finally:
                if not correct:
                    # Cleanup and show error
                    db.session.rollback()
                    flash('Error when creating a Work Role','error')
                else:
                    flash("Our Work Role was created!","success")
                    return redirect(url_for('manage.manage_work_role'))

    return render_template('manage/add_edit_work_role.html', title='Add Work Role',form=wk_form)

@bp_manage.route('/modify_work_role', methods=['GET','POST'])
@login_required
@roles_required('Admin')
def modify_work_role():

    """ Metodo exclusivo del administrador que sirve para modificar un work-role."""

    id_hash = request.args.get('id')
    if not id_hash or id_hash=='':
        flash('There is no ID.','error')
        return redirect(url_for('manage.manage_knowledge'))
    #Localizamos el knowledges y luego lo modificamos
    modify_wk = WorkRole.query.filter_by(id=hashids_hasher.decode(id_hash)).first()

    if not modify_wk:
        flash('There is no Work Role','error')
        return redirect(url_for('manage.manage_knowledge'))

    wk_form = WorkRoleForm(name=modify_wk.name,description=modify_wk.description,
                           ksat=modify_wk.ksat_ids)

    if wk_form.validate_on_submit():

        new_name = request.form['name']
        new_description = request.form['description']
        new_ksat = request.form['ksat']

        if not new_name or new_name == '' :
            flash("No null or empty values are allowed.","warn")
            return render_template('manage/add_edit_work_role.html', title='Modify Work Role',
                form=wk_form)
        if not new_description or new_description == '' :
            flash("No null or empty values are allowed.",'warn')
            return render_template('manage/add_edit_work_role.html', title='Modify Work Role',
                form=wk_form)
        if not new_ksat or new_ksat == '' :
            flash("No null or empty values are allowed.",'warn')
            return render_template('manage/add_edit_work_role.html', title='Modify Work Role',
                form=wk_form)
        else:
            modify_wk.name = new_name
            modify_wk.description = new_description
            modify_wk.ksat_ids = new_ksat
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
                    flash('Error when modifying a Work Role','error')
                else:
                    flash("Our Work Role was modified!",'success')
                    return redirect(url_for('manage.manage_work_role'))

    return render_template('manage/add_edit_work_role.html', title='Modify Work Role',form=wk_form)


@bp_manage.route('/manage_db_catspewk', methods=['GET','POST'])
@login_required
@roles_required('Admin')
def manage_db_catspewk():

    """ Metodo exclusivo del administrador que sirve para gestionar las tablas CATEGORY-SPECIALIST-WKROLE.

    Esta configuracoin de relaciones entre CATEGORY --SPECIALIST --WORK ROLES SE HACE
    UNA SOLA VEZ Por el administrador !

    """

    categories_ids = Category.query.all()
    specialists_ids = Specialist.query.all()
    workRoles_ids = WorkRole.query.all()

    names_specialists = [i.name for i in specialists_ids]
    names_wk_names = [i.name for i in workRoles_ids]

    for i in categories_ids:
        if i.name == 'Analyze':

            name_spe = 'All-Source Analysis'
            if name_spe in names_specialists:
                index_spe = names_specialists.index(name_spe)
                # se añade dentro de la categoria su especilista
                i.specialist.append(specialists_ids[index_spe])
                #añidimos al especialista sus wk roles
                name_wk = 'All-Source Analyst'
                if name_wk in names_wk_names:
                    index = names_wk_names.index(name_wk)
                    specialists_ids[index_spe].wk_roles.append(workRoles_ids[index])

                name_wk = 'Mission Assessment Specialist'
                if  name_wk in names_wk_names:
                    index = names_wk_names.index(name_wk)
                    specialists_ids[index_spe].wk_roles.append(workRoles_ids[index])

            name_spe = 'Exploitation Analysis'
            if name_spe in names_specialists:
                index_spe = names_specialists.index(name_spe)
                # se añade dentro de la categoria su especilista
                i.specialist.append(specialists_ids[index_spe])
                #wk roles XXX buscarrr----------
                name_wk = 'Exploitation Analyst'
                if name_wk in names_wk_names:
                    index = names_wk_names.index(name_wk)
                    specialists_ids[index_spe].wk_roles.append(workRoles_ids[index])

            name_spe = 'Language Analysis'
            if name_spe in names_specialists:
                index_spe = names_specialists.index(name_spe)
                # se añade dentro de la categoria su especilista
                i.specialist.append(specialists_ids[index_spe])
                #awk roles XXX buscarrr----------
                name_wk = 'Multi-Disciplined Language Analyst'
                if name_wk in names_wk_names:
                    index = names_wk_names.index(name_wk)
                    specialists_ids[index_spe].wk_roles.append(workRoles_ids[index])

            name_spe = 'Targets'
            if name_spe in names_specialists:
                index_spe = names_specialists.index(name_spe)
                # se añade dentro de la categoria su especilista
                i.specialist.append(specialists_ids[index_spe])
                #wk roles XXX buscarrr----------
                wk_name = 'Target Developer'
                if wk_name in names_wk_names:
                    index = names_wk_names.index(wk_name)
                    specialists_ids[index_spe].wk_roles.append(workRoles_ids[index])

                wk_name = 'Target Network Analyst'
                if wk_name in names_wk_names:
                    index = names_wk_names.index(wk_name)
                    specialists_ids[index_spe].wk_roles.append(workRoles_ids[index])

            name_spe = 'Threat Analysis'
            if name_spe in names_specialists:
                index_spe = names_specialists.index(name_spe)
                # se añade dentro de la categoria su especilista
                i.specialist.append(specialists_ids[index_spe])
                #wk roles XXX buscarrr----------
                wk_name = 'Threat/Warning Analyst'
                if wk_name in names_wk_names:
                    index = names_wk_names.index(wk_name)
                    specialists_ids[index_spe].wk_roles.append(workRoles_ids[index])


        if i.name == 'Collect and Operate':
            name_spe = 'Collection Operations'
            if name_spe in names_specialists:
                index_spe = names_specialists.index(name_spe)
                # se añade dentro de la categoria su especilista
                i.specialist.append(specialists_ids[index_spe])
                #añidimos al especialista sus wk roles
                wk_name = 'All Source-Collection Manager'
                if wk_name in names_wk_names:
                    index = names_wk_names.index(wk_name)
                    specialists_ids[index_spe].wk_roles.append(workRoles_ids[index])
                wk_name = 'All Source-Collection Requirements Manager'
                if wk_name in names_wk_names:
                    index = names_wk_names.index(wk_name)
                    specialists_ids[index_spe].wk_roles.append(workRoles_ids[index])

            name_spe = 'Cyber Operational Planning'
            if name_spe in names_specialists:
                index_spe = names_specialists.index(name_spe)
                # se añade dentro de la categoria su especilista
                i.specialist.append(specialists_ids[index_spe])
                #wk roles XXX buscarrr----------
                wk_name = 'Cyber Intel Planner'
                if wk_name in names_wk_names:
                    index = names_wk_names.index(wk_name)
                    specialists_ids[index_spe].wk_roles.append(workRoles_ids[index])

                wk_name = 'Cyber Ops Planner'
                if wk_name in names_wk_names:
                    index = names_wk_names.index(wk_name)
                    specialists_ids[index_spe].wk_roles.append(workRoles_ids[index])

                wk_name = 'Partner Integration Planner'
                if wk_name in names_wk_names:
                    index = names_wk_names.index(wk_name)
                    specialists_ids[index_spe].wk_roles.append(workRoles_ids[index])

            name_spe = 'Cyber Operations'
            if name_spe in names_specialists:
                index_spe = names_specialists.index(name_spe)
                # se añade dentro de la categoria su especilista
                i.specialist.append(specialists_ids[index_spe])
                #awk roles XXX buscarrr----------
                wk_name = 'Cyber Operator'
                if wk_name in names_wk_names:
                    index = names_wk_names.index(wk_name)
                    specialists_ids[index_spe].wk_roles.append(workRoles_ids[index])


        if i.name == 'Investigate':
            name_spe = 'Cyber Investigation'
            if name_spe in names_specialists:
                index_spe = names_specialists.index(name_spe)
                # se añade dentro de la categoria su especilista
                i.specialist.append(specialists_ids[index_spe])
                #wk roles XXX buscarrr----------
                wk_name = 'Cyber Crime Investigator'
                if wk_name in names_wk_names:
                    index = names_wk_names.index(wk_name)
                    specialists_ids[index_spe].wk_roles.append(workRoles_ids[index])


            name_spe = 'Digital Forensics'
            if name_spe in names_specialists:
                index_spe = names_specialists.index(name_spe)
                # se añade dentro de la categoria su especilista
                i.specialist.append(specialists_ids[index_spe])
                #awk roles XXX buscarrr----------
                wk_name = 'Cyber Defense Forensics Analyst'
                if wk_name in names_wk_names:
                    index = names_wk_names.index(wk_name)
                    specialists_ids[index_spe].wk_roles.append(workRoles_ids[index])

                wk_name = 'Law Enforcement/Counterintelligence Forensics Analyst'
                if wk_name in names_wk_names:
                    index = names_wk_names.index(wk_name)
                    specialists_ids[index_spe].wk_roles.append(workRoles_ids[index])


        if i.name == 'Operate and Maintain':
            name_spe = 'Customer Service and Technical Support'
            if name_spe in names_specialists:
                index_spe = names_specialists.index(name_spe)
                # se añade dentro de la categoria su especilista
                i.specialist.append(specialists_ids[index_spe])
                #añidimos al especialista sus wk roles
                wk_name = 'Technical Support Specialist'
                if wk_name in names_wk_names:
                    index = names_wk_names.index(wk_name)
                    specialists_ids[index_spe].wk_roles.append(workRoles_ids[index])
                

            name_spe = 'Data Administration'
            if name_spe in names_specialists:
                index_spe = names_specialists.index(name_spe)
                # se añade dentro de la categoria su especilista
                i.specialist.append(specialists_ids[index_spe])
                #wk roles XXX buscarrr----------
                wk_name = 'Data Analyst'
                if wk_name in names_wk_names:
                    index = names_wk_names.index(wk_name)
                    specialists_ids[index_spe].wk_roles.append(workRoles_ids[index])

                wk_name = 'Database Administrator'
                if wk_name in names_wk_names:
                    index = names_wk_names.index(wk_name)
                    specialists_ids[index_spe].wk_roles.append(workRoles_ids[index])

            name_spe = 'Knowledge Management'
            if name_spe in names_specialists:
                index_spe = names_specialists.index(name_spe)
                # se añade dentro de la categoria su especilista
                i.specialist.append(specialists_ids[index_spe])
                #awk roles XXX buscarrr----------
                wk_name = 'Knowledge Manager'
                if wk_name in names_wk_names:
                    index = names_wk_names.index(wk_name)
                    specialists_ids[index_spe].wk_roles.append(workRoles_ids[index])



            name_spe = 'Network Services'
            if name_spe in names_specialists:
                index_spe = names_specialists.index(name_spe)
                # se añade dentro de la categoria su especilista
                i.specialist.append(specialists_ids[index_spe])
                #wk roles XXX buscarrr----------
                wk_name = 'Network Operations Specialist'
                if wk_name in names_wk_names:
                    index = names_wk_names.index(wk_name)
                    specialists_ids[index_spe].wk_roles.append(workRoles_ids[index])



            name_spe = 'Systems Administration'
            if name_spe in names_specialists:
                index_spe = names_specialists.index(name_spe)
                # se añade dentro de la categoria su especilista
                i.specialist.append(specialists_ids[index_spe])
                #wk roles XXX buscarrr----------
                wk_name = 'System Administrator'
                if wk_name in names_wk_names:
                    index = names_wk_names.index(wk_name)
                    specialists_ids[index_spe].wk_roles.append(workRoles_ids[index])
                

            name_spe = 'Systems Analysis'
            if name_spe in names_specialists:
                index_spe = names_specialists.index(name_spe)
                # se añade dentro de la categoria su especilista
                i.specialist.append(specialists_ids[index_spe])
                #wk roles XXX buscarrr----------
                wk_name = 'Systems Security Analyst'
                if wk_name in names_wk_names:
                    index = names_wk_names.index(wk_name)
                    specialists_ids[index_spe].wk_roles.append(workRoles_ids[index])



        if i.name == 'Oversee and Govern':
            name_spe = 'Cybersecurity Management'
            if name_spe in names_specialists:
                index_spe = names_specialists.index(name_spe)
                # se añade dentro de la categoria su especilista
                i.specialist.append(specialists_ids[index_spe])
                #wk roles XXX buscarrr----------
                wk_name = 'Communications Security (COMSEC) Manager'
                if wk_name in names_wk_names:
                    index = names_wk_names.index(wk_name)
                    specialists_ids[index_spe].wk_roles.append(workRoles_ids[index])

                wk_name = 'Information Systems Security Manager'
                if wk_name in names_wk_names:
                    index = names_wk_names.index(wk_name)
                    specialists_ids[index_spe].wk_roles.append(workRoles_ids[index])

            name_spe = 'Executive Cyber Leadership'
            if name_spe in names_specialists:
                index_spe = names_specialists.index(name_spe)
                # se añade dentro de la categoria su especilista
                i.specialist.append(specialists_ids[index_spe])
                #awk roles XXX buscarrr----------
                wk_name = 'Executive Cyber Leadership'
                if wk_name in names_wk_names:
                    index = names_wk_names.index(wk_name)
                    specialists_ids[index_spe].wk_roles.append(workRoles_ids[index])


            name_spe = 'Legal Advice and Advocacy'
            if name_spe in names_specialists:
                index_spe = names_specialists.index(name_spe)
                # se añade dentro de la categoria su especilista
                i.specialist.append(specialists_ids[index_spe])
                #wk roles XXX buscarrr----------
                wk_name = 'Cyber Legal Advisor'
                if wk_name in names_wk_names:
                    index = names_wk_names.index(wk_name)
                    specialists_ids[index_spe].wk_roles.append(workRoles_ids[index])

                wk_name = 'Privacy Officer/Privacy Compliance Manager'
                if wk_name in names_wk_names:
                    index = names_wk_names.index(wk_name)
                    specialists_ids[index_spe].wk_roles.append(workRoles_ids[index])

            name_spe = 'Program/Project Management and Acquisition'
            if name_spe in names_specialists:
                index_spe = names_specialists.index(name_spe)
                # se añade dentro de la categoria su especilista
                i.specialist.append(specialists_ids[index_spe])
                #wk roles XXX buscarrr----------
                wk_name = 'IT Investment/Portfolio Manager'
                if wk_name in names_wk_names:
                    index = names_wk_names.index(wk_name)
                    specialists_ids[index_spe].wk_roles.append(workRoles_ids[index])

                wk_name = 'IT Program Auditor'
                if wk_name in names_wk_names:
                    index = names_wk_names.index(wk_name)
                    specialists_ids[index_spe].wk_roles.append(workRoles_ids[index])


                wk_name = 'IT Project Manager'
                if wk_name in names_wk_names:
                    index = names_wk_names.index(wk_name)
                    specialists_ids[index_spe].wk_roles.append(workRoles_ids[index])


                wk_name = 'Product Support Manager'
                if wk_name in names_wk_names:
                    index = names_wk_names.index(wk_name)
                    specialists_ids[index_spe].wk_roles.append(workRoles_ids[index])


                wk_name = 'Program Manager'
                if wk_name in names_wk_names:
                    index = names_wk_names.index(wk_name)
                    specialists_ids[index_spe].wk_roles.append(workRoles_ids[index])

            name_spe = 'Strategic Planning and Policy'
            if name_spe in names_specialists:
                index_spe = names_specialists.index(name_spe)
                # se añade dentro de la categoria su especilista
                i.specialist.append(specialists_ids[index_spe])
                #wk roles XXX buscarrr----------
                wk_name = 'Cyber Policy and Strategy Planner'
                if wk_name in names_wk_names:
                    index = names_wk_names.index(wk_name)
                    specialists_ids[index_spe].wk_roles.append(workRoles_ids[index])

                wk_name = 'Cyber Workforce Developer and Manager'
                if wk_name in names_wk_names:
                    index = names_wk_names.index(wk_name)
                    specialists_ids[index_spe].wk_roles.append(workRoles_ids[index])

            name_spe = 'Training, Education, and Awareness'
            if name_spe in names_specialists:
                index_spe = names_specialists.index(name_spe)
                # se añade dentro de la categoria su especilista
                i.specialist.append(specialists_ids[index_spe])
                #wk roles XXX buscarrr----------
                wk_name = 'Cyber Instructional Curriculum Developer'
                if wk_name in names_wk_names:
                    index = names_wk_names.index(wk_name)
                    specialists_ids[index_spe].wk_roles.append(workRoles_ids[index])

                wk_name = 'Cyber Instructor'
                if wk_name in names_wk_names:
                    index = names_wk_names.index(wk_name)
                    specialists_ids[index_spe].wk_roles.append(workRoles_ids[index])

        if i.name == 'Protect and Defend':
            name_spe = 'Cyber Defense Analysis'
            if name_spe in names_specialists:
                index_spe = names_specialists.index(name_spe)
                # se añade dentro de la categoria su especilista
                i.specialist.append(specialists_ids[index_spe])
                #wk roles XXX buscarrr----------
                wk_name = 'Cyber Defense Analyst'
                if wk_name in names_wk_names:
                    index = names_wk_names.index(wk_name)
                    specialists_ids[index_spe].wk_roles.append(workRoles_ids[index])


            name_spe = 'Cyber Defense Infrastructure Support'
            if name_spe in names_specialists:
                index_spe = names_specialists.index(name_spe)
                # se añade dentro de la categoria su especilista
                i.specialist.append(specialists_ids[index_spe])
                #wk roles XXX buscarrr----------
                wk_name = 'Cyber Defense Infrastructure Support Specialist'
                if wk_name in names_wk_names:
                    index = names_wk_names.index(wk_name)
                    specialists_ids[index_spe].wk_roles.append(workRoles_ids[index])


            name_spe = 'Incident Response'
            if name_spe in names_specialists:
                index_spe = names_specialists.index(name_spe)
                # se añade dentro de la categoria su especilista
                i.specialist.append(specialists_ids[index_spe])
                #wk roles XXX buscarrr----------
                wk_name = 'Cyber Defense Incident Responder'
                if wk_name in names_wk_names:
                    index = names_wk_names.index(wk_name)
                    specialists_ids[index_spe].wk_roles.append(workRoles_ids[index])


            name_spe = 'Vulnerability Assessment and Management'
            if name_spe in names_specialists:
                index_spe = names_specialists.index(name_spe)
                # se añade dentro de la categoria su especilista
                i.specialist.append(specialists_ids[index_spe])
                #wk roles XXX buscarrr----------
                wk_name = 'Vulnerability Assessment Analyst'
                if wk_name in names_wk_names:
                    index = names_wk_names.index(wk_name)
                    specialists_ids[index_spe].wk_roles.append(workRoles_ids[index])


        if i.name == 'Securely Provision':
            name_spe = 'Risk Management'
            if name_spe in names_specialists:
                index_spe = names_specialists.index(name_spe)
                # se añade dentro de la categoria su especilista
                i.specialist.append(specialists_ids[index_spe])
                #wk roles XXX buscarrr----------
                wk_name = 'Authorizing Official/Designating Representative'
                if wk_name in names_wk_names:
                    index = names_wk_names.index(wk_name)
                    specialists_ids[index_spe].wk_roles.append(workRoles_ids[index])

                wk_name = 'Security Control Assessor'
                if wk_name in names_wk_names:
                    index = names_wk_names.index(wk_name)
                    specialists_ids[index_spe].wk_roles.append(workRoles_ids[index])

            name_spe = 'Software Development'
            if name_spe in names_specialists:
                index_spe = names_specialists.index(name_spe)
                # se añade dentro de la categoria su especilista
                i.specialist.append(specialists_ids[index_spe])
                #wk roles XXX buscarrr----------
                wk_name = 'Secure Software Assessor'
                if wk_name in names_wk_names:
                    index = names_wk_names.index(wk_name)
                    specialists_ids[index_spe].wk_roles.append(workRoles_ids[index])

                wk_name = 'Software Developer'
                if wk_name in names_wk_names:
                    index = names_wk_names.index(wk_name)
                    specialists_ids[index_spe].wk_roles.append(workRoles_ids[index])

            name_spe = 'Systems Architecture'
            if name_spe in names_specialists:
                index_spe = names_specialists.index(name_spe)
                # se añade dentro de la categoria su especilista
                i.specialist.append(specialists_ids[index_spe])
                #wk roles XXX buscarrr----------

                wk_name = 'Enterprise Architect'
                if wk_name in names_wk_names:
                    index = names_wk_names.index(wk_name)
                    specialists_ids[index_spe].wk_roles.append(workRoles_ids[index])

                wk_name = 'Security Architect'
                if wk_name in names_wk_names:
                    index = names_wk_names.index(wk_name)
                    specialists_ids[index_spe].wk_roles.append(workRoles_ids[index])

            name_spe = 'Systems Development'
            if name_spe in names_specialists:
                index_spe = names_specialists.index(name_spe)
                # se añade dentro de la categoria su especilista
                i.specialist.append(specialists_ids[index_spe])
                #wk roles XXX buscarrr----------
                wk_name = 'Information Systems Security Developer'
                if wk_name in names_wk_names:
                    index = names_wk_names.index(wk_name)
                    specialists_ids[index_spe].wk_roles.append(workRoles_ids[index])

                wk_name = 'Systems Developer'
                if wk_name in names_wk_names:
                    index = names_wk_names.index(wk_name)
                    specialists_ids[index_spe].wk_roles.append(workRoles_ids[index])

            name_spe = 'Systems Requirements Planning'
            if name_spe in names_specialists:
                index_spe = names_specialists.index(name_spe)
                # se añade dentro de la categoria su especilista
                i.specialist.append(specialists_ids[index_spe])
                #wk roles XXX buscarrr----------
                wk_name = 'Systems Requirements Planner'
                if wk_name in names_wk_names:
                    index = names_wk_names.index(wk_name)
                    specialists_ids[index_spe].wk_roles.append(workRoles_ids[index])


            name_spe = 'Technology R&D'
            if name_spe in names_specialists:
                index_spe = names_specialists.index(name_spe)
                # se añade dentro de la categoria su especilista
                i.specialist.append(specialists_ids[index_spe])
                #wk roles XXX buscarrr----------
                wk_name = 'Research & Development Specialist'
                if wk_name in names_wk_names:
                    index = names_wk_names.index(wk_name)
                    specialists_ids[index_spe].wk_roles.append(workRoles_ids[index])


            name_spe = 'Test and Evaluation'
            if name_spe in names_specialists:
                index_spe = names_specialists.index(name_spe)
                # se añade dentro de la categoria su especilista
                i.specialist.append(specialists_ids[index_spe])
                #wk roles XXX buscarrr----------
                wk_name = 'System Testing and Evaluation Specialist'
                if wk_name in names_wk_names:
                    index = names_wk_names.index(wk_name)
                    specialists_ids[index_spe].wk_roles.append(workRoles_ids[index])

    db.session.commit()


    return jsonify({'status':'Ok'})
