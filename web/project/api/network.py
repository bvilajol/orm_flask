import json
from flask import abort, make_response, jsonify

from project.config import db

from project.model.db import Network, Tenant
from project.model.schemas import network_schema, networks_schema

""" Controller Methods for Network """

def read_all():
    """ API endpoint:  """

    networks = Network.query.all()
    return networks_schema.dump(networks)

def read(id):
    """ API endpoint:  """
    network = Network.query.filter(Network.id == id).one_or_none()
    if network is not None:
        return network_schema.dump(network)
    else:
        abort(404, f"Network {id} not found")

def read_tenant(id):
    """ API endpoint: """
    tenant = Tenant.query.filter(Tenant.id == id).one_or_none()
    if tenant is not None:
        networks = Network.query.join(Tenant,
                                   Tenant.id == Network.tenant).add_columns(Network.id,
                                                                            Network.name,
                                                                            Network.subnet,
                                                                            Network.created_on,
                                                                            Network.updated_on).filter(
                                                                                Tenant.id == id) #.all()
        if networks is not None:
            return networks_schema.dump(networks), 200
        else:
            abort(500, f"Error on Tenant id {id}")
    else:
        abort(404, f"Tenant id {id} not found")

def list_tenant(id):
    """ API endpoint: """
    tenant = Tenant.query.filter(Tenant.id == id).one_or_none()
    if tenant is not None:
        network_list = []
        networks = Network.query.join(Tenant,
                                   Tenant.id == Network.tenant).add_columns(Network.id,
                                                                            Network.name,
                                                                            Network.subnet,
                                                                            Network.created_on,
                                                                            Network.updated_on).filter(
                                                                                Tenant.id == id) #.all()
        if networks is not None:
            for network in networks:
                if network.id not in networks:
                    network_list.append(network.id)
            return (jsonify(network_list)), 200
        else:
            abort(500, f"Error on Tenant id {id}")
    else:
        abort(404, f"Tenant id {id} not found")

def create(network):
    """ API endpoint: """
    name = network.get("name")
    subnet = network.get("subnet")
    tenant = network.get("tenant")
    existing = Network.query.filter(Network.name == name,
                                    Network.subnet == subnet,
                                    Network.tenant == tenant).one_or_none()
    if existing is None:
        new = network_schema.load(network, session=db.session)
        db.session.add(new)
        db.session.commit()
        return network_schema.dump(new), 201
    else:
        abort(406, f"Network {name} - {network} in tenant {tenant} already exists")

def delete(id):
    """ API endpoint:  """
    existing = Network.query.filter(Network.id == id).one_or_none()
    if existing:
        db.session.delete(existing)
        db.session.commit()
        return make_response(f"Network {id} successfully deleted", 202)
    else:
        abort(404, f"Network id {id} not found")