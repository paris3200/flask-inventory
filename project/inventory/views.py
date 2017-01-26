# project/vendor/views.py

#################
#    imports    #
#################
import datetime
from flask import render_template, Blueprint, url_for, \
    redirect, flash, request
from flask_login import login_required

from project import db
from project.models import Vendor, PurchaseOrder, LineItem, Component, Address, \
    Transaction, TagCategory, Tag
from project.inventory.forms import VendorCreateForm, PurchaseOrderForm, \
    ComponentCreateForm, TransactionForm, TagForm

################
#    config    #
################

inventory_blueprint = Blueprint('inventory',
                                __name__,
                                template_folder='templates')


################
#    routes    #
################

@inventory_blueprint.route('/transactions/', methods=['GET'])
@login_required
def transactions():
    transactions = Transaction.query.all()
    return render_template("/transaction/transactions.html", transactions=transactions)

@inventory_blueprint.route('/transactions/check-in', methods=['GET','POST'])
@login_required
def checkin():
    form = TransactionForm(request.form)
    form.component.choices = [(x.id, x.description) for x in Component.query.all()]
    if form.validate_on_submit():
        nt = Transaction()
        form.component.data = Component.query.get(form.component.data)
        form.populate_obj(nt)
        nt.date_create = datetime.datetime.now()
        if form.checkout.data:
            nt.qty = form.qty.data * -1
        db.session.add(nt)
        db.session.commit()
        flash('Success: Items Checked In')
        return redirect(url_for('main.home'))
    return render_template("/transaction/make.html", form=form, the_action="checkin")

@inventory_blueprint.route('/transactions/check-out', methods=['GET','POST'])
@login_required
def checkout():
    form = TransactionForm(request.form)
    form.component.choices = [(x.id, x.description) for x in Component.query.all()]
    if form.validate_on_submit():
        nt = Transaction()
        form.component.data = Component.query.get(form.component.data)
        form.populate_obj(nt)
        nt.date_create = datetime.datetime.now()
        if form.checkout.data:
            nt.qty = form.qty.data * -1
        db.session.add(nt)
        db.session.commit()
        flash('Success: Items Checked Out')
        return redirect(url_for('main.home'))
    return render_template("/transaction/make.html", form=form, the_action="checkout")

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
        address = Address.query.filter_by(line1=form.line1.data).first()
        with db.session.no_autoflush:
            if address is None:
                address = Address(line1=form.line1.data, line2=form.line2.data,
                                  city=form.city.data, state=form.state.data,
                                  zipcode=form.zipcode.data)
                db.session.add(address)
            if vendor is None:
                vendor = Vendor(name=form.name.data,
                                contact=form.contact.data,
                                phone=form.phone.data,
                                website=form.website.data,
                                address=address)
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
    form.component.choices = [(x.id, x.description) for x in Component.query.all()]
    if form.validate_on_submit():
        with db.session.no_autoflush:
            order = PurchaseOrder()
            order.created_on = datetime.date.today()
            order.vendor = vendor
            db.session.add(order)
            component = Component.query.filter_by(
                sku=form.sku.data).first()
            if component:
                line1 = LineItem(component=component,
                                 quantity=form.quantity.data,
                                 total_price=form.total_price.data)
                order.line_item.append(line1)
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

@inventory_blueprint.route('/manage-tags', methods=['GET','POST'])
def manage_tags():
    form = TagForm(request.form)
    if form.validate_on_submit():
        cat = form.category.data.strip().upper()
        tag = form.tag_name.data.strip().upper()
        cat_obj = TagCategory.query.filter_by(name=cat).first()
        tag_obj = Tag.query.filter_by(name=tag).first()
        if not cat_obj and cat:
            cat_obj = TagCategory(cat)
            db.session.add(cat_obj)
            flash('Category %s Created' % cat)
        if not tag_obj:
            tag_obj = Tag(tag)
            flash('Tag %s Created' % tag)
            db.session.add(tag_obj)
        db.session.commit()
        if cat_obj and tag_obj not in cat_obj.tags:
            cat_obj.tags.append(tag_obj)
        db.session.commit()
    categories = TagCategory.query.all()
    uncategorized_tags = Tag.query.filter(Tag.categories == None).all()
    print(uncategorized_tags)
    print(Tag.query.all())

    return render_template("/tags/tag-manager.html",
        categories=categories, uncategorized_tags = uncategorized_tags, form=form)

@inventory_blueprint.route('/tag-component/<int:component_id>', methods=['GET', 'POST'])
def tag_component(component_id=None):
    form = TagForm(request.form)
    the_component = Component.query.get_or_404(component_id)
    if form.validate_on_submit():
        cat = form.category.data.strip().upper()
        tag = form.tag_name.data.strip().upper()
        cat_obj = TagCategory.query.filter_by(name=cat).first()
        tag_obj = Tag.query.filter_by(name=tag).first()
        if cat and not cat_obj:
            cat_obj = TagCategory(cat)
            db.session.add(cat_obj)
        if not tag_obj:
            tag_obj = Tag(tag)
            db.session.add(tag_obj)
        db.session.commit()
        if cat_obj and tag_obj not in cat_obj.tags:
            cat_obj.tags.append(tag_obj)
        if tag_obj not in the_component.tags:
            the_component.tags.append(tag_obj)
        db.session.commit()
        flash("%s (%s) has been tagged with %s" % (the_component.description, the_component.sku, tag_obj.name))
        return redirect(url_for('inventory.view_component', component_id=component_id))
    categories = TagCategory.query.all()
    tags = Tag.query.all()
    return render_template("/component/tag-component.html", result=the_component, form=form,
        categories=categories, tags=tags)
