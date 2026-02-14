#!/usr/bin/env python3
"""
Script para inicializar las funcionalidades sociales
"""
from app import app
from extensions import db
from models import Badge, User, Category, Note

def init_badges():
    """Inicializar badges por defecto"""
    with app.app_context():
        default_badges = [
            {
                'name': 'Primer Paso',
                'description': 'Creaste tu primera nota',
                'requirement_type': 'notes_count',
                'requirement_value': 1,
                'icon': 'fas fa-baby',
                'color': '#28a745'
            },
            {
                'name': 'Escritor',
                'description': 'Has creado 5 notas',
                'requirement_type': 'notes_count',
                'requirement_value': 5,
                'icon': 'fas fa-pen',
                'color': '#007bff'
            },
            {
                'name': 'Autor Prolífico',
                'description': 'Has creado 20 notas',
                'requirement_type': 'notes_count',
                'requirement_value': 20,
                'icon': 'fas fa-book',
                'color': '#6f42c1'
            },
            {
                'name': 'Popular',
                'description': 'Has recibido 10 likes',
                'requirement_type': 'likes_received',
                'requirement_value': 10,
                'icon': 'fas fa-heart',
                'color': '#dc3545'
            },
            {
                'name': 'Estrella',
                'description': 'Has recibido 50 likes',
                'requirement_type': 'likes_received',
                'requirement_value': 50,
                'icon': 'fas fa-star',
                'color': '#ffc107'
            },
            {
                'name': 'Conversador',
                'description': 'Has hecho 10 comentarios',
                'requirement_type': 'comments_made',
                'requirement_value': 10,
                'icon': 'fas fa-comments',
                'color': '#17a2b8'
            },
            {
                'name': 'Influencer',
                'description': 'Tienes 5 seguidores',
                'requirement_type': 'followers_count',
                'requirement_value': 5,
                'icon': 'fas fa-users',
                'color': '#fd7e14'
            },
            {
                'name': 'Experto',
                'description': 'Has alcanzado 500 puntos de reputación',
                'requirement_type': 'reputation_points',
                'requirement_value': 500,
                'icon': 'fas fa-crown',
                'color': '#ffd700'
            },
        ]
        
        created_count = 0
        for badge_data in default_badges:
            existing = Badge.query.filter_by(name=badge_data['name']).first()
            if not existing:
                badge = Badge(**badge_data)
                db.session.add(badge)
                created_count += 1
        
        db.session.commit()
        print(f"✅ {created_count} badges creados exitosamente!")

def update_all_users_reputation():
    """Actualizar reputación de todos los usuarios"""
    with app.app_context():
        users = User.query.all()
        updated_count = 0
        
        for user in users:
            old_reputation = user.reputation_points
            new_reputation = user.calculate_reputation()
            newly_awarded = user.check_and_award_badges()
            
            if old_reputation != new_reputation or newly_awarded:
                updated_count += 1
                print(f"Usuario {user.username}: {old_reputation} -> {new_reputation} puntos")
                if newly_awarded:
                    badge_names = [badge.name for badge in newly_awarded]
                    print(f"  Nuevos badges: {', '.join(badge_names)}")
        
        db.session.commit()
        print(f"✅ {updated_count} usuarios actualizados!")

def create_sample_data():
    """Crear datos de ejemplo si no existen"""
    with app.app_context():
        # Crear usuarios de ejemplo si no existen
        if User.query.count() == 0:
            print("Creando usuarios de ejemplo...")
            
            # Crear categoría por defecto si no existe
            category = Category.query.first()
            if not category:
                category = Category(name='General', color='#007bff', icon='fas fa-tag')
                db.session.add(category)
                db.session.commit()
            
            users_data = [
                {'username': 'admin', 'email': 'admin@example.com', 'bio': 'Administrador del sistema'},
                {'username': 'alice', 'email': 'alice@example.com', 'bio': 'Experta en Python y Machine Learning'},
                {'username': 'bob', 'email': 'bob@example.com', 'bio': 'Desarrollador Full Stack'},
            ]
            
            for user_data in users_data:
                user = User(
                    username=user_data['username'],
                    email=user_data['email'],
                    bio=user_data['bio']
                )
                user.set_password('password123')
                db.session.add(user)
            
            db.session.commit()
            
            # Crear algunas notas de ejemplo
            users = User.query.all()
            notes_data = [
                {'title': 'Bienvenido a la Red Social de Conocimiento', 'content': 'Esta es una plataforma para compartir conocimiento y hacer nuevos amigos. ¡Explora y comparte!', 'user': users[0]},
                {'title': 'Introducción a Python', 'content': 'Python es un lenguaje de programación versátil y fácil de aprender. Perfecto para principiantes y expertos.', 'user': users[1]},
                {'title': 'Desarrollo Web Moderno', 'content': 'Las tecnologías web evolucionan constantemente. Aquí te comparto las últimas tendencias.', 'user': users[2]},
            ]
            
            for note_data in notes_data:
                note = Note(
                    title=note_data['title'],
                    content=note_data['content'],
                    category_id=category.id,
                    user_id=note_data['user'].id,
                    is_public=True
                )
                db.session.add(note)
            
            db.session.commit()
            print(f"✅ {len(users_data)} usuarios y {len(notes_data)} notas creados!")

if __name__ == '__main__':
    print("🚀 Inicializando funcionalidades sociales...")
    create_sample_data()
    init_badges()
    update_all_users_reputation()
    print("🎉 ¡Funcionalidades sociales inicializadas correctamente!")