import json
from flask import abort, make_response, jsonify

from project.config import db

from project.model.db import Environment
from project.model.schemas import environment_schema, environments_schema

""" Controller Methods for Environment """

def read_all():
    """ API endpoint: /environment """

    environments = Environment.query.all()
    return environments_schema.dump(environments)

def read(id):
    """ API endpoint:  """

    environment = Environment.query.filter(Environment.id == id).one_or_none()
    if environment is not None:
        return environment_schema.dump(environment)
    else:
        abort(404, f"Environment id {id} not found")

def read_name(name):
    """ API endpoint: /environment/name/{name} """

    environment = Environment.query.filter(Environment.name == name).one_or_none()
    if environment is not None:
        return environment_schema.dump(environment)
    else:
        abort(404, f"Environment name {name} not found")

def create(env):
    """ API endpoint: """

    name = env.get("name")
    existing_env = Environment.query.filter(Environment.name == name).one_or_none()

    if existing_env is None:
        new_env = environment_schema.load(env, session=db.session)
        db.session.add(new_env)
        db.session.commit()
        return environment_schema.dump(new_env), 201
    else:
        abort(406, f"Environment {name} already exists")

def delete(id):
    """ API endpoint:  """

    existing_env = Environment.query.filter(Environment.id == id).one_or_none()
    if existing_env:
        db.session.delete(existing_env)
        db.session.commit()
        return make_response(f"Environment {id} successfully deleted", 202)
    else:
        abort(404, f"Environment id {id} not found")

def delete_name(name):
    """ API endpoint:  """

    existing_env = Environment.query.filter(Environment.name == name).one_or_none()
    if existing_env:
        db.session.delete(existing_env)
        db.session.commit()
        return make_response(f"Environment {id} successfully deleted", 202)
    else:
        abort(404, f"Environment id {id} not found")