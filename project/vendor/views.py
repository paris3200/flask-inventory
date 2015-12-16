# project/vendor/views.py

#################
#### imports ####
#################

from flask import render_template, Blueprint, url_for, \
    redirect, flash, request, jsonify
from flask.ext.login import login_required

from project import db
from project.models import Vendor, PurchaseOrder, LineItem, Component
from project.vendor.forms import RegisterForm, PurchaseOrderForm

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
        vendor = Vendor.query.filter_by(name=form.name.data).first()
        if vendor is None:
            vendor = Vendor(name=form.name.data,
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


@vendor_blueprint.route('/vendor/edit/<int:vendor_id>', methods=['GET', 'POST'])
@login_required
def edit(vendor_id):
    vendor = Vendor.query.get_or_404(vendor_id)
    form = RegisterForm(obj=vendor)
    if form.validate_on_submit():
        form.populate_obj(vendor)
        db.session.commit()

        flash('Vendor Updated', 'success')
        return redirect(url_for('vendor.view'))
    return render_template('vendor/edit.html', form=form)


@vendor_blueprint.route('/vendor/view', methods=['GET', 'POST'])
@login_required
def view():
    vendors = Vendor.query.all()
    return render_template('/vendor/view_all.html', entries=vendors)


@vendor_blueprint.route('/purchase_order/create/<int:vendor_id>',
                        methods=['GET', 'POST'])
@login_required
def purchase_order(vendor_id):
    vendor = Vendor.query.get_or_404(vendor_id)
    form = PurchaseOrderForm()
    if form.validate_on_submit():
        with db.session.no_autoflush:
            order = PurchaseOrder()
            order.vendor = vendor
            db.session.add(order)
            component = Component.query.get(int(form.item.data))
            line1 = LineItem(component=component,
                             quantity=form.quantity.data,
                             unit_price=form.unit_price.data)
            order.line_items.append(line1)
        db.session.commit()

        flash('Vendor Updated', 'success')
        return redirect(url_for('vendor.view_purchase_order'))
    return render_template('vendor/purchase_order.html', form=form)

@vendor_blueprint.route('/purchase_order/view/<int:po_id>',
                        methods=['GET', 'POST'])
@login_required
def view_purchase_order(po_id):
    po = PurchaseOrder.query.get_or_404(po_id)
    return render_template('/vendor/view_po.html', entries=po)

@vendor_blueprint.route('/vendor/search', methods=['GET'])
@login_required
def search():
    """ Doesn't work. """
    form_name = request.args.get('name')
    vendors = Vendor.query.filter(Vendor.name.like(form_name)).all()
    result = []
    for v in vendors:
        result.append(v.as_dict()['name'])
    return jsonify(name=result)
