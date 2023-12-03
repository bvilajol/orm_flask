from sqlalchemy import UniqueConstraint
from sqlalchemy.orm import backref
from sqlalchemy.sql import func

from project.config import db

from project.model.mixins import (  EnvironmentMixin, ZoneMixin, ZonePolicyMixin,
                                    TenantNetworkObjectMixin, TenantFqdnObjectMixin,
                                    ContactMixin, NetworkMixin, TenantMixin,)

class Zone(ZoneMixin, db.Model):
    """ Object to model a Zone """

    __table_args__ = (
        UniqueConstraint('name', 'env_id', name='zone_object__uk'),
    )

    env_id = db.Column(db.Integer,
                       db.ForeignKey('environment.id', ondelete='CASCADE'), nullable=False)

    policies = db.relationship('ZonePolicy',
                               primaryjoin = 'or_(Zone.id==ZonePolicy.tx_id, ' 'Zone.id==ZonePolicy.rx_id)',
                               lazy = 'joined',
                               backref = 'policies',
                               cascade = 'all,delete',
                               passive_deletes = True)

    fqdn_objects = db.relationship('TenantFqdnObject',
                                   lazy='joined',
                                   backref='fqdn_objects',
                                   cascade='all,delete',
                                   passive_deletes=True)

    network_objects = db.relationship('TenantNetworkObject',
                                   lazy='joined',
                                   backref='network_objects',
                                   cascade='all,delete',
                                   passive_deletes=True)

    def __repr__(self):
        """ Object representation """
        return 'Zone(name=%s)' % self.name

class ZonePolicy(ZonePolicyMixin, db.Model):
    """ Object to model a Zone Policy """

    __table_args__ = (
        UniqueConstraint('tx_id', 'rx_id', name='zone_policy_object__uk'),
    )

    tx_id = db.Column(db.Integer, 
                      db.ForeignKey('zone.id', ondelete='CASCADE'),
                      nullable=False)

    rx_id = db.Column(db.Integer,
                      db.ForeignKey('zone.id', ondelete='CASCADE'),
                      nullable=False)
    
    def __repr__(self):
        """ Object representation """
        return 'ZonePolicy(rx=%s, tx=%s)' % self.rx, self.tx

class Environment(EnvironmentMixin, db.Model):
    """ Object to model an Environment """

    __table_args__ = (
        UniqueConstraint('name', 'fmg_name', 'faz_name',
                         'az_keyvault', 'fmg_keyvault', name='env_object__uk'),
    )

    tenants = db.relationship('Tenant',
                              lazy='joined',
                              backref='tenants',
                              cascade='all,delete',
                              passive_deletes=True)

    zones = db.relationship('Zone',
                            lazy='joined',
                            backref='zones',
                            cascade='all,delete',
                            passive_deletes=True)

    def __repr__(self):
        """ Object representation """
        return 'Environment(name=%s)' % self.name

class Contact(ContactMixin, db.Model):
    """ Object to model a Contact """

    __table_args__ = (
        UniqueConstraint('email', 'tenant_id', name='contact_object_uk'),
    )

    tenant_id = db.Column(db.Integer,
                          db.ForeignKey('tenant.id', ondelete='CASCADE'),
                          nullable=False)

    def __repr__(self):
        """ Object representation """
        return 'Contact(name=%s)' % self.name

class Network(NetworkMixin, db.Model):
    """ Object to model a Network """

    __table_args__ = (
        UniqueConstraint('name', 'subnet', 'tenant_id', name='network_object_uk'),
    )

    tenant_id = db.Column(db.Integer,
                          db.ForeignKey('tenant.id', ondelete='CASCADE'),
                          nullable=False)

    def __repr__(self):
        """ Object representation """
        return 'Network(name=%s)' % self.name

class TenantNetworkObject(TenantNetworkObjectMixin, db.Model):
    """ Object to model a Zone Object Group """

    __table_args__ = (
        UniqueConstraint('code', 'zone_id', 'tenant_id', name='zoned_network_object__uk'),
    )

    zone_id = db.Column(db.Integer,
                        db.ForeignKey('zone.id', ondelete='CASCADE'),
                        nullable=False)

    tenant_id = db.Column(db.Integer,
                          db.ForeignKey('tenant.id', ondelete='CASCADE'),
                          nullable=True)

    def __repr__(self):
        """ Object representation """
        return 'ZonedNetworkObject(subnet=%s)' % self.subnet

class TenantFqdnObject(TenantFqdnObjectMixin, db.Model):
    """ Object to model a Zone Object Group """

    __table_args__ = (
        UniqueConstraint('code', 'zone_id', 'tenant_id', name='zoned_fqdn_object__uk'),
    )

    zone_id = db.Column(db.Integer,
                        db.ForeignKey('zone.id', ondelete='CASCADE'),
                        nullable=False)

    tenant_id = db.Column(db.Integer,
                          db.ForeignKey('tenant.id', ondelete='CASCADE'),
                          nullable=True)

    def __repr__(self):
        """ Object representation """
        return 'ZonedFqdnObject(fqdn=%s)' % self.fqdn

class Tenant(TenantMixin, db.Model):
    """ Object to model a Tenant """

    __table_args__ = (
        UniqueConstraint('name', 'env_id', name='tenant_object__uk'),
    )

    env_id = db.Column(db.Integer,
                       db.ForeignKey('environment.id', ondelete='CASCADE'),
                       nullable=False)

    users = db.relationship('Contact',
                            lazy='joined',
                            backref='users',
                            cascade='all,delete',
                            passive_deletes=True)

    networks = db.relationship('Network',
                               lazy='joined',
                               backref='networks',
                               cascade='all,delete',
                               passive_deletes=True)

    """fqdn_objects = db.relationship('TenantFqdnObject',
                                   lazy='joined',
                                   backref='fqdn_objects',
                                   cascade='all,delete',
                                   passive_deletes=True)

    network_objects = db.relationship('TenantNetworkObject',
                                      lazy='joined',
                                      backref='network_objects',
                                      cascade='all,delete',
                                      passive_deletes=True)"""

    def __repr__(self):
        """ Object representation """
        return 'Tenant(name=%s)' % self.name