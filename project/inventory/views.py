# project/vendor/views.py

#################
#    imports    #
#################
import datetime
from flask import render_template, Blueprint, url_for, \
    redirect, flash, request

from flask.views import View

from flask_login import login_required

from project import db
from project.models import Vendor, PurchaseOrder, LineItem, Component, Address,\
    Transaction, TagCategory, Tag, VendorComponent, TagManager
from project.inventory.forms import VendorCreateForm, PurchaseOrderForm, \
    ComponentCreateForm, TransactionForm, TagForm

################
#    config    #
################

inventory_blueprint = Blueprint('inventory',
                                __name__,
                                template_folder='templates')

################
#    views     #
################


class TransactionMakerView(View):
    methods = ["GET", "POST"]
    decorators = [login_required]

    def __init__(self, action_type):
        self.action_type = action_type

    def get_template_name(self):
        return '/transaction/make.html'

    def render_template(self, context):
        return render_template(self.get_template_name(), ** context)

    def dispatch_request(self):
        form = TransactionForm(request.form)
        form.component.choices = [(x.id, x.description)
                                  for x in Component.query.all()]
        if form.validate_on_submit():
            nt = Transaction()
            form.component.data = Component.query.get(form.component.data)
            nt.date_create = datetime.datetime.now()
            if request.form.get("checkout"):
                void = form.qty.data * (-1)
                if form.component.data.qty + void >= 0:
                    form.populate_obj(nt)
                    nt.component_id = form.component.data.id
                    nt.qty = void
                    db.session.add(nt)
                    db.session.commit()
                    flash('Success: Items Checked Out')
                else:
                    flash("Not enough items, only %s available" %
                          (form.component.data.qty))
                    form.component.data = form.component.data.id
                    return render_template("/transaction/make.html", form=form, the_action=self.action_type)
            elif request.form.get("checkin"):
                form.populate_obj(nt)
                nt.component_id = form.component.data.id
                nt.qty = form.qty.data
                db.session.add(nt)
                db.session.commit()
                flash('Success: %s Checked In' %
                      ("Items" if nt.qty > 1 else "Item"))
            return redirect(url_for('main.home'))
        return render_template("/transaction/make.html",
                               form=form, the_action=self.action_type)

################
#    routes    #
################
@inventory_blueprint.route('/transactions/', methods=['GET'])
@login_required
def transactions():
    page = request.args.get("page", 1)
    if page==u"":
        page=1
    else:
        page = int(page)
    period = request.args.get("period", None)
    search = request.args.get("search")
    query = Transaction.query.order_by(Transaction.date_create.desc())
    if search and search !="":
        period="all"
        query = query.filter(Transaction.notes.contains(search))
    if period == 'ten_days':
        period_date = datetime.datetime.now()
        time_delta = datetime.timedelta(days=-10)
        period_date = period_date + time_delta
        query = query.filter(Transaction.date_create > period_date)
    elif period == 'today':
        period_date = datetime.datetime.now()
        period_date = period_date.replace(hour=0, minute=0)
        query = query.filter(Transaction.date_create > period_date)
    elif period == 'month':
        period_date = datetime.date.today()
        period_date = period_date.replace(day=1)
        period_date = datetime.datetime.combine(period_date, datetime.datetime.min.time())
        query = query.filter(Transaction.date_create > period_date)
    transactions = query.paginate(page, per_page=20, error_out=True)
    return render_template("/transaction/transactions.html",
                           transactions=transactions, page=page, period=period, search=search)


inventory_blueprint.add_url_rule(
    '/transactions/check-in',
    view_func=TransactionMakerView.as_view('checkin', action_type='checkin'))
inventory_blueprint.add_url_rule(
    '/transactions/check-out',
    view_func=TransactionMakerView.as_view('checkout', action_type='checkout'))


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
    choices = [(x.id, x.description) for x in Component.query.all()]
    form.component.choices = choices if choices else [(0, 'None')]
    if form.validate_on_submit():
        with db.session.no_autoflush:
            order = PurchaseOrder()
            order.created_on = datetime.date.today()
            order.vendor = vendor
            order.user_id = form.user_id.data
            db.session.add(order)
            component = VendorComponent.query.filter_by(
                sku=form.sku.data).first()
            if component:
                line1 = LineItem(vendor_component=component,
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


@inventory_blueprint.route('/vendor/<int:vendor_id>/component/create',
                           methods=['GET', 'POST'])
@login_required
def create_vendor_component(vendor_id):
    vendor = Vendor.query.get_or_404(vendor_id)
    form = ComponentCreateForm()
    if form.validate_on_submit():
        component = VendorComponent.query.filter_by(sku=form.sku.data).first()
        if component is None:
            component = VendorComponent(sku=form.sku.data,
                                        description=form.description.data,
                                        vendor=vendor)
            db.session.add(component)
            db.session.commit()
            flash('New Component Added', 'success')
            return redirect(url_for('.view_vendor_component',
                                    vendor_id=vendor_id))
        else:
            flash('Component already exists.')
            return redirect(url_for('.create_vendor_component',
                                    vendor_id=vendor_id))
    return render_template('/vendor_component/create.html', form=form)


@inventory_blueprint.route('/vendor/<int:vendor_id>/component/',
                           methods=['GET'])
@login_required
def view_vendor_component(vendor_id, component_id=None):
    vendor = Vendor.query.get_or_404(vendor_id)
    component = VendorComponent.query.filter_by(vendor=vendor)
    return render_template('/vendor_component/view_all.html', result=component)


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


@inventory_blueprint.route('/manage-tags', methods=['GET', 'POST'])
def manage_tags():
    form = TagForm(request.form)
    if form.validate_on_submit():
        # returns tag object (new or existing). returns None if invalid params
        new_tag = TagManager.new_tag(form.tag_name.data, form.category.data)
        if new_tag:
            flash('Tag "%s" was Created' % new_tag)
        else:
            flash('Tag could not be created')
    categories = TagCategory.query.all()
    uncategorized_tags = Tag.query.filter(Tag.categories is None).all()
    return render_template("/tags/tag-manager.html",
                           categories=categories,
                           uncategorized_tags=uncategorized_tags,
                           form=form)


@inventory_blueprint.route('/tag-component/<int:component_id>',
                           methods=['GET', 'POST'])
def tag_component(component_id=None):
    form = TagForm(request.form)
    the_component = Component.query.get_or_404(component_id)
    if form.validate_on_submit():
        tag_obj = the_component.tag_with(form.tag_name.data, form.category.data)
        if tag_obj:
            flash("%s (%s) has been tagged with %s" %
              (the_component.description, the_component.sku, tag_obj.name))
        else:
            flash("There was an error tagging the component")
        return redirect(url_for('inventory.view_component',
                                component_id=component_id))
    categories = TagCategory.query.all()
    tags = Tag.query.all()
    return render_template("/component/tag-component.html",
                           result=the_component, form=form,
                           categories=categories, tags=tags)
