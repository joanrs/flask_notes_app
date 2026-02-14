from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from extensions import db
from models import Task
from datetime import datetime

tasks_bp = Blueprint('tasks', __name__)

@tasks_bp.route('/tasks')
@login_required
def list_tasks():
    tasks = Task.query.filter_by(user_id=current_user.id).order_by(Task.due_date.asc(), Task.priority.desc()).all()
    return render_template('tasks.html', tasks=tasks)

@tasks_bp.route('/tasks/create', methods=['POST'])
@login_required
def create_task():
    title = request.form.get('title')
    description = request.form.get('description')
    due_date_str = request.form.get('due_date')
    priority = request.form.get('priority', 1, type=int)
    
    if not title:
        flash('Title is required', 'error')
        return redirect(url_for('tasks.list_tasks'))
    
    due_date = None
    if due_date_str:
        due_date = datetime.fromisoformat(due_date_str)
    
    new_task = Task(
        title=title,
        description=description,
        due_date=due_date,
        priority=priority,
        user=current_user
    )
    db.session.add(new_task)
    db.session.commit()
    
    flash('Task created successfully!', 'success')
    return redirect(url_for('tasks.list_tasks'))

@tasks_bp.route('/tasks/<int:task_id>/toggle', methods=['POST'])
@login_required
def toggle_task(task_id):
    task = Task.query.get_or_404(task_id)
    if task.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    task.status = 'completed' if task.status == 'pending' else 'pending'
    db.session.commit()
    return jsonify({'status': task.status})

@tasks_bp.route('/tasks/<int:task_id>/delete', methods=['POST'])
@login_required
def delete_task(task_id):
    task = Task.query.get_or_404(task_id)
    if task.user_id != current_user.id:
        flash('Unauthorized', 'error')
        return redirect(url_for('tasks.list_tasks'))
    
    db.session.delete(task)
    db.session.commit()
    flash('Task deleted', 'info')
    return redirect(url_for('tasks.list_tasks'))
