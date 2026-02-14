# helpers.py
from models import Category
from flask import current_app
import os

def categories_to_dict():
    """
    Convierte todas las categorías a diccionarios para serialización JSON
    """
    categories = Category.query.all()
    return [{'id': cat.id, 'name': cat.name, 'color': cat.color} for cat in categories]

def category_to_dict(category):
    """
    Convierte una sola categoría a diccionario
    """
    if not category:
        return None
    return {
        'id': category.id,
        'name': category.name,
        'color': category.color
    }

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

def create_uploads_folder():
    if not os.path.exists(current_app.config['UPLOAD_FOLDER']):
        os.makedirs(current_app.config['UPLOAD_FOLDER'])