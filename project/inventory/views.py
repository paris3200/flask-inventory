# project/vendor/views.py

#################
#    imports    #
#################
import datetime
from flask import render_template, Blueprint, url_for, \
    redirect, flash
from flask.ext.login import login_required

from project import db
from project.models import Vendor, PurchaseOrder, LineItem, Component
from project.inventory.forms import VendorCreateForm, PurchaseOrderForm, \
    ComponentCreateForm

################
#    config    #
################

inventory_blueprint = Blueprint('inventory',
                                __name__,
                                template_folder='templates')


################
#    routes    #
################


################
#    Vendor    #
################


@inventory_blueprint.route('/vendor/<int:vendor_id>', methods=['GET'])
@inventory_blueprint.route('/vendor/', methods=['GET'])
@login_required
def view_vendor(vendor_id=None):
    if vendor_id:
        vendor = Vendor.query.get_or_404(vendor_id)
        orders = PurchaseOrder.query.filter_by(vendor_id=vendor.id)
        return render_template('vendor/view.html', vendor=vendor,
                               purchase_orders=orders)
    vendors = Vendor.query.all()
    return render_template('/vendor/view_all.html', entries=vendors)


@inventory_blueprint.route('/vendor/create', methods=['GET', 'POST'])
@login_required
def create_vendor():
    form = VendorCreateForm()
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
            return redirect(url_for('.view_vendor'))
        else:
            flash('Vendor already exist.')
            return redirect(url_for('.view_vendor'))
    return render_template('vendor/create.html', form=form)


@inventory_blueprint.route('/vendor/edit/<int:vendor_id>',
                           methods=['GET', 'POST'])
@login_required
def edit_vendor(vendor_id):
    vendor = Vendor.query.get_or_404(vendor_id)
    form = VendorCreateForm(obj=vendor)
    if form.validate_on_submit():
        form.populate_obj(vendor)
        db.session.commit()

        flash('Vendor Updated', 'success')
        return redirect(url_for('.view_vendor'))
    return render_template('vendor/edit.html', form=form)


#########################
#    Purchase Orders    #
#########################


@inventory_blueprint.route('/purchase_order/')
@inventory_blueprint.route('/purchase_order/<int:po_id>',
                           methods=['GET', 'POST'])
@login_required
def view_purchase_order(po_id=None):
    if po_id:
        order = PurchaseOrder.query.get_or_404(po_id)
        return render_template('/purchase_order/view.html',
                               result=order)
    purchase_orders = PurchaseOrder.query.all()
    return render_template('/purchase_order/view_all.html',
                           result=purchase_orders)


@inventory_blueprint.route('/purchase_order/create/<int:vendor_id>',
                           methods=['GET', 'POST'])
@login_required
def create_purchase_order(vendor_id):
    vendor = Vendor.query.get_or_404(vendor_id)
    form = PurchaseOrderForm()
    if form.validate_on_submit():
        with db.session.no_autoflush:
            order = PurchaseOrder()
            order.created_on = datetime.date.today()
            order.vendor = vendor
            db.session.add(order)
            component = Component.query.filter_by(
                id=int(form.item.data)).first()
            if component:
                line1 = LineItem(component=component,
                                 quantity=form.quantity.data,
                                 unit_price=form.unit_price.data)
                order.line_items.append(line1)
            else:
                flash('Component not found.')
                return render_template('/purchase_order/create.html',
                                       form=form,
                                       vendor=vendor)
        db.session.commit()
        flash('Purchase Order Added', 'success')
        return redirect(url_for('.view_purchase_order', po_id=order.id))
    return render_template('/purchase_order/create.html', form=form,
                           vendor=vendor)


@inventory_blueprint.route('/component/create', methods=['GET', 'POST'])
@login_required
def create_component():
    form = ComponentCreateForm()
    if form.validate_on_submit():
        component = Component.query.filter_by(sku=form.sku.data).first()
        if component is None:
            component = Component(sku=form.sku.data,
                                  description=form.description.data)
            db.session.add(component)
            db.session.commit()

            flash('New Component Added', 'success')
            return redirect(url_for('.view_component'))
        else:
            flash('Component already exist.')
            return redirect(url_for('.view_component'))
    return render_template('/component/create.html', form=form)


@inventory_blueprint.route('/component/<int:component_id>', methods=['GET'])
@inventory_blueprint.route('/component/', methods=['GET'])
@login_required
def view_component(component_id=None):
    if component_id:
        component = Component.query.get_or_404(component_id)
        return render_template('component/view.html', result=component)
    component = Component.query.all()
    return render_template('/component/view_all.html', result=component)
