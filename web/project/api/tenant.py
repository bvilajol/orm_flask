import json
from flask import abort, make_response, jsonify

from project.config import db
from project.model.db import Tenant
from project.model.schemas import tenant_schema, tenants_schema

def read_all():
    """ API endpoint: /tenants """

    tenants = Tenant.query.all()
    return tenants_schema.dump(tenants)

def list_name():
    """ API endpoint: /tenants/list/name """

    tenants = Tenant.query.all()
    names = []
    if tenants:
        for tenant in tenants:
            if tenant.name not in names:
                names.append(tenant.name)
    return (jsonify(names)), 200

def read(id):
    """ API endpoint: /tenant/id/{id} """

    tenant = Tenant.query.filter(Tenant.id == id).one_or_none()

    if tenant:
        return tenant_schema.dump(tenant)
    else:
        abort(404, f"Tenant id {id} not found")

def read_name(name):
    """ API endpoint: /tenant/name/{name} """

    tenants = Tenant.query.filter(Tenant.name == name).all()
    if tenants is not None:
        return tenants_schema.dump(tenants)
    else:
        abort(404, f"Tenant name {name} not found")

def create(tenant):
    """ API endpoint: /tenants: """

    name = tenant.get("name")
    existing_tenant = Tenant.query.filter(Tenant.name == name).one_or_none()
    if existing_tenant is None:
        new_tenant = tenant_schema.load(tenant, session=db.session)
        db.session.add(new_tenant)
        db.session.commit()
        return tenant_schema.dump(new_tenant), 201
    else:
        abort(406, f"Tenant name {name} already exists")
        
def delete_name(name):
    """ API endpoint: /tenant/name/{name} """

    existing_tenant = Tenant.query.filter(Tenant.name == name).one_or_none()
    if existing_tenant:
        db.session.delete(existing_tenant)
        db.session.commit()
        return make_response(f"Tenant {name} successfully deleted", 202)
    else:
        abort(404, f"Tenant name {name} not found")

def delete(id):
    """ API endpoint: /tenant/id/{name} """

    existing_tenant = Tenant.query.filter(Tenant.id == id).one_or_none()
    if existing_tenant:
        db.session.delete(existing_tenant)
        db.session.commit()
        return make_response(f"Tenant {id} successfully deleted", 202)
    else:
        abort(404, f"Tenant id {id} not found")