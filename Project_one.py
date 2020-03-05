from flask import Flask, render_template, redirect, request, url_for, render_template_string, session, flash
from flask_wtf import FlaskForm, Form
from wtforms import Form, StringField, PasswordField, validators
from wtforms.validators import IPAddress, InputRequired, EqualTo, Regexp
from builtins import KeyError
from functools import wraps
from Back_end import *
from ftth_block_user_server_side import *
from ldap3.core.exceptions import LDAPBindError

from ldap3 import Server, Connection, ALL





app = Flask (__name__)
app.config['SECRET_KEY']='Networking Secret Key'


class loginform(FlaskForm):
    username=StringField('Username', [InputRequired()], description='Username')
    password=PasswordField('Password', [InputRequired(), validators.EqualTo('password', message='Passwords must match')])

class ipaddress(FlaskForm):
    ipaddress= StringField('IP Address', validators= [InputRequired(), IPAddress() , Regexp("(^(10).((25[0-5]|2[0-4][0-9])\.)((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.)(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$)" , message="Enter the Correct Format.Ex :10.2XX.X.X")])

class macaddress(FlaskForm):
    macaddress= StringField('MAC Address', validators=[InputRequired()])

class networking():

    #Enroute Login
    @app.route("/")
    def open():
       return redirect(url_for("login"))

    #Login Page
    @app.route('/login', methods=['GET','POST'])
    def login():
        form = loginform()
        try:
            if form.validate_on_submit():
                session["username"]=form.username.data
                session["password"]=form.password.data
                if demo_backend.establish_connection(form.username.data, form.password.data):
                    session['logged_in'] = True
                    flash("Login Successful")
                else:
                    return redirect(url_for("login"))
                return render_template("1.html")
            return render_template('login.html', form=form)
        except LDAPBindError:
            flash("Incorrect Username and Password")
            return redirect(url_for("login"))


    #@app.errorhandler(Exception)
    #def all_exception_handler(error):
    #  return redirect(url_for("login"))

    #Login_Required Wrap
    def is_logged_in(f):
        @wraps(f)
        def wrap(*args,**kwargs):
            if 'logged_in' in session:
                return f(*args,**kwargs)
            else:
                flash("Unauthorized Access. Please Log in")
                return redirect(url_for("login"))
        return wrap

    #Options Page
    @app.route("/1")
    @is_logged_in
    def options():
        try:
            session['home'] = True
            return render_template('1.html')
        except KeyError:
            return redirect(url_for("login"))

    # Blocking URL
    @app.route("/block", methods=['GET', 'POST'])
    @is_logged_in
    def block():
        try:
            ip = ipaddress()
            session['home'] = False
            username = session.get("username", None)
            password = session.get("password", None)

            if ip.validate_on_submit():
                session["ipaddress"] = ip.ipaddress.data
                mac, switchip, vlanid = demo_backend.blocking_ip()
                session["mac"] = mac
                session["switchip"] = switchip
                session["vlanid"] = vlanid
                return redirect(url_for("confirm"))
                # return render_template("confirm.html",mac=mac,switchip=switchip,vlanid=vlanid)
                # demo_backend.save_summary(ipaddress, username)

            return render_template("block.html", ip=ip)
        except KeyError:
            return redirect(url_for("login"))

    @app.route("/confirm", methods=['GET', 'POST'])
    @is_logged_in
    def confirm():
        username = session.get("username", None)
        ipaddress = session.get("ipaddress", None)
        mac = session.get("mac", None)
        switchip = session.get("switchip", None)
        vlanid = session.get("vlanid", None)
        return render_template("confirm.html", mac=mac, switchip=switchip, vlanid=vlanid)

    @app.route("/save_summary")
    @is_logged_in
    def save_summary():
        username = session.get("username", None)
        ipaddress = session.get("ipaddress", None)
        mac = session.get("mac", None)
        switchip = session.get("switchip", None)
        vlanid = session.get("vlanid", None)
        demo_backend.save_summary(ipaddress, username, mac, switchip, vlanid)
        flash("User is now Blocked")
        return redirect(url_for("options"))


    #Unblocking IP Address
    @app.route("/unblock",methods=['GET', 'POST'])
    @is_logged_in
    def unblock():
        try:
            mac=macaddress()
            session['home'] = False
            if mac.validate_on_submit():
                session["mac"] = mac.macaddress.data
                demo_backend.unblockingip(mac.macaddress.data)
                return redirect(url_for("options"))
            return render_template('unblock.html', mac=mac)
        except KeyError:
            return redirect(url_for("login"))

    @app.route("/macconfirm", methods=['GET', 'POST'])
    @is_logged_in
    def macconfirm():
        username = session.get("username", None)
        data = session.get("data", None)
        session['home'] = False
        return render_template("macconfirm.html")


    #Logout
    @app.route("/logout")
    @is_logged_in
    def logout():
        session.clear()
        flash("You are now logged out")
        return redirect(url_for('login'))

if __name__ == "__main__":
    app.run(debug=True, port=4000)