import os
from PIL import Image
from flask import Blueprint, current_app
from flask_restful import Resource, Api, reqparse, marshal_with
from flask_login import login_required
from ..models import db, Component, Tag, components_tags, TagCategory, Picture
from .marshals import *

from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename

api_module = Blueprint('api', __name__,  url_prefix = '/api')
api = Api(api_module)

parser = reqparse.RequestParser(bundle_errors = True)
parser.add_argument('sku', type=str, location='json')
parser.add_argument('description', type=str, location='json')

parser.add_argument('tag_text', type=str, location='json')
parser.add_argument('cat_text', type=str, location='json')

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

class ComponentTagsAPI(Resource):
	decorators = [login_required]
	@marshal_with(item)
	def delete(self, component_id, tag_id):
		comp = Component.query.get(component_id)
		tag = Tag.query.get(tag_id)
		comp.remove_tag(tag.name)
		return comp

	@marshal_with(item)
	def put(self,component_id,tag_id=None):
		comp = Component.query.get(component_id)
		args = parser.parse_args()
		tag_text = args.get('tag_text')
		cat_text = args.get('cat_text')
		if tag_text:
			comp.tag_with(tag_text, cat_text)
		if not comp:
			return 404
		return comp

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


class PicturesAPI(Resource):
	decorators = [login_required]
	
	parse = reqparse.RequestParser()
	parse.add_argument('picture_file', type=FileStorage, location='files')
	@marshal_with(picture)
	def get(self, component_id=None):
		if component_id:
			comp = Component.query.get(component_id)
			pictures = comp.pictures.all()
		else:
			pictures = Picture.query.all()
		# for t in tags:
		# 	setattr(t,'__repr__',str(t))
		return pictures
	
	@marshal_with(picture)
	def post(self, component_id=None):
		args = self.parse.parse_args()
		if component_id:
			comp = Component.query.get(component_id)
			print("args")
			print(args)
			if comp:
				picture = args['picture_file']
				if picture.filename:
					new_picture = Picture()
					filename = secure_filename(picture.filename)
					new_picture.filename = filename
					comp.pictures.append(new_picture)
					db.session.flush()
					new_picture.filename = str(new_picture.id).zfill(5)+new_picture.filename
					picture.save(os.path.join(current_app.config['PICTURES_FOLDER'], new_picture.filename))
					im = Image.open(os.path.join(current_app.config['PICTURES_FOLDER'], new_picture.filename))
					# if image is square and greater than 900
					if im.size[0] == im.size[1] and im.size[0] > 900:
						im.reize(900,900)
						im.save(os.path.join(current_app.config['PICTURES_FOLDER'], new_picture.filename))
					# if height > 900
					elif im.size[1] > 900:
						# get percentage coefficient
						coeff = float(900) / float(im.size[1])
						x, y  = int(float(im.size[0]) * float(coeff)), int(float(im.size[1]) * float(coeff))
						im = im.resize((x,y))
						im.save(os.path.join(current_app.config['PICTURES_FOLDER'], new_picture.filename))
					# Make thumbnail 
					coeff = float(200) / float(im.size[1])
					x, y  = int(float(im.size[0]) * float(coeff)), int(float(im.size[1]) * float(coeff))
					im = im.resize((x,y))
					im.save(os.path.join(current_app.config['PICTURES_FOLDER'], 'thumbnail_'+new_picture.filename))
					db.session.commit()
					return Picture.query.all()
		return []

	def delete(self, component_id, picture_id=None):
		comp = Component.query.get(component_id)
		if comp:
			the_picture = filter(lambda x: x.id == picture_id, comp.pictures)[0]
			print(the_picture)
			print(comp.pictures)
			comp.pictures.remove(the_picture)
			db.session.commit()
			return the_picture.id
		return ([],404)

	def put(self,component_id, picture_id):
		comp = Component.query.get(component_id)
		pic = Picture.query.get(picture_id)
		if not comp or not pic:
			return 404
		comp.pictures.append(pic)
		db.session.commit()
		return ([], 200)

api.add_resource(ComponentsAPI, '/components','/components/<int:component_id>')
api.add_resource(ComponentTagsAPI, '/component-tags/<int:component_id>', '/component-tags/<int:component_id>/<int:tag_id>')
# api.add_resource(ComponentTagsAPI, '/component-tags/<int:component_id>/<int:tag_id>')
api.add_resource(SingleTagsAPI, '/single-tags')
api.add_resource(CategoriesAPI, '/categories')
api.add_resource(TagAPI, '/tag/<int:tag_id>')

# pictures
api.add_resource(PicturesAPI, '/pictures',
	'/pictures/<int:component_id>',
	'/pictures/delete/<int:component_id>/<int:picture_id>',
	'/pictures/put/<int:component_id>/<int:picture_id>')
