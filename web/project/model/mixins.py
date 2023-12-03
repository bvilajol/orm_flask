from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.ext.declarative import has_inherited_table

from sqlalchemy.sql import func

from sqlalchemy import UniqueConstraint

from project.config import db

class TimeColumns(object):
    created_on = db.Column(db.DateTime(), server_default=func.now())
    updated_on = db.Column(db.DateTime(), onupdate=func.now())

class TableMixin(TimeColumns):
    @declared_attr
    def __tablename__(cls):
        if has_inherited_table(cls):
            return None
        return cls.__name__.lower()

    id = db.Column(db.Integer, primary_key=True)

class EnvironmentMixin(TableMixin):
    name = db.Column(db.String(24), unique=True, nullable=False)
    fmg_name = db.Column(db.String(16), nullable=False)
    faz_name = db.Column(db.String(16), nullable=False)
    az_keyvault = db.Column(db.String(16), nullable=False)
    fmg_keyvault = db.Column(db.String(16), nullable=False)

class TenantMixin(TableMixin):
    name = db.Column(db.String(4), nullable=False)
    name_long = db.Column(db.String(64), nullable=True)

class ZoneMixin(TableMixin):
    code = db.Column(db.String(5), nullable=False)
    name = db.Column(db.String(10), nullable=False)
    description = db.Column(db.String(128), nullable=True)

class ZonePolicyMixin(TableMixin):
    code = db.Column(db.Boolean(), nullable=False)
    description = db.Column(db.String(256), nullable=True)

class ContactMixin(TableMixin):
    name = db.Column(db.String(12), nullable=False)
    surname = db.Column(db.String(24))
    email = db.Column(db.String(32), nullable=False)

class NetworkMixin(TableMixin):
    name = db.Column(db.String(18), nullable=False)
    subnet = db.Column(db.String(32), nullable=False)
    site = db.Column(db.String(3), nullable=True)

class ZoneObjectMixin(TableMixin):
    code = db.Column(db.String(8), nullable=False)
    description = db.Column(db.String(128), nullable=True)
    color = db.Column(db.Integer(), nullable=True)

class TenantNetworkObjectMixin(ZoneObjectMixin):
    subnet = db.Column(db.String(32), nullable=False)

class TenantFqdnObjectMixin(ZoneObjectMixin):
    fqdn = db.Column(db.String(48), nullable=False)