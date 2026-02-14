from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from flask_login import login_required, current_user
from extensions import db
from models import User, Note
from sqlalchemy import or_

users_bp = Blueprint('users', __name__)

@users_bp.route('/users')
@login_required
def users_list():
    """Lista de todos los usuarios"""
    search = request.args.get('search', '')
    page = request.args.get('page', 1, type=int)
    per_page = 12
    
    query = User.query
    if search:
        query = query.filter(or_(
            User.username.contains(search),
            User.bio.contains(search)
        ))
    
    users = query.paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return render_template('users/list.html', users=users, search=search)

@users_bp.route('/users/<int:user_id>')
@login_required
def user_profile(user_id):
    """Perfil de usuario"""
    user = User.query.get_or_404(user_id)
    
    # Obtener notas públicas del usuario
    notes = Note.query.filter_by(user_id=user_id, is_public=True).order_by(Note.created_at.desc()).limit(10).all()
    
    # Verificar si el usuario actual sigue a este usuario
    is_following = current_user.is_following(user) if current_user.is_authenticated else False
    
    return render_template('users/profile.html', 
                         user=user, 
                         notes=notes, 
                         is_following=is_following)

@users_bp.route('/users/<int:user_id>/followers')
@login_required
def user_followers(user_id):
    """Lista de seguidores del usuario"""
    user = User.query.get_or_404(user_id)
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    followers = user.followers.paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return render_template('users/followers.html', user=user, followers=followers)

@users_bp.route('/users/<int:user_id>/following')
@login_required
def user_following(user_id):
    """Lista de usuarios que sigue"""
    user = User.query.get_or_404(user_id)
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    following = user.followed.paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return render_template('users/following.html', user=user, following=following)

@users_bp.route('/api/users/<int:user_id>/follow', methods=['POST'])
@login_required
def follow_user(user_id):
    """Seguir a un usuario"""
    if user_id == current_user.id:
        return jsonify({'error': 'No puedes seguirte a ti mismo'}), 400
    
    user = User.query.get_or_404(user_id)
    
    if current_user.is_following(user):
        return jsonify({'error': 'Ya sigues a este usuario'}), 400
    
    current_user.follow(user)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': f'Ahora sigues a {user.username}',
        'followers_count': user.get_followers_count()
    })

@users_bp.route('/api/users/<int:user_id>/unfollow', methods=['POST'])
@login_required
def unfollow_user(user_id):
    """Dejar de seguir a un usuario"""
    if user_id == current_user.id:
        return jsonify({'error': 'No puedes dejar de seguirte a ti mismo'}), 400
    
    user = User.query.get_or_404(user_id)
    
    if not current_user.is_following(user):
        return jsonify({'error': 'No sigues a este usuario'}), 400
    
    current_user.unfollow(user)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': f'Has dejado de seguir a {user.username}',
        'followers_count': user.get_followers_count()
    })

@users_bp.route('/api/users/suggestions')
@login_required
def user_suggestions():
    """Sugerencias de usuarios para seguir"""
    # Usuarios que no sigue actualmente
    following_ids = [user.id for user in current_user.followed.all()]
    following_ids.append(current_user.id)  # Excluir a sí mismo
    
    suggested_users = User.query.filter(~User.id.in_(following_ids)).limit(5).all()
    
    return jsonify([user.to_dict() for user in suggested_users])

@users_bp.route('/my-profile')
@login_required
def my_profile():
    """Perfil del usuario actual"""
    return redirect(url_for('users.user_profile', user_id=current_user.id))