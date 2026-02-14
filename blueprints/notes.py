from flask import Blueprint, render_template, request, redirect, url_for, flash, send_from_directory, jsonify, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
import os
from datetime import datetime
from sqlalchemy.orm import joinedload
from extensions import db
from models import User, Category, Note, Attachment, Like
from helpers import categories_to_dict, category_to_dict, allowed_file

notes_bp = Blueprint('notes', __name__)


@notes_bp.route('/notes/table')
@login_required
def notes_table():
    page = request.args.get('page', 1, type=int)
    format_type = request.args.get('format', 'html')
    per_page = request.args.get('per_page', 25, type=int)
    
    notes_query = Note.query.filter_by(user_id=current_user.id)\
        .options(
            joinedload(Note.category),
            joinedload(Note.attachments),
            joinedload(Note.likes)
        )
    
    # Apply filters from URL if AJAX request
    if format_type == 'json':
        category_id = request.args.get('category')
        search = request.args.get('search')
        
        if category_id:
            notes_query = notes_query.filter_by(category_id=category_id)
        
        if search:
            notes_query = notes_query.filter(
                db.or_(
                    Note.title.ilike(f'%{search}%'),
                    Note.content.ilike(f'%{search}%')
                )
            )
    
    notes_query = notes_query.order_by(Note.updated_at.desc())
    notes_paginated = notes_query.paginate(page=page, per_page=per_page, error_out=False)
    
    # Pre-cálculos
    for note in notes_paginated.items:
        note.content_preview = note.content[:150] + ('...' if len(note.content) > 150 else '')
        note.attachments_count = len(note.attachments)
        note.likes_count = len(note.likes)
    
    # Usar el helper
    categories_data = categories_to_dict()
    
    # JSON response for AJAX
    if format_type == 'json':
        notes_data = []
        for note in notes_paginated.items:
            notes_data.append({
                'id': note.id,
                'title': note.title,
                'content': note.content,
                'content_preview': note.content_preview,
                'created_at': note.created_at.isoformat(),
                'updated_at': note.updated_at.isoformat(),
                'category_id': note.category_id,
                'category': category_to_dict(note.category),
                'attachments_count': note.attachments_count,
                'attachments': [{'id': a.id, 'filename': a.filename, 'file_type': a.file_type} for a in note.attachments],
                'likes_count': note.likes_count,
                'user_id': note.user_id
            })
        
        return jsonify({
            'items': notes_data,
            'total': notes_paginated.total,
            'page': notes_paginated.page,
            'pages': notes_paginated.pages,
            'has_prev': notes_paginated.has_prev,
            'has_next': notes_paginated.has_next,
            'prev_num': notes_paginated.prev_num,
            'next_num': notes_paginated.next_num
        })
    
    # Convertir notas paginadas a diccionario
    notes_data = {
        'items': [note.to_dict() for note in notes_paginated.items],
        'total': notes_paginated.total,
        'page': notes_paginated.page,
        'pages': notes_paginated.pages,
        'has_prev': notes_paginated.has_prev,
        'has_next': notes_paginated.has_next,
        'prev_num': notes_paginated.prev_num,
        'next_num': notes_paginated.next_num
    }
    
    return render_template('notes_table.html', notes=notes_data, categories=categories_data)

@notes_bp.route('/notes/keep')
@login_required
def notes_keep():
    page = request.args.get('page', 1, type=int)
    format_type = request.args.get('format', 'html')
    per_page = 12
    
    notes_query = Note.query.filter_by(user_id=current_user.id)\
        .options(
            joinedload(Note.category),
            joinedload(Note.attachments),
            joinedload(Note.likes)
        )\
        .order_by(Note.updated_at.desc())
    
    notes_paginated = notes_query.paginate(page=page, per_page=per_page, error_out=False)
    
    # Pre-cálculos
    for note in notes_paginated.items:
        note.content_preview = note.content[:150] + ('...' if len(note.content) > 150 else '')
        note.attachments_count = len(note.attachments)
        note.likes_count = len(note.likes)
    
    # Usar el helper
    categories_data = categories_to_dict()
    
    # Si es una petición JSON (para AJAX/Vue)
    if format_type == 'json':
        notes_data = []
        for note in notes_paginated.items:
            notes_data.append({
                'id': note.id,
                'title': note.title,
                'content': note.content,
                'content_preview': note.content_preview,
                'created_at': note.created_at.isoformat(),
                'updated_at': note.updated_at.isoformat(),
                'category_id': note.category_id,
                'category': category_to_dict(note.category),
                'attachments_count': note.attachments_count,
                'attachments': [{'id': a.id, 'filename': a.filename, 'file_type': a.file_type} for a in note.attachments],
                'likes_count': note.likes_count,
                'user_id': note.user_id
            })
        
        return jsonify({
            'items': notes_data,
            'total': notes_paginated.total,
            'page': notes_paginated.page,
            'pages': notes_paginated.pages,
            'has_prev': notes_paginated.has_prev,
            'has_next': notes_paginated.has_next,
            'prev_num': notes_paginated.prev_num,
            'next_num': notes_paginated.next_num
        })
    
    # Convertir notas paginadas a diccionario
    notes_data = {
        'items': [note.to_dict() for note in notes_paginated.items],
        'total': notes_paginated.total,
        'page': notes_paginated.page,
        'pages': notes_paginated.pages,
        'has_prev': notes_paginated.has_prev,
        'has_next': notes_paginated.has_next,
        'prev_num': notes_paginated.prev_num,
        'next_num': notes_paginated.next_num
    }
    
    return render_template('notes_keep.html', notes=notes_data, categories=categories_data)

@notes_bp.route('/notes/create', methods=['GET', 'POST'])
@login_required
def create_note():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        category_id = request.form['category_id']
        
        is_public = 'is_public' in request.form
        
        new_note = Note(
            title=title, 
            content=content, 
            category_id=category_id, 
            author=current_user,
            is_public=is_public
        )
        db.session.add(new_note)
        db.session.commit()
        
        # Handle file uploads
        if 'attachments' in request.files:
            files = request.files.getlist('attachments')
            upload_error = False
            for file in files:
                if file.filename == '':
                    continue
                
                if allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    # Handle potential duplicate filenames by appending timestamp
                    if os.path.exists(os.path.join(current_app.config['UPLOAD_FOLDER'], filename)):
                        timestamp = datetime.now().strftime('%Y%m%d%H%M%S_')
                        filename = timestamp + filename
                    
                    file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                    file.save(file_path)
                    
                    attachment = Attachment(
                        filename=filename,
                        file_path=file_path,
                        file_type=file.content_type,
                        note_id=new_note.id
                    )
                    db.session.add(attachment)
                else:
                    upload_error = True
            
            if upload_error:
                flash('Some files were not uploaded because their extension is not allowed.', 'warning')
        
        db.session.commit()
        flash('Note created successfully!', 'success')
        return redirect(url_for('notes.notes_table'))
    
    categories = Category.query.all()
    return render_template('create_note.html', categories=categories)

@notes_bp.route('/notes/<int:note_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_note(note_id):
    note = Note.query.get_or_404(note_id)
    if note.author != current_user:
        flash('You do not have permission to edit this note.', 'error')
        return redirect(url_for('notes.notes_table'))
    
    if request.method == 'POST':
        note.title = request.form['title']
        note.content = request.form['content']
        note.category_id = request.form['category_id']
        note.is_public = 'is_public' in request.form
        
        # Handle new file uploads
        if 'attachments' in request.files:
            files = request.files.getlist('attachments')
            upload_error = False
            for file in files:
                if file.filename == '':
                    continue
                
                if allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    # Handle potential duplicate filenames by appending timestamp
                    if os.path.exists(os.path.join(current_app.config['UPLOAD_FOLDER'], filename)):
                        timestamp = datetime.now().strftime('%Y%m%d%H%M%S_')
                        filename = timestamp + filename
                        
                    file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                    file.save(file_path)
                    
                    attachment = Attachment(
                        filename=filename,
                        file_path=file_path,
                        file_type=file.content_type,
                        note_id=note.id
                    )
                    db.session.add(attachment)
                else:
                    upload_error = True
            
            if upload_error:
                flash('Some files were not uploaded because their extension is not allowed.', 'warning')
        
        db.session.commit()
        flash('Note updated successfully!', 'success')
        return redirect(url_for('notes.view_note', note_id=note.id))
    
    categories = Category.query.all()
    return render_template('edit_note.html', note=note, categories=categories)

@notes_bp.route('/notes/<int:note_id>')
@login_required
def view_note(note_id):
    note = Note.query.get_or_404(note_id)
    
    # Allow viewing if it's the user's own note or if it's public
    if note.author != current_user and not note.is_public:
        flash('You do not have permission to view this note.', 'error')
        return redirect(url_for('notes.notes_table'))
    
    # Increment view count if it's not the author viewing
    if note.author != current_user:
        note.view_count += 1
        db.session.commit()
    
    return render_template('view_note.html', note=note)

@notes_bp.route('/notes/<int:note_id>/delete', methods=['POST'])
@login_required
def delete_note(note_id):
    note = Note.query.get_or_404(note_id)
    if note.author != current_user:
        flash('You do not have permission to delete this note.', 'error')
        return redirect(url_for('notes.notes_table'))
    
    # Delete associated files
    for attachment in note.attachments:
        try:
            if os.path.exists(attachment.file_path):
                os.remove(attachment.file_path)
        except Exception as e:
            current_app.logger.error(f'Error deleting file {attachment.file_path}: {e}')
    
    db.session.delete(note)
    db.session.commit()
    flash('Note deleted successfully!', 'success')
    return redirect(url_for('notes.notes_table'))

@notes_bp.route('/notes/<int:note_id>/like', methods=['POST'])
@login_required
def like_note(note_id):
    note = Note.query.get_or_404(note_id)
    like = Like(note_id=note.id)
    db.session.add(like)
    db.session.commit()
    return redirect(url_for('notes.view_note', note_id=note.id))

@notes_bp.route('/notes/<int:note_id>/attachment/<int:attachment_id>/delete', methods=['POST'])
@login_required
def delete_attachment(note_id, attachment_id):
    attachment = Attachment.query.get_or_404(attachment_id)
    
    # Verify the attachment belongs to the note
    if attachment.note_id != note_id:
        flash('Invalid attachment!', 'error')
        return redirect(url_for('notes.view_note', note_id=note_id))
    
    # Delete the file
    try:
        if os.path.exists(attachment.file_path):
            os.remove(attachment.file_path)
    except Exception as e:
        current_app.logger.error(f'Error deleting file {attachment.file_path}: {e}')
        flash('Error deleting file!', 'error')
    
    db.session.delete(attachment)
    db.session.commit()
    flash('Attachment deleted successfully!', 'success')
    return redirect(url_for('notes.view_note', note_id=note_id))

@notes_bp.route('/uploads/<filename>')
@login_required
def download_file(filename):
    return send_from_directory(current_app.config['UPLOAD_FOLDER'], filename)
