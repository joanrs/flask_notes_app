from app import app
from extensions import db
from models import Category

def seed_categories():
    categories = [
        {"name": "Programación", "color": "#3366ff", "icon": "fas fa-code"},
        {"name": "Diseño UI/UX", "color": "#ff33cc", "icon": "fas fa-paint-brush"},
        {"name": "Productividad", "color": "#00cc66", "icon": "fas fa-check-circle"},
        {"name": "Finanzas", "color": "#ffcc00", "icon": "fas fa-wallet"},
        {"name": "Estilo de Vida", "color": "#ff6600", "icon": "fas fa-heart"},
        {"name": "Tecnología", "color": "#6600ff", "icon": "fas fa-microchip"},
        {"name": "Ingeniería", "color": "#996633", "icon": "fas fa-cog"},
        {"name": "Idiomas", "color": "#ff9900", "icon": "fas fa-language"},
        {"name": "Viajes", "color": "#33cccc", "icon": "fas fa-plane"},
        {"name": "Salud y Deporte", "color": "#cc0000", "icon": "fas fa-running"},
        {"name": "Inteligencia Artificial", "color": "#003399", "icon": "fas fa-robot"},
        {"name": "Marketing Digital", "color": "#9900cc", "icon": "fas fa-bullhorn"},
        {"name": "Ciencia", "color": "#0099ff", "icon": "fas fa-flask"},
        {"name": "Negocios", "color": "#006600", "icon": "fas fa-briefcase"},
        {"name": "Desarrollo Personal", "color": "#ffcc99", "icon": "fas fa-user-graduate"},
        {"name": "Fotografía", "color": "#333333", "icon": "fas fa-camera"},
        {"name": "Música", "color": "#ff0066", "icon": "fas fa-music"},
        {"name": "Libros", "color": "#663300", "icon": "fas fa-book"},
        {"name": "Cine y Series", "color": "#e50914", "icon": "fas fa-film"},
        {"name": "Gastronomía", "color": "#ff9933", "icon": "fas fa-utensils"}
    ]

    with app.app_context():
        for cat_data in categories:
            # Only add if doesn't exist
            existing = Category.query.filter_by(name=cat_data["name"]).first()
            if not existing:
                cat = Category(**cat_data)
                db.session.add(cat)
            else:
                existing.color = cat_data["color"]
                existing.icon = cat_data["icon"]
        
        db.session.commit()
        print(f"Succefully seeded {len(categories)} categories.")

if __name__ == "__main__":
    seed_categories()
