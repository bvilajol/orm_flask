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
from project.model.db import Network
from project.model.db import Contact
from project.model.db import Tenant
from project.model.db import Environment
from project.model.db import Zone, ZonePolicy

""" Import Schemas """
from project.model.schemas import (network_schema,
                                   networks_schema,
                                   contact_schema,
                                   contacts_schema,
                                   tenant_schema,
                                   tenants_schema,
                                   environment_schema,
                                   environments_schema,
                                   zones_schema,
                                   zone_policies_schema,
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

@app.route('/')
def home():
    result = Tenant.query.all()
    tenants = tenants_schema.dump(result)
    return render_template("home.html", tenants=tenants)

@app.route('/api')
def ui():
    return render_template("api.html")

@app.route('/environments', methods=["GET", "POST"])
def environments():
    #envs = Environment.query.all()
    if request.method == "POST":
        name = request.form['name']
        fmg_name = request.form['fmg_name']
        faz_name = request.form['fmg_name']
        az_keyvault = request.form['az_keyvault']
        fmg_keyvault = request.form['fmg_keyvault']
        env_dict = { "name": name,
                    "fmg_name": fmg_name,
                    "faz_name": faz_name,
                    "az_keyvault": az_keyvault,
                    "fmg_keyvault": fmg_keyvault}
        existing = Environment.query.filter(Environment.name == name,
                                            Environment.fmg_name == fmg_name,
                                            Environment.faz_name == faz_name,
                                            Environment.az_keyvault == az_keyvault,
                                            Environment.fmg_keyvault == fmg_keyvault).one_or_none()
        if existing is None:
            new = environment_schema.load(env_dict, session=db.session)
            db.session.add(new)
            db.session.commit()
        return redirect(url_for('environments'))
    else:
        result = Environment.query.all()
        #envs = environments_schema.dump(result)
        env_form = EnvironmentForm()
        return render_template("environments.html", envs=result, form=env_form, env=None)
    return redirect(url_for('home'))

@app.route('/environment/<id>/details', methods=["GET"])
def details_zone(id):
    try:
        result = Environment.query.filter(Environment.id == id).one_or_none()
        env = environment_schema.dump(result)
        if env:
            if request.method == "POST":
                return redirect(url_for('environments'))
            else:
                return render_template("zones.html", env=env)
        return redirect(url_for('environments'))
    except IndexError:
        return redirect(url_for('home'))

@app.route('/environment/remove/<id>', methods=["GET", "POST"])
def remove_env(id):
    try:
        existing = Environment.query.filter(Environment.id == id).one_or_none()
        if existing:
            if request.method == "POST":
                db.session.delete(existing)
                db.session.commit()
                return redirect(url_for('environments'))
            else:
                return render_template("remove_environment.html", env=existing)
        return redirect(url_for('environments'))
    except IndexError:
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

@app.route('/tenant/<id>')
def tenant(id):
    try:
        existing = Tenant.query.filter(Tenant.id == id).one_or_none()
        if existing is None:
            redirect(url_for('home'))
        else:
            environment = Environment.query.filter(Environment.id == existing.env_id).one_or_none()
            if environment:
                return render_template("tenant.html", tenant=existing, env=environment)
            return redirect(url_for('home'))
    except IndexError:
        return redirect(url_for('home'))

@app.route('/tenant/remove/<id>', methods=["GET", "POST"])
def remove_tenant(id):
    try:
        existing = Tenant.query.filter(Tenant.id == id).one_or_none()
        if existing:
            if request.method == "POST":
                db.session.delete(existing_tenant)
                db.session.commit()
                return redirect(url_for('home'))
            else:
                return render_template("remove_tenant.html", tenant=existing)
        else:
            return redirect(url_for('home'))
    except IndexError:
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