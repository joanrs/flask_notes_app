from flask import Blueprint, render_template, jsonify
from flask_login import login_required, current_user
from models import Note, Task

calendar_bp = Blueprint('calendar', __name__)

@calendar_bp.route('/calendar')
@login_required
def view_calendar():
    return render_template('calendar.html')

@calendar_bp.route('/api/calendar-events')
@login_required
def get_events():
    # Fetch notes and tasks to show on calendar
    notes = Note.query.filter_by(user_id=current_user.id).all()
    tasks = Task.query.filter_by(user_id=current_user.id).all()
    
    events = []
    
    for note in notes:
        events.append({
            'id': f'note-{note.id}',
            'title': f'📝 {note.title}',
            'start': note.created_at.isoformat(),
            'url': f'/notes/{note.id}',
            'color': note.category.color if note.category else '#3366ff'
        })
        
    for task in tasks:
        if task.due_date:
            events.append({
                'id': f'task-{task.id}',
                'title': f'✅ {task.title}',
                'start': task.due_date.isoformat(),
                'color': '#ffcc00' if task.status == 'pending' else '#00cc66'
            })
            
    return jsonify(events)
