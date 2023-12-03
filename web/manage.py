import logging

from flask.cli import FlaskGroup

from project.config import db
from project.app import app

from project.model.db import (  Zone,
                                ZonePolicy,
                                Tenant,
                                Contact,
                                Environment,
                                Network,
                                TenantFqdnObject,
                                TenantNetworkObject,
                                )

cli = FlaskGroup(app)

def load_objects(file):
    import yaml
    from pathlib import Path
    input = yaml.safe_load(Path(file).read_text())
    mapping = { 'Environment': Environment,
                'Tenant': Tenant,
                'Contact': Contact,
                'Network': Network,
                'Zone': Zone,
                'ZonePolicy': ZonePolicy,
                'TenantFqdnObject': TenantFqdnObject,
                'TenantNetworkObject': TenantNetworkObject,}
    output = []
    for i in input.get("objects"):
        type_field = None
        attrs = {}
        for key,value in i.items():
            if not type_field: type_field = key
            else: attrs[key] = value
        if type_field and type_field in mapping.keys():
            obj = mapping[type_field](**attrs)
            output.append(obj)
    return output

@cli.command("create_db")
def create_db():
    db.drop_all()
    db.create_all()
    db.session.commit()

@cli.command("seed_db")
def seed_db():
    obj_list = load_objects(file='seed_db.yml')
    db.session.add_all(obj_list)
    db.session.commit()

@cli.command("seed_db_obj")
def test():
    obj_list = load_objects(file='seed_db_objects.yml')
    db.session.add_all(obj_list)
    db.session.commit()

if __name__ == "__main__":
    cli()