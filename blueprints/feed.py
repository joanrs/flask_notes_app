from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from models import Note, Category, User
from sqlalchemy.orm import joinedload

feed_bp = Blueprint('feed', __name__)

@feed_bp.route('/feed')
@login_required
def discovery_feed():
    # Show notes from followed users
    followed_notes = current_user.get_followed_notes().limit(20).all()
    
    # If no followed users, show popular public notes
    if not followed_notes:
        followed_notes = Note.query.filter_by(is_public=True)\
            .options(joinedload(Note.author), joinedload(Note.category))\
            .order_by(Note.view_count.desc(), Note.created_at.desc())\
            .limit(20).all()
    
    return render_template('feed.html', notes=followed_notes)

@feed_bp.route('/discover')
@login_required
def discover_feed():
    # Show all public notes for discovery
    notes = Note.query.filter_by(is_public=True)\
        .options(joinedload(Note.author), joinedload(Note.category))\
        .order_by(Note.created_at.desc())\
        .limit(20).all()
        
    return render_template('discover.html', notes=notes)

@feed_bp.route('/shared-with-me')
@login_required
def shared_notes():
    notes = current_user.shared_with_me.all()
    return render_template('shared.html', notes=notes)
