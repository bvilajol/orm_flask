import json
from flask import abort, make_response, jsonify

from project.config import db

from project.model.db import (  Contact,
                                Tenant,
                                Environment,
                                )
from project.model.schemas import contact_schema, contacts_schema

def read_all():
    """ API endpoint: """
    contacts = Contact.query.all()
    return contacts_schema.dump(contacts)

def read(id):
    """ API endpoint: """
    existing_contact = Contact.query.filter(Contact.id == id).one_or_none()
    if existing_contact is not None:
        return contact_schema.dump(existing_contact), 200
    else:
        abort(404, f"Contact id {id} not found")

def read_email(email):
    """ API endpoint: """
    contacts = Contact.query.filter(Contact.email == email).all()
    if contacts is not None:
        return contacts_schema.dump(contacts), 200
    else:
        abort(404, f"Contact email {email} not found")

def create(contact):
    """ API endpoint: """
    name = contact.get("name")
    surname = contact.get("surname")
    email = contact.get("email")
    tenant = contact.get("tenant")

    existing_contact = Contact.query.filter(Contact.email == email,
                                            Contact.tenant == tenant).one_or_none()
    if existing_contact is None:
        new_contact = contact_schema.load(contact, session=db.session)
        db.session.add(new_contact)
        db.session.commit()
        return contact_schema.dump(new_contact), 201
    else:
        abort(406, f"Contact {name} {email} for tenant id {tenant} already exists")

def delete(id):
    """ API endpoint: """
    existing_contact = Contact.query.filter(Contact.id == id).one_or_none()
    if existing_contact:
        db.session.delete(existing_contact)
        db.session.commit()
        return make_response(f"Contact {id} successfully deleted", 202)
    else:
        abort(404, f"Contact id {id} not found")

def delete_email(email):
    """ API endpoint: """
    existing_contacts = Contact.query.filter(Contact.email == email).all()
    if existing_contacts:
        for existing_contact in existing_contacts:
            db.session.delete(existing_contact)
        db.session.commit()
        return make_response(f"Contact {email} successfully deleted", 202)
    else:
        abort(404, f"Contact email {email} not found")

def list_tenant_email(email):
    """ API endpoint: """
    contacts = Contact.query.filter(Contact.email == email).all()
    tenants = []
    if contacts:
        for contact in contacts:
            if contact.tenant not in tenants:
                tenants.append(contact.tenant)
    return (jsonify(tenants)), 200

def read_tenant(id):
    """ API endpoint: """
    tenant = Tenant.query.filter(Tenant.id == id).one_or_none()
    if tenant is not None:
        contacts = Contact.query.join(Tenant,
                                   Tenant.id == Contact.tenant).add_columns(Contact.id,
                                                                    Contact.name,
                                                                    Contact.surname,
                                                                    Contact.email,
                                                                    Contact.created_on,
                                                                    Contact.updated_on).filter(
                                                                        Tenant.id == id) #.all()
        if contacts is not None:
            return contacts_schema.dump(contacts), 200
        else:
            abort(500, f"Error on Tenant id {id}")
    else:
        abort(404, f"Tenant id {id} not found")

def list_tenant(id):
    """ API endpoint: """
    tenant = Tenant.query.filter(Tenant.id == id).one_or_none()
    if tenant is not None:
        tenants = []
        contacts = Contact.query.join(Tenant,
                                   Tenant.id == Contact.tenant).add_columns(Contact.id).filter(
                                                                        Tenant.id == id) #.all()
        if contacts is not None:
            for contact in contacts:
                if contact.id not in tenants:
                    tenants.append(contact.id)
            return (jsonify(tenants)), 200
        else:
            abort(500, f"Error on Tenant id {id}")
    else:
        abort(404, f"Tenant id {id} not found")

def list_env(id):
    """ API endpoint: """
    id_list = []
    tenants = Tenant.query.join(Environment,
                                Environment.id == Tenant.env).add_columns(Tenant.id).filter(Tenant.env == id) #.all()
    if tenants is not None:
        for tenant in tenants:
            contacts = Contact.query.join(Tenant,
                                   Tenant.id == Contact.tenant).add_columns(Contact.id).filter(Tenant.id == f"{tenant.id}")
            if contacts is not None:
                for contact in contacts:
                    if contact.id not in id_list:
                        id_list.append(contact.id)
        return (jsonify(id_list)), 200
    else:
        abort(404, f"Environment id {id} not found")

def read_env(id):
    """ API endpoint: """
    contact_list = []
    tenants = Tenant.query.join(Environment,
                                Environment.id == Tenant.env).add_columns(Tenant.id).filter(Tenant.env == id) #.all()
    if tenants is not None:
        for tenant in tenants:
            contacts = Contact.query.join(Tenant,
                                   Tenant.id == Contact.tenant).add_columns(Contact.id,
                                                                    Contact.name,
                                                                    Contact.surname,
                                                                    Contact.email,
                                                                    Contact.tenant,
                                                                    Contact.created_on,
                                                                    Contact.updated_on).filter(Tenant.id == f"{tenant.id}")
            if contacts is not None:
                for contact in contacts:
                    if contact not in contact_list:
                        contact_list.append(contact)
        return contacts_schema.dump(contact_list), 200
    else:
        abort(404, f"Environment id {id} not found")

def list_env_email(id):
    """ API endpoint: """
    emails = []
    tenants = Tenant.query.join(Environment,
                                Environment.id == Tenant.env).add_columns(Tenant.id).filter(Tenant.env == id) #.all()
    if tenants is not None:
        for tenant in tenants:
            contacts = Contact.query.join(Tenant,
                                   Tenant.id == Contact.tenant).add_columns(Contact.id,
                                                                    Contact.name,
                                                                    Contact.surname,
                                                                    Contact.email,
                                                                    Contact.tenant,
                                                                    Contact.created_on,
                                                                    Contact.updated_on).filter(Tenant.id == f"{tenant.id}")
            if contacts is not None:
                for contact in contacts:
                    if contact.email not in emails:
                        emails.append(contact.email)
        return (jsonify(emails)), 200
    else:
        abort(404, f"Environment id {id} not found")