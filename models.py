# -*- coding: utf-8 -*-

"""This file contains SQLAlchemy model declarations."""

import datetime
import os

from flask_user import UserMixin
from sqlalchemy import event, CheckConstraint
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.orm.collections import attribute_mapped_collection

from cyber_role import db
from cyber_role.search import add_to_index, remove_from_index, query_index



#Configuracion de Elasticsearch para convertir los ids (JSON que devuelve elastic) en objetos sqlachemy
# Y reset de inddex para que no explote en un futuro
class SearchableMixin(object):
    @classmethod
    def search(cls, expression, page, per_page):
        ids, total = query_index(cls.__tablename__, expression, page, per_page)
        if total == 0:
            return cls.query.filter_by(id=0), 0
        when = []
        for i in range(len(ids)):
            when.append((ids[i], i))

        return cls.query.filter(cls.id.in_(ids)).order_by(
            db.case(when, value=cls.id)), total

    @classmethod
    def before_commit(cls, session):
        session._changes = {
            'add': list(session.new),
            'update': list(session.dirty),
            'delete': list(session.deleted)
        }

    @classmethod
    def after_commit(cls, session):
        for obj in session._changes['add']:
            if isinstance(obj, SearchableMixin):
                add_to_index(obj.__tablename__, obj)
        for obj in session._changes['update']:
            if isinstance(obj, SearchableMixin):
                add_to_index(obj.__tablename__, obj)
        for obj in session._changes['delete']:
            if isinstance(obj, SearchableMixin):
                remove_from_index(obj.__tablename__, obj)
        session._changes = None

    @classmethod
    def reindex(cls):
        for obj in cls.query:
            add_to_index(cls.__tablename__, obj)
            # remove_from_index(cls.__tablename__, obj)

db.event.listen(db.session, 'before_commit', SearchableMixin.before_commit)
db.event.listen(db.session, 'after_commit', SearchableMixin.after_commit)




# Flask-User models
class Role(SearchableMixin,db.Model):
    """Flask-User model for user roles.
    Attributes:
        id (int): Unique ID of the role.
        name (str): Unique name of the role.
    """
    __tablename__ = 'roles'
    __searchable__ = ['name']

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True)


    @classmethod
    def get_role(self, name):
        """Obtain an already existing role by name.

        Args:
            name (str): Unique name of the role.

        Returns:
            Role instance or None if not found.
        """
        role = Role.query.filter_by(name=name).first()

        return role



class User(db.Model,SearchableMixin, UserMixin):
    """Flask-User model for users.
    Includes additional attributes.
    Attributes:
        locale (str): Locale code.
        timezone (str): Timezone used to localize dates.
    """
    __tablename__ = 'users'

    #Indexacion mediante elastiseacrh del atributo username
    __searchable__ = ['username']

    id = db.Column(db.Integer, primary_key=True)

    # Authentication
    username = db.Column(db.String(50), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False, default='')
    reset_password_token = db.Column(
        db.String(100), nullable=False, default='')

    # Email information
    email = db.Column(db.String(255), nullable=False, unique=True)
    confirmed_at = db.Column(db.DateTime)

    # User information
    is_enabled = db.Column(db.Boolean, nullable=False, default=False)
    first_name = db.Column(db.String(50), nullable=False, default='')
    last_name = db.Column(db.String(50), nullable=False, default='')

    # Additional attributes
    locale = db.Column(db.String(2), nullable=False, default='en')
    timezone = db.Column(db.String(50), nullable=False, default='UTC')

    # Relationships
    roles = db.relationship(
        'Role', secondary='user_roles',
        backref=db.backref('users', lazy='dynamic'),
        cascade='delete, save-update',collection_class=set
    )

    # Proxies para obtener los roles del usuario
    role_names = association_proxy(
        'roles',
        'name',
        creator=lambda n: Role.get_role(n)
    )

    #Relacion 1 a 1 para eso usamos uselist a false
    ksat = db.relationship('Ksat', uselist=False, backref='users')


    # Un usuario 1 tendra  N  courses
    course = db.relationship('Course', backref='users',lazy='dynamic')


    def is_active(self):
        return self.is_enabled

    @classmethod
    def get_by_username(self, username):
        """Obtain an already existing user by username.

        Args:
            username (str): Unique username of the user

        Returns:
            User instance or None if not found.
        """
        user = User.query.filter_by(username=username).first()

        return user


class UserRoles(db.Model):
    """Flask-User model for user-role relations."""
    __tablename__ = 'user_roles'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', onupdate='CASCADE', ondelete='CASCADE')
    )
    role_id = db.Column(
        db.Integer,
        db.ForeignKey('roles.id', onupdate='CASCADE', ondelete='CASCADE')
    )


# class CourseUsers(db.Model):
#     """Flask-User model for course-users.
#     Includes additional attributes.
#     Attributes:

#     """
#     __tablename__ = 'course_users'

#     id = db.Column(db.Integer, primary_key=True)
#     user_id = db.Column(
#         db.Integer,
#         db.ForeignKey('users.id', onupdate='CASCADE', ondelete='CASCADE')
#     )
#     course_id = db.Column(
#         db.Integer,
#         db.ForeignKey('courses.id', onupdate='CASCADE', ondelete='CASCADE')
#     )


class Course(SearchableMixin,db.Model):
    """Flask-User model for course.

    Attributes:

    """
    __tablename__ = 'courses'
    __searchable__ = ['name']

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(400), nullable=False, unique=True)
    description = db.Column(db.String(500), nullable=False, unique=True)
    create_date = db.Column(db.DateTime)

    total_time = db.Column(db.Integer, nullable=False)
    total_cost = db.Column(db.Integer, nullable=False)
    average_reputation = db.Column(db.Integer, nullable=False)


    fitness_learning_goal = db.Column(db.Float, nullable=False)
    fitness_time = db.Column(db.Float, nullable=False)
    fitness_cost = db.Column(db.Float, nullable=False)
    fitness_reputation = db.Column(db.Float, nullable=False)
    fitness_total = db.Column(db.Float, nullable=False)


    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', onupdate='CASCADE', ondelete='CASCADE')
    )

    user = db.relationship('User',backref=db.backref('courses'))


    los = db.relationship('LearningObject', backref='courses',collection_class=set)



    @classmethod
    def get_by_name(self, course_name):
        """Obtain an already existing user by name.

        Args:
            course_name (str): Unique lo-name

        Returns:
            Course instance or None if not found.
        """
        course = Course.query.filter_by(name=course_name).first()

        return course



class LearningObject(db.Model,SearchableMixin):
    """Flask-User model for learning objects.


    Attributes:

    """
    __tablename__ = 'los'
    __searchable__ = ['id']

    id = db.Column(db.Integer, primary_key=True)

    time = db.Column(db.Integer, nullable=False)
    cost = db.Column(db.Integer, nullable=False)
    reputation = db.Column(db.Integer, nullable=False)


    #Aqui solo tendremos solo dos ksas
    ksats = db.relationship('Ksat', backref='los')

    course_id = db.Column(
        db.Integer,
        db.ForeignKey('courses.id', onupdate='CASCADE', ondelete='CASCADE')
    )




class Category(db.Model,SearchableMixin):
    """Flask-model for categories.
    Includes additional attributes.
    Attributes:

    """
    __tablename__ = 'categories'
    __searchable__ = ['name']

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)
    description = db.Column(db.String(255), nullable=False, default='')


    specialist = db.relationship('Specialist',backref=db.backref('categories'))
    specialist_names = association_proxy(
        'specialists',
        'name',
        creator=lambda n: Specialist.get_specialist(n)
    )

    @classmethod
    def get_by_name(self, name):
        """Obtain an already existing user by name.

        Args:
            name (str): Unique categorie_name

        Returns:
            User instance or None if not found.
        """
        category = Category.query.filter_by(name=name).first()

        return category


class Specialist(db.Model,SearchableMixin):
    """Flask-model for specialists.
    Includes additional attributes.
    Attributes:

    """
    __tablename__ = 'specialists'
    __searchable__ = ['name']

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)
    description = db.Column(db.String(580), nullable=False, default='')

    category_id = db.Column(
        db.Integer,
        db.ForeignKey('categories.id', onupdate='CASCADE', ondelete='CASCADE')
    )
    #info de su category
    category = db.relationship('Category',backref=db.backref('specialists'))


    #los wk roles que tiene un specialist
    wk_roles = db.relationship('WorkRole',backref=db.backref('specialists'))
    wk_names = association_proxy(
        'work_roles',
        'name',
        creator=lambda n: WorkRole.get_by_name(n)
    )

    @classmethod
    def get_specialist(self, name):
        """Obtain an already existing specaliast by name.
          Args:
            name (str): Unique specialist_name
          Returns:
            Specialist instance or None if not found.
        """

        specialist = Specialist.query.filter_by(name=name).first()
        return specialist


class WorkRole(db.Model,SearchableMixin):
    """Flask-model for work-roles.
    Includes additional attributes.
    Attributes:
    """
    __tablename__ = 'work_roles'
    __searchable__ = ['name']

    # Hay que meter los valores de forma manual desde la db
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(55), nullable=False, unique=True)
    description = db.Column(db.String(500), nullable=False, unique=True)


    """
    Example de JSON - ksat_ids:

    "name_work_role":{
             "knowledges_ids : {
                  "myK0001":"Description..", 
                  }
               },
             "skill_ids : {
                  "myS0001": "Description..",
                  }
               },
             "abilities_ids : {
                  "myA0001":"Description..",
                  }
               },
             "tasks_ids : {
                  "myT0001":"Description..",
                  }
               }
      }
    """
    ksat_ids = db.Column(JSON)


    specialist_id = db.Column(
        db.Integer,
        db.ForeignKey('specialists.id', onupdate='CASCADE', ondelete='CASCADE')
    )
    specialist = db.relationship('Specialist',backref=db.backref('work_roles'))



    @classmethod
    def get_by_name(self, wk_name):
        """Obtain an already existing work_role by name.

        Args:
            wk_name (str): Unique work role name

        Returns:
            User instance or None if not found.
        """
        work_role = WorkRole.query.filter_by(name=wk_name).first()

        return work_role


class Ksat(db.Model,SearchableMixin):
    """Model for Ksats.
    Includes additional attributes.
    Attributes:

    """
    __tablename__ = 'ksats'
    __searchable__ = ['name']

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(400), nullable=False, unique=True)
    date = db.Column(db.DateTime)
    # Porque solo un usuario tendra un KSA exclusivo, ya que un usuario tiene
    # un KSa id unico

    """
    Example de JSON:
    {
       "knowledges_ids = {"myK0001": {
             "id_number": 24,
             "level": 5,
             "description": "Description....."}
         }
       ,
       "skill_ids = {"myS0001": {
             "id_number": 24,
             "level": 5,
             "description": "Description....."}
         },
       "abilities_ids = {"myA0001": {
             "id_number": 24,
             "level": 5,
             "description": "Description....."}
         },
       "tasks_ids = {"myT0001": {
             "ID": 24,
             "description": "Description....."}
         }
    }
    
    """
    ksat_ids = db.Column(JSON)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', onupdate='CASCADE', ondelete='CASCADE')
    )

    user = db.relationship('User',backref=db.backref('ksats'))


    lo_id = db.Column(
        db.Integer,
        db.ForeignKey('los.id', onupdate='CASCADE', ondelete='CASCADE')
    )


    @classmethod
    def get_by_name(self, name):
        """Obtain an already existing user by name.

        Args:
            name (str): Unique ksat_name

        Returns:
            User instance or None if not found.
        """
        ksat = Ksat.query.filter_by(name=name).first()

        return ksat


class Knowledge(db.Model,SearchableMixin):
    """Flask-model for knowledges.
    Includes additional attributes.
    Attributes:

    """
    __tablename__ = 'knowledges'
    __searchable__ = ['description']

    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(350), nullable=False, unique=True)


class Skill(db.Model,SearchableMixin):
    """Flask-model for skills.
    Includes additional attributes.
    Attributes:

    """
    __tablename__ = 'skills'
    __searchable__ = ['description']

    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(350), nullable=False, unique=True)


class Ability(db.Model,SearchableMixin):
    """Flask-model for abilities.
    Includes additional attributes.
    Attributes:

    """
    __tablename__ = 'abilities'
    __searchable__ = ['description']

    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(550), nullable=False, unique=True)


class Task(db.Model,SearchableMixin):
    """Flask-model for tasks.
    Includes additional attributes.
    Attributes:

    """
    __tablename__ = 'tasks'
    __searchable__ = ['description']

    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(430), nullable=False, unique=True)
