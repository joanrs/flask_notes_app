from flask import Flask
from extensions import db
import os
# Import models to ensure tables are registered
import models

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'empty_notes.db')

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_PATH}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize DB with this app
db.init_app(app)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        print(f'Created {DB_PATH} with schema (no data).')
