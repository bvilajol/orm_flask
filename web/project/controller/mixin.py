import json

from project.config import db

from project.model.db import Network
from project.model.db import Contact
from project.model.db import Tenant
from project.model.db import Environment

class BaseMixin:
    pass

class TenantMixin(BaseMixin):

    def __init__(self):
        super().__init__()

    def _to_dict(self):
        return self._traverse_dict(self.__dict__)

    def _to_json(self):
        return json.dumps(self._dict())

    def _traverse_dict(self, attributes):
        result = {}
        for key, value in attributes.items():
            result[key] = self._traverse(key, value)

        return result

    def _traverse(self, key, value):
        if isinstance(value, DictMixin):
            return value._to_dict()
        elif isinstance(value, dict):
            return self._traverse_dict(value)
        elif isinstance(value, list):
            return [self._traverse(key, v) for v in value]
        elif hasattr(value, '__dict__'):
            return self._traverse_dict(value.__dict__)
        else:
            return value

    def create(self, obj_dict):
        if isinstance(obj_dict, Network):
            existing = Network.query.filter(Network.name == obj_dict.get("name"),
                                            Network.subnet == obj_dict.get("subnet"),
                                            Network.tenant_id == obj_dict.get("tenant_id")).first()
            if existing is None:
                new = network_schema.load(obj_dict, session=db.session)
        elif isinstance(obj_dict, Contact):
            existing = Contact.query.filter(Contact.email == obj_dict.get("email"),
                                            Contact.tenant_id == obj_dict.get("tenant_id")).first()
            if existing_contact is None:
                new = contact_schema.load(obj_dict, session=db.session)
        elif isinstance(obj_dict, Tenant):
            existing = Tenant.query.filter(Tenant.name == obj_dict.get("name"),
                                           Tenant.env_id == obj_dict.get("env_id")).first()
            if existing is None:
                new = tenant_schema.load(obj_dict, session=db.session)
        elif isinstance(obj_dict, Environment):
            existing = Environment.query.filter(Environment.name == obj_dict.get("name"),
                                                Environment.fmg_name == obj_dict.get("fmg_name"),
                                                Environment.faz_name == obj_dict.get("faz_name"),
                                                Environment.az_keyvault == obj_dict.get("az_keyvault"),
                                                Environment.fmg_keyvault == obj_dict.get("fmg_keyvault")).first()
            if existing is None:
                new = environment_schema.load(obj_dict, session=db.session)
        else:
            pass
        if new:
            db.session.add(new)
            db.session.commit()
            return new._to_json()
        return False

    def delete(self, id):
        if isinstance(self, Network):
            existing = Network.query.filter(Network.id == id).first()
        elif isinstance(self, Contact):
            existing = Contact.query.filter(Contact.id == id).first()
        elif isinstance(self, Tenant):
            existing = Tenant.query.filter(Tenant.id == id).first()
        elif isinstance(self, Environment):
            existing = Environment.query.filter(Environment.id == id).first()
        else:
            pass
        if existing:
            db.session.delete(existing)
            db.session.commit()
            return existing._to_json()
        return False