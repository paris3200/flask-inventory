from flask import Blueprint
from flask_restful import Resource, Api, reqparse, marshal_with
from flask_login import login_required
from ..models import db, Component, Tag, components_tags, TagCategory
from .marshals import *

api_module = Blueprint('api', __name__,  url_prefix = '/api')
api = Api(api_module)

parser = reqparse.RequestParser(bundle_errors = True)
parser.add_argument('sku', type=str, location='json')
parser.add_argument('description', type=str, location='json')

class ComponentsAPI(Resource):
	decorators = [login_required]
	@marshal_with(item)
	def get(self,component_id=None):
		if component_id:
			return Component.query.get(component_id)
		else:
			return Component.query.all()
	@marshal_with(item)
	def put(self,component_id):
		component = Component.query.get(component_id)
		if not component:
			return 404
		args = parser.parse_args()
		clashing_component = Component.query.filter(
			Component.sku == args.get('sku'),
			Component.id  != int(component_id)).first()
		print('\n\tSKU: ',args.get('sku'))
		print(clashing_component)
		if args.get('sku') and not clashing_component:
			component.sku = args.get('sku')
		if args.get('description'):
			component.description = args.get('description')
		db.session.commit()
		return component

class SingleTagsAPI(Resource):
	decorators = [login_required]
	@marshal_with(tag)
	def get(self):
		tags = Tag.query.filter(Tag.categories == None).all()
		for t in tags:
			setattr(t,'__repr__',str(t))
		return tags
	

class TagAPI(Resource):
	decorators = [login_required]
	def delete(self, tag_id):
		tag = Tag.query.get(tag_id)
		if tag:
			tag_id = tag.id
			db.session.delete(tag)
			db.session.commit()
			return tag_id
		return ([],404)


class CategoriesAPI(Resource):
	decorators = [login_required]
	@marshal_with(category)
	def get(self):
		cats = TagCategory.query.all()
		for c in cats:
			setattr(c,'__repr__',c)
		return cats


api.add_resource(ComponentsAPI, '/components','/components/<int:component_id>')
api.add_resource(SingleTagsAPI, '/single-tags')
api.add_resource(CategoriesAPI, '/categories')
api.add_resource(TagAPI, '/tag/<int:tag_id>')
