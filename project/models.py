# project/models.py


import datetime
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.sql.functions import sum


from project import db, bcrypt

class Base(db.Model):
    __abstract__ = True
    id              = db.Column(db.Integer, primary_key=True)
    date_create     = db.Column(db.DateTime, default=db.func.current_timestamp())
    date_modified   = db.Column(db.DateTime, default=db.func.current_timestamp(),
                                            onupdate = db.func.current_timestamp()) 

class User(db.Model):

    __tablename__ = "user"

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

    @hybrid_property
    def sub_total(self):
        price = 0
        for line in self.line_items:
            price += line.total_price
        return price

    @hybrid_property
    def total(self):
        return self.sub_total+self.shipping+self.tax

    def as_dict(self):
       return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    def __repr__(self):
        return dir(self)


class LineItem(db.Model):
    __tablename__ = "line_item"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    quantity = db.Column(db.Integer, nullable=False)
    total_price = db.Column(db.Numeric(12, 2), nullable=False)

    purchase_order_id = db.Column(db.Integer,
                                  db.ForeignKey('purchase_order.id'),
                                  nullable=False)

    component_id = db.Column(db.Integer,
                             db.ForeignKey('component.id'),
                             nullable=False)

    purchase_order = db.relationship("PurchaseOrder", backref='line_item',
                                     lazy="joined")
    component = db.relationship("Component", uselist=False)

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
    
    @hybrid_property
    def qty(self):
        # the_query = Transaction.filter(Transaction.component_id == self.id)
        # qty_available = the_query.with_entities(sum(Transaction.qty).label('available')).first()
        qty_available = [ x.qty for x in self.transactions]
        s = 0
        for i in qty_available:
            s += i
        return s

class Transaction(Base):
    __tablename__ = "transaction"
    component_id = db.Column(db.Integer, db.ForeignKey('component.id'),
                          nullable=False)
    component = db.relationship("Component", backref="transactions")
    qty = db.Column(db.Integer, nullable=False)



