# project/main/views.py


#################
#### imports ####
#################

from flask import render_template, Blueprint, redirect, url_for
from flask_login import login_required, current_user

################
#### config ####
################

main_blueprint = Blueprint('main', __name__,)


################
#### routes ####
################

@login_required
@main_blueprint.route('/index')
def index():
    return render_template('user/index.html')

@main_blueprint.route('/')
def home():
	if current_user.is_authenticated():
		return redirect(url_for('main.index'))
	return render_template('main/home.html')


@main_blueprint.route("/about/")
def about():
    return render_template("main/about.html")
