# Flask ORM Template

  * Template for an ORM Python Application.
  * Data model implemented using 8 tables and several mixins.
  * SQLALchemy is used towards the postgreeSQL relational database.
  * Swagger and Connexion are used for the REST API application.
  * The Bootstrap CSS based Web UI uses Flask-Marshmallow and Flask-SQLAlchemy libraries.
  * Flask WTF is used for some of the forms.
  * Marshmallow OneOfSchema is used for some models shemas (work in progress)
  * Gunicorn as selected WSGI application server for the web docker image.
  * Nginx as selected proxy server for web the docker image.
  * Pgadmin image is included for the development docker-compose file.

# Contents

- [Model](#model)
- [Local development](#local-development)
- [Docker image](#docker-image)

## Model

This section shows the complete code for one of the objects within the ORM, Tenant:

Mixins are used towards SQLAlchemy as per implementing class heritance and mixin.

    class TimeColumns(object):
         """ Class to model common columns for DB Tables """
         created_on = db.Column(db.DateTime(), server_default=func.now())
         updated_on = db.Column(db.DateTime(), onupdate=func.now())

    class TableMixin(TimeColumns):
         """ Mixin class to model a DB Table """
         @declared_attr
         def __tablename__(cls):
             if has_inherited_table(cls):
                 return None
             return cls.__name__.lower()
         id = db.Column(db.Integer, primary_key=True)
   
    class TenantMixin(TableMixin):
        """ Class to model a Tenant DB Table mixin """
        name = db.Column(db.String(4), nullable=False)
        name_long = db.Column(db.String(64), nullable=True)

SQLAlchemy classes to define a DB table include only the relational side for the model.

    class Tenant(TenantMixin, db.Model):
        """ Class to model Tenant into DB """
        __table_args__ = (
         UniqueConstraint('name', 'env_id', name='tenant_object__uk'),
        )
        env_id = db.Column(db.Integer, db.ForeignKey('environment.id', ondelete='CASCADE'), nullable=False)
        users = db.relationship('Contact', lazy='joined', backref='users', cascade='all,delete', passive_deletes=True)
        networks = db.relationship('Network', lazy='joined', backref='networks', cascade='all,delete', passive_deletes=True)

Schema classes to model I/O from DB include defined data into the serialization for the object.

    class TenantSchema(ma.SQLAlchemyAutoSchema):
         """ Schema class to model a Tenant I/O from DB """
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

Singletron instances exist for the (de)serialization for the objects.

     """ Instances for TenantSchema object """
     tenant_schema = TenantSchema()
     tenants_schema = TenantSchema(many=True)

Example JSON for Tenant

     {
       "id": 1,
       "env_id": 1,
       "type_field": "Tenant",
       "name": "VRF1",
       "name_long": "PCI DSS Network",
       "created_on": "2023-12-03T15:24:04.345556",
       "updated_on": "2023-12-03T15:25:04.345556",
       "networks": [
         {
              "id": 1,
              "tenant_id": 1,
              "type_field": "Network",
              "name": "GLOBAL",
              "site": null,
              "subnet": "10.12.0.0/16",
              "created_on": "2023-12-03T15:24:04.345556",
              "updated_on": "2023-12-03T15:25:04.345556"
         },
         {
              "id": 2,
              "tenant_id": 1,
              "type_field": "Network",
              "name": "DC01",
              "site": null,
              "subnet": "10.12.128.0/22",
              "created_on": "2023-12-03T15:24:04.345556",
              "updated_on": "2023-12-03T15:25:04.345556"
         },
               ...
       ],
       "users": [
         {
              "created_on": "2023-12-03T15:24:04.345556",
              "updated_on": null,
              "id": 8,
              "email": "carla.pota@acme.nl",
              "name": "Carla",
              "surname": "Pota",
              "tenant_id": 1,
              "type_field": "Contact"
           
         },
         {
              "created_on": "2023-12-03T15:24:04.345556",
              "updated_on": null,
              "id": 5,
              "email": "pere.samfaina@acme.nl",
              "name": "Pere",
              "surname": "Samfaina",
              "tenant_id": 1,
              "type_field": "Contact"
              
          },
               ...
       ]
     }

## Local development

For the development image, web server to serve the API is meant to run locally. Export the following environment variables,

    $ source dev.env

    export DB_NAME=tenants_db
    export DB_DRIVER=postgresql
    export DB_USER=admin
    export DB_PASSWORD=admin
    export DB_HOST=localhost
    export FLASK_APP=project.app.py

before starting the application.

    $ docker-compose -f docker-compose.dev.yml build
    $ docker-compose -f docker-compose.dev.yml up
    [$ docker-compose -f docker-compose.dev.yml down]

    [+] Running 4/4
    ✔ Volume "tests_orm_dev_db_orm"  Created
    ✔ Volume "tests_orm_dev_pg_orm"  Created
    ✔ Container dev_pgadmin          Created
    ✔ Container dev_db               Created

Once that, commands to operate the application are located on manage.py file:

    $ python3 manage.py create_db
    $ python3 manage.py seed_db
    $ python3 manage.py run

## Docker image

For the production-called image, web server docker is launched to serve the application.
    
    $ docker-compose -f docker-compose.yml build    
    $ docker-compose -f docker-compose.yml up
    [$ docker-compose -f docker-compose.yml down]

On first run, create and seed the database as well.

    $ docker ps

    CONTAINER ID   IMAGE             COMMAND
    a3894acd0797   tests_orm-nginx   "/docker-entryp...
    89f61d60501f   tests_orm-web     "/home/app/web/...
    304459caf481   postgres:13       "docker-entrypo...

    $ docker exec -it 89f61d60501f bash

    app@89f61d60501f:~/web$ python3 manage.py create_db
    app@89f61d60501f:~/web$ python3 manage.py seed_db
    app@89f61d60501f:~/web$ exit
