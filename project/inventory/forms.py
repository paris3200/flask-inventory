# project/vendor/forms.py


from flask_wtf import Form
from wtforms import TextField, SelectField, IntegerField
from wtforms.validators import DataRequired, URL, Optional

STATE_ABBREV = ('AL', 'AK', 'AZ', 'AR', 'CA', 'CO', 'CT', 'DE', 'FL', 'GA',
                'HI', 'ID', 'IL', 'IN', 'IO', 'KS', 'KY', 'LA', 'ME', 'MD',
                'MA', 'MI', 'MN', 'MS', 'MO', 'MT', 'NE', 'NV', 'NH', 'NJ',
                'NM', 'NY', 'NC', 'ND', 'OH', 'OK', 'OR', 'PA', 'RI', 'SC',
                'SD', 'TN', 'TX', 'UT', 'VT', 'VA', 'WA', 'WV', 'WI', 'WY')


class VendorCreateForm(Form):
    name = TextField('Company', validators=[DataRequired()])
    contact = TextField('Contact')
    line1 = TextField('Address 1')
    line2 = TextField('Address 2')
    line3 = TextField('Address 3')
    city = TextField('City')
    state = SelectField('State',
                        choices=[(state, state) for state in STATE_ABBREV])
    zipcode = TextField('Zipcode')
    phone = TextField('Phone')
    website = TextField('Website', validators=[Optional(strip_whitespace=True),
                                               URL(require_tld=True)])


class PurchaseOrderForm(Form):
    sku = TextField('SKU', validators=[DataRequired()])
    quantity = IntegerField('Quantity', validators=[DataRequired()])
    total_price = TextField('Total Item  Price', validators=[DataRequired()])


class ComponentCreateForm(Form):
    sku = TextField('Sku', validators=[DataRequired()])
    description = TextField('Description', validators=[DataRequired()])
