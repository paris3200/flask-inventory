# project/vendor/views.py

#################
#### imports ####
#################
import datetime
from flask import render_template, Blueprint, url_for, \
    redirect, flash, request, jsonify
from flask.ext.login import login_required

from project import db
from project.models import Vendor, PurchaseOrder, LineItem, Component
from project.inventory.forms import RegisterForm, PurchaseOrderForm

################
#### config ####
################

inventory_blueprint = Blueprint('inventory',
                                __name__,
                                template_folder='templates')


################
#### routes ####
################

@inventory_blueprint.route('/vendor/register', methods=['GET', 'POST'])
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
            return redirect(url_for('inventory.view'))
        else:
            flash('Vendor already exist')
            return redirect(url_for('inventory.register'))

    return render_template('vendor/register.html', form=form)


@inventory_blueprint.route('/vendor/edit/<int:vendor_id>',
                           methods=['GET', 'POST'])
@login_required
def edit(vendor_id):
    vendor = Vendor.query.get_or_404(vendor_id)
    form = RegisterForm(obj=vendor)
    if form.validate_on_submit():
        form.populate_obj(vendor)
        db.session.commit()

        flash('Vendor Updated', 'success')
        return redirect(url_for('inventory.view'))
    return render_template('inventory/edit.html', form=form)


@inventory_blueprint.route('/vendor/view/', methods=['GET'])
@login_required
def view():
    vendors = Vendor.query.all()
    return render_template('/vendor/view_all.html', entries=vendors)


@inventory_blueprint.route('/view/<int:vendor_id>', methods=['GET'])
@login_required
def view_vendor(vendor_id):
    vendor = Vendor.query.get_or_404(vendor_id)
    purchase_orders = PurchaseOrder.query.filter_by(vendor_id=vendor.id)
    return render_template('inventory/view_vendor.html', vendor=vendor,
                           purchase_orders = purchase_orders)

@inventory_blueprint.route('/purchase_order/create/<int:vendor_id>',
                        methods=['GET', 'POST'])
@login_required
def purchase_order(vendor_id):
    vendor = Vendor.query.get_or_404(vendor_id)
    form = PurchaseOrderForm()
    if form.validate_on_submit():
        with db.session.no_autoflush:
            order = PurchaseOrder()
            order.created_on = datetime.date.today()
            order.vendor = vendor
            db.session.add(order)
            component = Component.query.get(int(form.item.data))
            line1 = LineItem(component=component,
                             quantity=form.quantity.data,
                             unit_price=form.unit_price.data)
            order.line_items.append(line1)
        db.session.commit()

        flash('Purchase Order Added', 'success')
        return redirect(url_for('inventory.view_purchase_order', po_id=order.id))
    return render_template('inventory/purchase_order.html', form=form,
                           vendor=vendor)

@inventory_blueprint.route('/purchase_order/view/<int:po_id>',
                        methods=['GET', 'POST'])
@login_required
def view_purchase_order(po_id):
    po = PurchaseOrder.query.get_or_404(po_id)
    return render_template('/inventory/view_po.html', entries=po)

@inventory_blueprint.route('/vendor/search', methods=['GET'])
@login_required
def search():
    """ Doesn't work. """
    form_name = request.args.get('name')
    vendors = Vendor.query.filter(Vendor.name.like(form_name)).all()
    result = []
    for v in vendors:
        result.append(v.as_dict()['name'])
    return jsonify(name=result)
