from flask_restful import fields
tag = {
	'id' : fields.String,
	'name' : fields.String,
}

item = {
	'id': fields.String,
	'sku' : fields.String,
	'description' : fields.String,
	'tags' : fields.Nested(tag),
}