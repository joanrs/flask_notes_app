from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_required, current_user
import os
from datetime import datetime
from flask_migrate import Migrate
from extensions import db, login_manager, migrate
from models import User, Category, Note, Attachment, Like, Comment, Badge
from blueprints import auth_bp, notes_bp, categories_bp, tasks_bp, calendar_bp, feed_bp, users_bp, social_bp
from helpers import create_uploads_folder

# Configuration
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here-change-in-production'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///notes.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif', 'pdf', 'txt', 'doc', 'docx'}
import re
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max upload

# Custom Jinja tests
app.jinja_env.tests['match'] = lambda s, p: bool(re.match(p, s)) if s else False

# Inicializar extensiones
db.init_app(app)
login_manager.init_app(app)
migrate.init_app(app, db)

login_manager.login_view = 'auth.login'

# Register user_loader directly in app.py
@login_manager.user_loader
def load_user(user_id):
    from models import User  # Importar aquí para evitar dependencias circulares
    return User.query.get(int(user_id))

# Register blueprints
app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(notes_bp)
app.register_blueprint(categories_bp)
app.register_blueprint(tasks_bp)
app.register_blueprint(calendar_bp)
app.register_blueprint(feed_bp)
app.register_blueprint(users_bp)
app.register_blueprint(social_bp)

# Root route (redirect to notes table)
@app.route('/')
@login_required
def index():
    return redirect(url_for('notes.notes_table'))

# Initialize app
if __name__ == '__main__':
    with app.app_context():
        create_uploads_folder()
        db.create_all()
        
        # Create default category if none exists
        if not Category.query.first():
            default_category = Category(name='General', color='#ffffff')
            db.session.add(default_category)
            db.session.commit()
    
    app.run(debug=True)