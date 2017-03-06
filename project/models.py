# project/models.py


import datetime
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.sql.functions import sum

from project import db, bcrypt

tag_categories_tags = db.Table('tag_categories_tags',
                               db.Column('tag_category_id',
                                         db.Integer(),
                                         db.ForeignKey('tag_category.id')
                                         ),
                               db.Column('tag_id', db.Integer(),
                                         db.ForeignKey('tag.id')))

components_tags = db.Table('components_tags',
                           db.Column('component_id',
                                     db.Integer(),
                                     db.ForeignKey('component.id')),
                           db.Column('tag_id',
                                     db.Integer(),
                                     db.ForeignKey('tag.id')))


class Base(db.Model):
    __abstract__ = True
    id = db.Column(db.Integer, primary_key=True)
    date_create = db.Column(db.DateTime, default=db.func.current_timestamp())
    date_modified = db.Column(db.DateTime,
                              default=db.func.current_timestamp(),
                              onupdate=db.func.current_timestamp())


class User(db.Model):

    __tablename__ = "user"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    registered_on = db.Column(db.DateTime, nullable=False)
    admin = db.Column(db.Boolean, nullable=False, default=False)
    transactions = db.relationship('Transaction', backref='user',
                                   lazy='joined')
    purchase_orders = db.relationship('PurchaseOrder', backref='user',
                                   lazy='joined')

    def __init__(self, email, password, admin=False):
        self.email = email
        self.password = bcrypt.generate_password_hash(password)
        self.registered_on = datetime.datetime.now()
        self.admin = admin

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return self.id

    def __repr__(self):
        return '<User {0}>'.format(self.email)


class Vendor(db.Model):
    __tablename__ = "vendor"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(120), index=True, unique=True)
    contact = db.Column(db.String(120))
    phone = db.Column(db.String(15))
    website = db.Column(db.String(120))
    address_id = db.Column(db.Integer, db.ForeignKey('address.id'))

    def __repr__(self):
        return '<Vendor {0}>'.format(self.name)

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class Address(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    line1 = db.Column(db.String(120))
    line2 = db.Column(db.String(120))
    city = db.Column(db.String(120))
    state = db.Column(db.String(2))
    zipcode = db.Column(db.String(16))
    vendor = db.relationship("Vendor", backref='address')


class PurchaseOrder(db.Model):
    __tablename__ = "purchase_order"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    created_on = db.Column(db.DateTime, nullable=False)
    vendor_id = db.Column(db.Integer, db.ForeignKey('vendor.id'),
                          nullable=False)
    vendor = db.relationship('Vendor', backref="purchase_order",
                             lazy="joined")
    shipping = db.Column(db.Numeric(12, 2), nullable=False, default=0.00)
    tax = db.Column(db.Numeric(12, 2), nullable=False, default=0.00)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'),
                        nullable=False)

    @hybrid_property
    def sub_total(self):
        price = 0
        for line in self.line_item:
            price += line.total_price
        return price

    @hybrid_property
    def total(self):
        return self.sub_total + self.shipping + self.tax

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    def __repr__(self):
        return dir(self)


class VendorComponent(db.Model):
    __tablename__ = "vendor_component"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    sku = db.Column(db.String(5), unique=False, nullable=False)
    description = db.Column(db.String(), nullable=False)
    vendor =  db.relationship("Vendor", backref='vendor',
                                     lazy="joined")
    vendor_id = db.Column(db.Integer, db.ForeignKey('vendor.id'),
                          nullable=False)

class LineItem(db.Model):
    __tablename__ = "line_item"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    quantity = db.Column(db.Integer, nullable=False)
    total_price = db.Column(db.Numeric(12, 2), nullable=False)

    purchase_order_id = db.Column(db.Integer,
                                  db.ForeignKey('purchase_order.id'),
                                  nullable=False)

    vendor_component_id= db.Column(db.Integer,
                             db.ForeignKey('vendor_component.id'),
                             nullable=False)

    purchase_order = db.relationship("PurchaseOrder", backref='line_item',
                                     lazy="joined")
    vendor_component = db.relationship("VendorComponent", uselist=False)

    @hybrid_property
    def unit_price(self):
        return self.total_price / self.quantity

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class Component(db.Model):
    __tablename__ = "component"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    sku = db.Column(db.String(5), unique=True, nullable=False)
    description = db.Column(db.String(), nullable=False)
    tags = db.relationship("Tag",
                           secondary=components_tags,
                           backref='component')

    # @hybrid_property
    @property
    def qty(self):
        qty_available = [x.qty for x in self.transactions]
        s = 0
        for i in qty_available:
            s += i
        return s


class Transaction(Base):
    __tablename__ = "transaction"
    component_id = db.Column(db.Integer, db.ForeignKey('component.id'),
                             nullable=False)
    component = db.relationship("Component", backref="transactions")
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    notes = db.Column(db.String(40))
    qty = db.Column(db.Integer, nullable=False)


class TagCategory(db.Model):
    __tablename__ = "tag_category"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(25), unique=True, nullable=False)

    tags = db.relationship("Tag",
                           secondary=tag_categories_tags,
                           backref='categories')

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return "Category Name: %s, Tags: %s" % (self.name, str(
            0) if self.tags is None else ",".join([x.name for x in self.tags]))


class Tag(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(25), unique=True, nullable=False)

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return "%s in: %s" % (self.name, str(
            None) if self.categories is None else ",".join([x.name for x in self.categories]))
