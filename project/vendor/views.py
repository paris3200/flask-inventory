# project/vendor/views.py

#################
#### imports ####
#################

from flask import render_template, Blueprint, url_for, \
    redirect, flash, request
from flask.ext.login import login_required

from project import db
from project.models import Vendor
from project.vendor.forms import RegisterForm

################
#### config ####
################

vendor_blueprint = Blueprint('vendor', __name__,)


################
#### routes ####
################

@vendor_blueprint.route('/vendor/register', methods=['GET', 'POST'])
@login_required
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        vendor = Vendor.query.filter_by(name=form.company_name.data).first()
        if vendor is None:
            vendor = Vendor(name=form.company_name.data,
                            contact=form.contact.data,
                            phone=form.phone.data, website=form.website.data,
                            line1=form.line1.data, line2=form.line2.data,
                            city=form.city.data, state=form.state.data,
                            zipcode=form.zipcode.data)
            db.session.add(vendor)
            db.session.commit()

            flash('New Vendor Added', 'success')
            return redirect(url_for('vendor.view'))
        else:
            flash('Vendor already exist')
            return redirect(url_for('vendor.register'))

    return render_template('vendor/register.html', form=form)

@vendor_blueprint.route('/vendor/view', methods=['GET', 'POST'])
@login_required
def view():
    vendors = Vendor.query.all()
    return render_template('/vendor/view_all.html', entries=vendors)

