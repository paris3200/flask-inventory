# app/__init__.py


#################
#### imports ####
#################

import os

from flask import Flask, render_template
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from flask_debugtoolbar import DebugToolbarExtension
from flask_bootstrap import Bootstrap

bcrypt = Bcrypt()
from models import db


################
#### config ####
################

def create_app():
	app = Flask(__name__)
	app.config.from_object(os.environ['APP_SETTINGS'])


	####################
	#### extensions ####
	####################

	login_manager = LoginManager()
	login_manager.init_app(app)
	bcrypt.init_app(app)
	toolbar = DebugToolbarExtension(app)
	bootstrap = Bootstrap(app)
	db.init_app(app)


	###################
	### blueprints ####
	###################

	from mod_main.views import main_blueprint
	from mod_user.views import user_blueprint
	from mod_inventory.views import inventory_blueprint
	from mod_api.resources import api_module

	app.register_blueprint(user_blueprint)
	app.register_blueprint(main_blueprint)
	app.register_blueprint(inventory_blueprint)
	app.register_blueprint(api_module)


	###################
	### flask-login ####
	###################

	from models import User

	login_manager.login_view = "user.login"
	login_manager.login_message_category = 'danger'


	@login_manager.user_loader
	def load_user(user_id):
	    return User.query.filter(User.id == int(user_id)).first()


	########################
	#### error handlers ####
	########################

	@app.errorhandler(403)
	def forbidden_page(error):
	    return render_template("errors/403.html"), 403


	@app.errorhandler(404)
	def page_not_found(error):
	    return render_template("errors/404.html"), 404


	@app.errorhandler(500)
	def server_error_page(error):
	    return render_template("errors/500.html"), 500

	return app
