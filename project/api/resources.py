from flask import Blueprint
from flask_restful import Resource, Api, reqparse, marshal_with
from ..models import Component, Tag, components_tags
from marshals import *

api_module = Blueprint('api', __name__,  url_prefix = '/api')
api = Api(api_module)

parser = reqparse.RequestParser(bundle_errors = True)

class ComponentsAPI(Resource):
	@marshal_with(item)
	def get(self):
		return Component.query.all()


api.add_resource(ComponentsAPI, '/components')