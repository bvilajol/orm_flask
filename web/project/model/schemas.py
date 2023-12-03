from flask_marshmallow import Marshmallow
from marshmallow import Schema, fields, post_load, pre_load, pre_dump, post_dump

from marshmallow_oneofschema import OneOfSchema

from project.config import db, ma
from project.model.db import (  Contact,
                                Tenant,
                                Environment,
                                Network,
                                Zone,
                                ZonePolicy,
                                TenantNetworkObject,
                                TenantFqdnObject,
                                )
class ZonePolicySchema(ma.SQLAlchemyAutoSchema):
    """ Schema object to model a ZonePolicy """
    class Meta:
        model = ZonePolicy
        load_instance = True
        include_fk = True
        sqla_session = db.session

    created_on = ma.DateTime(dump_only=True)
    updated_on = ma.DateTime(dump_only=True)
    type_field = ma.String(required=True, dump_only=True, dump_default="ZonePolicy")

""" Instances for ZonePolicySchema object """
zone_policy_schema = ZonePolicySchema()
zone_policies_schema = ZonePolicySchema(many=True)

class TenantNetworkObjectSchema(ma.SQLAlchemyAutoSchema):
    """ Schema object to model a ZonedNetworkObjectS """
    class Meta:
        model = TenantNetworkObject
        load_instance = True
        include_fk = True
        sqla_session = db.session

    created_on = ma.DateTime(dump_only=True)
    updated_on = ma.DateTime(dump_only=True)
    type_field = ma.String(required=True, dump_only=True, dump_default="TenantNetworkObject")

""" Instances for ZonedObjectSchema object """
tenant_network_object_schema = TenantNetworkObjectSchema()
tenant_network_objects_schema = TenantNetworkObjectSchema(many=True)

class TenantFqdnObjectSchema(ma.SQLAlchemyAutoSchema):
    """ Schema object to model a TenantFqdnObject """
    class Meta:
        model = TenantFqdnObject
        load_instance = True
        include_fk = True
        sqla_session = db.session

    created_on = ma.DateTime(dump_only=True)
    updated_on = ma.DateTime(dump_only=True)
    type_field = ma.String(required=True, dump_only=True, dump_default="TenantFqdnObject")

""" Instances for TenantFqdnObject object """
tenant_fqdn_object_schema = TenantFqdnObjectSchema()
tenant_fqdn_objects_schema = TenantFqdnObjectSchema(many=True)

class TenantObjectSchema(OneOfSchema):
    type_schemas = {    "TenantNetworkObject": TenantNetworkObjectSchema,
                        "TenantFqdnObject": TenantFqdnObjectSchema,}

    def get_obj_type(self, obj):
        if isinstance(obj, ZonedFqdnObjectSchema):
            return "ZonedFqdnObject"
        elif isinstance(obj, ZonedNetworkObjectSchema):
            return "ZonedNetworkObject"
        else:
            raise Exception("Unknown object type: {}".format(obj.__class__.__name__))

tenant_objects_schema = TenantObjectSchema(many=True)

class ZoneSchema(ma.SQLAlchemyAutoSchema):
    """ Schema object to model a Zone """
    class Meta:
        model = Zone
        load_instance = True
        include_fk = True
        sqla_session = db.session

    policies = ma.Nested(ZonePolicySchema, many=True)
    network_objects = ma.Nested(TenantNetworkObjectSchema, many=True)
    fqdn_objects = ma.Nested(TenantFqdnObjectSchema, many=True)
    created_on = ma.DateTime(dump_only=True)
    updated_on = ma.DateTime(dump_only=True)
    type_field = ma.String(required=True, dump_only=True, dump_default="Zone")

""" Instances for ZoneSchema object """
zone_schema = ZoneSchema()
zones_schema = ZoneSchema(many=True)

class ContactSchema(ma.SQLAlchemyAutoSchema):
    """ Schema object to model a Contact """
    class Meta:
        model = Contact
        load_instance = True
        include_fk = True
        sqla_session = db.session

    created_on = ma.DateTime(dump_only=True)
    updated_on = ma.DateTime(dump_only=True)
    type_field = ma.String(required=True, dump_only=True, dump_default="Contact")

""" Instances for ContactSchema object """
contact_schema = ContactSchema()
contacts_schema = ContactSchema(many=True)

class NetworkSchema(ma.SQLAlchemyAutoSchema):
    """ Schema object to model an Environment """
    class Meta:
        model = Network
        load_instance = True
        include_fk = True
        sqla_session = db.session

    id = ma.Integer(dump_only=True)
    created_on = ma.DateTime(dump_only=True)
    updated_on = ma.DateTime(dump_only=True)
    type_field = ma.String(required=True, dump_only=True, dump_default="Network")

""" Instances for NetworkSchema( object """
network_schema = NetworkSchema()
networks_schema = NetworkSchema(many=True)
class TenantSchema(ma.SQLAlchemyAutoSchema):
    """ Schema object to model a Tenant """
    class Meta:
        model = Tenant
        load_instance = True
        include_fk = True
        sqla_session = db.session

    networks = ma.Nested(NetworkSchema, many=True)
    users = ma.Nested(ContactSchema, many=True)
    #network_objects = ma.Nested(TenantNetworkObjectSchema, many=True)
    #fqdn_objects = ma.Nested(TenantFqdnObjectSchema, many=True)
    #objects = ma.Nested(TenantObjectSchema, many=True)
    created_on = ma.DateTime(dump_only=True)
    updated_on = ma.DateTime(dump_only=True)
    type_field = ma.String(required=True, dump_only=True, dump_default="Tenant")

""" Instances for TenantSchema object """
tenant_schema = TenantSchema()
tenants_schema = TenantSchema(many=True)

class EnvironmentSchema(ma.SQLAlchemyAutoSchema):
    """ Schema object to model an Environment """
    class Meta:
        model = Environment
        load_instance = True
        include_fk = True
        sqla_session = db.session

    id = ma.Integer(dump_only=True)
    tenants = ma.Nested(TenantSchema, many=True)
    zones = ma.Nested(ZoneSchema, many=True)
    #network_objects = ma.Nested(TenantNetworkObjectSchema, many=True)
    #fqdn_objects = ma.Nested(TenantFqdnObjectSchema, many=True)
    created_on = ma.DateTime(dump_only=True)
    updated_on = ma.DateTime(dump_only=True)
    type_field = ma.String(required=True, dump_only=True, dump_default="Environment")

""" Instances for EnvironmentSchema object """
environment_schema = EnvironmentSchema()
environments_schema = EnvironmentSchema(many=True)