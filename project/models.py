# project/models.py


import datetime
from sqlalchemy.ext.hybrid import hybrid_property

from project import db, bcrypt


class User(db.Model):

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    registered_on = db.Column(db.DateTime, nullable=False)
    admin = db.Column(db.Boolean, nullable=False, default=False)

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
    __tablename__ = "vendors"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(120), index=True, unique=True)
    contact = db.Column(db.String(120))
    phone = db.Column(db.String(15))
    website = db.Column(db.String(120))
    line1 = db.Column(db.String(120))
    line2 = db.Column(db.String(120))
    city = db.Column(db.String(120))
    state = db.Column(db.String(2))
    zipcode = db.Column(db.String(16))

    def __repr__(self):
        return '<Vendor {0}>'.format(self.name)

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class PurchaseOrder(db.Model):
    __tablename__ = "purchase_orders"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    vendor_id = db.Column(db.Integer, db.ForeignKey('vendors.id'),
                          nullable=False)
    created_on = db.Column(db.DateTime, nullable=False)

    vendor = db.relationship('Vendor', backref="purchase_orders",
                             lazy="dynamic", uselist=True)


class LineItem(db.Model):
    __tablename__ = "line_items"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    quantity = db.Column(db.Integer, nullable=False)
    unit_price = db.Column(db.Numeric(12, 2), nullable=False)
    purchase_order = db.Column(db.Integer,
                               db.ForeignKey('purchase_orders.id'),
                               nullable=False)
    component = db.Column(db.Integer,
                          db.ForeignKey('components.id'),
                          nullable=False)

    @hybrid_property
    def total_price(self):
        return self.quantity * self.unit_price

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class Component(db.Model):
    __tablename__ = "components"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(120), nullable=False)
