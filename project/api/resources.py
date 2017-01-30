from flask import Blueprint
from flask_restful import Resource, Api, reqparse, marshal_with
from flask_login import login_required
from ..models import Component, Tag, components_tags, TagCategory
from marshals import *

api_module = Blueprint('api', __name__,  url_prefix = '/api')
api = Api(api_module)

parser = reqparse.RequestParser(bundle_errors = True)

class ComponentsAPI(Resource):
	decorators = [login_required]
	@marshal_with(item)
	def get(self):
		return Component.query.all()

class SingleTagsAPI(Resource):
	decorators = [login_required]
	@marshal_with(tag)
	def get(self):
		print(TagCategory.query.all())
		print(Tag.query.all())
		return Tag.query.filter(Tag.categories == None).all()

class CategoriesAPI(Resource):
	decorators = [login_required]
	@marshal_with(category)
	def get(self):
		return TagCategory.query.all()


api.add_resource(ComponentsAPI, '/components')
api.add_resource(SingleTagsAPI, '/single-tags')
api.add_resource(CategoriesAPI, '/categories')