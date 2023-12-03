import os
import sys

from flask import (
    #jsonify,
    send_from_directory,
    request,
    render_template,
    redirect,
    url_for,
)

from werkzeug.utils import secure_filename

"""
Web App project is to use the Model, not the
Controller available in the repository. The
controller is meant for the REST API App.
Note Controller returns http responses.
Import Model. """
from project.model.db import (  Network,
                                Contact,
                                Tenant,
                                Environment,
                                #Zone,
                                #ZonePolicy,
                                )

""" Import Schemas """
from project.model.schemas import ( network_schema,
                                    #networks_schema,
                                    contact_schema,
                                    #contacts_schema,
                                    tenant_schema,
                                    tenants_schema,
                                    environment_schema,
                                    environments_schema,
                                    #zones_schema,
                                    #zone_policies_schema,
                                    )

""" Import config and main instances """
import project.config
db = project.config.db
app = project.config.app
api = project.config.api

""" Add swagger definition to Conexion instance """
api.add_api(project.config.basedir / "api/swagger.yml")

""" Import Forms """
from project.controller.forms import EnvironmentForm, NetworkForm

@app.route('/api')
def ui():
    """ Renders Swagger UI
        -
        Returns: api.html
    """
    return render_template("api.html")

@app.route('/')
def home():
    """ Renders Tenants main view
        -
        Returns: environments.html
    """
    result = Tenant.query.all()
    tenants = tenants_schema.dump(result)
    return render_template("home.html", tenants=tenants)

@app.route('/environments', methods=["GET", "POST"])
def environments():
    """ Renders Environments main view. Methods: GET, POST

        'GET'
            Read all Environment objects from DB and render them alongside with Form.

        'POST':
            Validate Environment object is not existing.
            If Environment exists, redirect to 'GET' method.
            If Environment does not exists, create it and redirect to 'GET' method.
        -
        Returns: environments.html
    """
    env_form = EnvironmentForm()
    if env_form.validate_on_submit(): # Use of WTForms validate method
        name = request.form['name']                 # Name for the Environment
        fmg_name = request.form['fmg_name']         # FMG Name for the Environment
        faz_name = request.form['faz_name']         # FAZ Name for the Environment
        az_keyvault = request.form['az_keyvault']   # AZ Keyvault for the Environment
        fmg_keyvault = request.form['fmg_keyvault'] # FMG Keyvault for the Environment
        # Query the DB
        env = Environment.query.filter(Environment.name == name,
                                            Environment.fmg_name == fmg_name,
                                            Environment.faz_name == faz_name,
                                            Environment.az_keyvault == az_keyvault,
                                            Environment.fmg_keyvault == fmg_keyvault).first()
        # Create Environment into the DB
        if env is None:
            # Generate dict to create the Environment
            env_dict = { "name": name, "fmg_name": fmg_name, "faz_name": faz_name,
                        "az_keyvault": az_keyvault, "fmg_keyvault": fmg_keyvault }
            # Generate the Environment instance
            new = environment_schema.load(env_dict, session=db.session)
            # Add, commit and redirect to 'GET'
            db.session.add(new)
            db.session.commit()
        return redirect(url_for('environments'))
    else:
        envs = Environment.query.all()
        return render_template("environments.html", envs=envs, form=env_form)
    return redirect(url_for('home'))

@app.route('/environment/<id>')
def environment(id):
    """ Renders Environment details view
        -
        Returns: environment.html
    """
    result = Environment.query.filter(Environment.id == id).one_or_none()
    env = environment_schema.dump(result)
    if env:
        return render_template("environment.html", env=env)
    return redirect(url_for('environments'))

@app.route('/environment/<id>/remove', methods=["GET", "POST"])
def del_environment(id):
    """ Renders Environment remove confirmation view
        -
        Returns: remove_environment.html
                 redirect to environments if cancel
    """
    existing = Environment.query.filter(Environment.id == id).one_or_none()
    if existing:
        if request.method == "POST":
            db.session.delete(existing)
            db.session.commit()
            return redirect(url_for('environments'))
        else:
            return render_template("remove_environment.html", env=existing)
    return redirect(url_for('environments'))

@app.route('/tenant/<id>')
def tenant(id):
    """ Renders Tenant details view
        -
        Returns: tenant.html
    """
    existing = Tenant.query.filter(Tenant.id == id).first()
    if existing:
        env = Environment.query.filter(Environment.id == existing.env_id).first()
        return render_template("tenant.html", tenant=existing, env=env)
    return redirect(url_for('home'))

@app.route('/tenant/create', methods=["GET", "POST"])
def create():
    if request.method == "POST":
        name = request.form['name']
        name_long = request.form['name_long']
        env_id = int(request.form['env'])
        tenant_dict = { "name": name, "name_long": name_long, "env_id": env_id}
        existing = Tenant.query.filter(Tenant.name == name,
                                       Tenant.name_long == name_long,
                                       Tenant.env == env).one_or_none()
        if existing is None:
            new = tenant_schema.load(tenant_dict, session=db.session)
            db.session.add(new)
            db.session.commit()
            existing = Tenant.query.filter(Tenant.name == name,
                                           Tenant.name_long == name_long,
                                           Tenant.env_id == env_id).one_or_none()
            environment = Environment.query.filter(Environment.id == env_id).one_or_none()
            if existing and environment:
                return render_template("tenant.html", tenant=existing, env=environment)
        return redirect(url_for('home'))
    else:
        result = Environment.query.all()
        envs = environments_schema.dump(result)
        return render_template("create_tenant.html", envs=envs)

@app.route('/tenant/remove/<id>', methods=["GET", "POST"])
def del_tenant(id):
    """ Renders Tenant remove confirmation view
        -
        Returns: remove_tenant.html
                 redirect to home if cancel
    """
    existing = Tenant.query.filter(Tenant.id == id).one_or_none()
    if existing:
        if request.method == "POST":
            db.session.delete(existing)
            db.session.commit()
            return redirect(url_for('home'))
        else:
            return render_template("remove_tenant.html", tenant=existing)
    else:
        return redirect(url_for('home'))

@app.route('/contact/<id_tenant>', methods=["GET", "POST"])
def create_contact(id_tenant):
    try:
        tenant = Tenant.query.filter(Tenant.id == id_tenant).one_or_none()
        if tenant is not None:
            environment = Environment.query.filter(Environment.id == tenant.env_id).one_or_none()
            if environment is not None:
                if request.method == "POST":
                    name = request.form['name']
                    surname = request.form['surname']
                    email = request.form['email']
                    tenants = request.form.getlist('tenants') #list
                    for tenant in tenants:
                        existing = Contact.query.filter(Contact.name == name,
                                                        Contact.surname == surname,
                                                        Contact.email == email,
                                                        Contact.tenant_id == id_tenant).one_or_none()
                        if existing is None:
                            contact_dict = { "name": name, "surname": surname, "email": email, "tenant_id": id_tenant }
                            new = contact_schema.load(contact_dict, session=db.session)
                            db.session.add(new)
                            db.session.commit()
                    return redirect(url_for('tenant', id=id_tenant))
                else:
                    return render_template("create_contact.html",
                                            environment=environment,
                                            id_tenant=id_tenant)
            return redirect(url_for('tenant', id=id_tenant))
        return redirect(url_for('home'))
    except IndexError:
        return redirect(url_for('home'))

@app.route('/contact/remove/<id>', methods=["GET", "POST"])
def remove_contact(id):
    try:
        existing = Contact.query.filter(Contact.id == id).one_or_none()
        if existing is not None:
            if request.method == "POST":
                db.session.delete(existing)
                db.session.commit()
                return redirect(url_for('tenant', id=existing.tenant))
            else:
                return render_template("remove_contact.html", contact=existing)
        return redirect(url_for('home'))
    except IndexError:
        return redirect(url_for('home'))

@app.route('/network/<id_tenant>', methods=["GET", "POST"])
def create_network(id_tenant):
    try:
        existing = Tenant.query.filter(Tenant.id == id_tenant).one_or_none()
        if existing and request.method == "POST":
            name = request.form['name']
            subnet = request.form['subnet']
            tenant_id = existing.get("tenant_id")
            code_id = request.form['code_id']
            existing_net = Network.query.filter(Network.name == name,
                                                Network.subnet == subnet,
                                                Network.tenant_id == tenant_id,
                                                Network.code == code).one_or_none()
            if existing_net is None:
                net_dict = { "name": name, "subnet": subnet, "tenant_id": tenant_id, "code": code }
                new = network_schema.load(net_dict, session=db.session)
                db.session.add(new)
                db.session.commit()
            return redirect(url_for('tenant', id=id_tenant))
        elif existing:
            net_form = NetworkForm()
            tenant_env = Environment.query.filter(Environment.id == existing.env_id).one_or_none()
            return render_template("create_network.html", id_tenant=id_tenant, env=tenant_env, form=net_form)
        return redirect(url_for('home'))
    except IndexError:
        return redirect(url_for('home'))

@app.route('/network/remove/<id>', methods=["GET", "POST"])
def remove_network(id):
    try:
        existing = Network.query.filter(Network.id == id).one_or_none()
        if existing is not None:
            if request.method == "POST":
                db.session.delete(existing)
                db.session.commit()
                return redirect(url_for('tenant', id=existing.tenant))
            else:
                return render_template("remove_network.html", network=existing)
        return redirect(url_for('home'))
    except IndexError:
        return redirect(url_for('home'))

@app.route("/static/<path:filename>")
def staticfiles(filename):
    return send_from_directory(app.config["STATIC_FOLDER"], filename)

def run():
    app.run(host="0.0.0.0", port=5000, debug=True)

if __name__ == "__main__":
    run()