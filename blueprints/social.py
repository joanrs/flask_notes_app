from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from extensions import db
from models import Note, Like, Comment, Badge, User
from datetime import datetime

social_bp = Blueprint('social', __name__)

@social_bp.route('/api/notes/<int:note_id>/like', methods=['POST'])
@login_required
def toggle_like(note_id):
    """Toggle like on a note"""
    note = Note.query.get_or_404(note_id)
    
    # Check if user already liked this note
    existing_like = Like.query.filter_by(note_id=note_id, user_id=current_user.id).first()
    
    if existing_like:
        # Unlike
        db.session.delete(existing_like)
        liked = False
        message = "Like removido"
    else:
        # Like
        new_like = Like(note_id=note_id, user_id=current_user.id)
        db.session.add(new_like)
        liked = True
        message = "¡Te gusta esta nota!"
        
        # Award reputation points to note author
        if note.author != current_user:
            note.author.reputation_points += 5
    
    db.session.commit()
    
    # Update author's reputation and check for badges
    if note.author != current_user:
        note.author.calculate_reputation()
        newly_awarded = note.author.check_and_award_badges()
        db.session.commit()
    
    return jsonify({
        'success': True,
        'liked': liked,
        'likes_count': len(note.likes),
        'message': message
    })

@social_bp.route('/api/notes/<int:note_id>/comments', methods=['GET', 'POST'])
@login_required
def handle_comments(note_id):
    """Get or create comments for a note"""
    note = Note.query.get_or_404(note_id)
    
    if request.method == 'POST':
        data = request.get_json()
        content = data.get('content', '').strip()
        parent_id = data.get('parent_id')
        
        if not content:
            return jsonify({'error': 'El comentario no puede estar vacío'}), 400
        
        # Create comment
        comment = Comment(
            content=content,
            note_id=note_id,
            user_id=current_user.id,
            parent_id=parent_id
        )
        db.session.add(comment)
        
        # Award reputation points
        current_user.reputation_points += 2
        if note.author != current_user:
            note.author.reputation_points += 1
        
        db.session.commit()
        
        # Update reputation and check badges
        current_user.calculate_reputation()
        newly_awarded = current_user.check_and_award_badges()
        
        if note.author != current_user:
            note.author.calculate_reputation()
            note.author.check_and_award_badges()
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'comment': comment.to_dict(),
            'message': 'Comentario agregado exitosamente'
        })
    
    else:
        # GET - Return comments
        comments = note.get_top_level_comments()
        return jsonify({
            'comments': [comment.to_dict() for comment in comments],
            'total': len(note.comments)
        })

@social_bp.route('/api/comments/<int:comment_id>/replies')
@login_required
def get_comment_replies(comment_id):
    """Get replies for a specific comment"""
    comment = Comment.query.get_or_404(comment_id)
    replies = comment.replies.order_by(Comment.created_at.asc()).all()
    
    return jsonify({
        'replies': [reply.to_dict() for reply in replies]
    })

@social_bp.route('/api/comments/<int:comment_id>/delete', methods=['DELETE'])
@login_required
def delete_comment(comment_id):
    """Delete a comment (only by author)"""
    comment = Comment.query.get_or_404(comment_id)
    
    if comment.author != current_user:
        return jsonify({'error': 'No tienes permiso para eliminar este comentario'}), 403
    
    db.session.delete(comment)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': 'Comentario eliminado'
    })

@social_bp.route('/badges')
@login_required
def list_badges():
    """List all available badges"""
    badges = Badge.query.all()
    user_badge_ids = [badge.id for badge in current_user.badges]
    
    return render_template('social/badges.html', badges=badges, user_badge_ids=user_badge_ids)

@social_bp.route('/leaderboard')
@login_required
def leaderboard():
    """Show reputation leaderboard"""
    top_users = User.query.order_by(User.reputation_points.desc()).limit(50).all()
    
    # Update all users' reputation (could be optimized with background tasks)
    for user in top_users:
        user.calculate_reputation()
    db.session.commit()
    
    return render_template('social/leaderboard.html', users=top_users)

@social_bp.route('/api/user/<int:user_id>/reputation/update', methods=['POST'])
@login_required
def update_user_reputation(user_id):
    """Manually update user reputation (admin only or self)"""
    if user_id != current_user.id:
        return jsonify({'error': 'No autorizado'}), 403
    
    user = User.query.get_or_404(user_id)
    old_reputation = user.reputation_points
    new_reputation = user.calculate_reputation()
    newly_awarded = user.check_and_award_badges()
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'old_reputation': old_reputation,
        'new_reputation': new_reputation,
        'newly_awarded_badges': [{'name': badge.name, 'icon': badge.icon} for badge in newly_awarded]
    })

# Initialize default badges
@social_bp.route('/init-badges', methods=['POST'])
@login_required
def init_default_badges():
    """Initialize default badges (admin function)"""
    default_badges = [
        {'name': 'Primer Paso', 'description': 'Creaste tu primera nota', 'requirement_type': 'notes_count', 'requirement_value': 1, 'icon': 'fas fa-baby', 'color': '#28a745'},
        {'name': 'Escritor', 'description': 'Has creado 10 notas', 'requirement_type': 'notes_count', 'requirement_value': 10, 'icon': 'fas fa-pen', 'color': '#007bff'},
        {'name': 'Autor Prolífico', 'description': 'Has creado 50 notas', 'requirement_type': 'notes_count', 'requirement_value': 50, 'icon': 'fas fa-book', 'color': '#6f42c1'},
        {'name': 'Popular', 'description': 'Has recibido 50 likes', 'requirement_type': 'likes_received', 'requirement_value': 50, 'icon': 'fas fa-heart', 'color': '#dc3545'},
        {'name': 'Estrella', 'description': 'Has recibido 200 likes', 'requirement_type': 'likes_received', 'requirement_value': 200, 'icon': 'fas fa-star', 'color': '#ffc107'},
        {'name': 'Conversador', 'description': 'Has hecho 25 comentarios', 'requirement_type': 'comments_made', 'requirement_value': 25, 'icon': 'fas fa-comments', 'color': '#17a2b8'},
        {'name': 'Influencer', 'description': 'Tienes 20 seguidores', 'requirement_type': 'followers_count', 'requirement_value': 20, 'icon': 'fas fa-users', 'color': '#fd7e14'},
        {'name': 'Experto', 'description': 'Has alcanzado 1000 puntos de reputación', 'requirement_type': 'reputation_points', 'requirement_value': 1000, 'icon': 'fas fa-crown', 'color': '#ffd700'},
    ]
    
    created_count = 0
    for badge_data in default_badges:
        existing = Badge.query.filter_by(name=badge_data['name']).first()
        if not existing:
            badge = Badge(**badge_data)
            db.session.add(badge)
            created_count += 1
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': f'{created_count} badges creados',
        'created_count': created_count
    })