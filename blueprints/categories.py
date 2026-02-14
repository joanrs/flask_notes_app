from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from extensions import db
from models import Category

categories_bp = Blueprint('categories', __name__)

@categories_bp.route('/categories')
@login_required
def list_categories():
    categories = Category.query.all()
    return render_template('categories.html', categories=categories)

@categories_bp.route('/categories/create', methods=['GET', 'POST'])
@login_required
def create_category():
    if request.method == 'POST':
        name = request.form['name']
        color = request.form['color']
        
        if not name:
            flash('Category name is required!', 'error')
            return redirect(url_for('categories.create_category'))
        
        # Check if category already exists
        existing_category = Category.query.filter_by(name=name).first()
        if existing_category:
            flash('Category already exists!', 'error')
            return redirect(url_for('categories.create_category'))
        
        new_category = Category(name=name, color=color)
        db.session.add(new_category)
        db.session.commit()
        flash('Category created successfully!', 'success')
        return redirect(url_for('categories.list_categories'))
    
    return render_template('create_category.html')

@categories_bp.route('/categories/<int:category_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_category(category_id):
    category = Category.query.get_or_404(category_id)
    
    if request.method == 'POST':
        category.name = request.form['name']
        category.color = request.form['color']
        db.session.commit()
        flash('Category updated successfully!', 'success')
        return redirect(url_for('categories.list_categories'))
    
    return render_template('edit_category.html', category=category)

@categories_bp.route('/categories/<int:category_id>/delete', methods=['POST'])
@login_required
def delete_category(category_id):
    category = Category.query.get_or_404(category_id)
    
    # Check if category has notes
    if category.notes:
        flash('Cannot delete category with notes! Move or delete notes first.', 'error')
        return redirect(url_for('categories.list_categories'))
    
    db.session.delete(category)
    db.session.commit()
    flash('Category deleted successfully!', 'success')
    return redirect(url_for('categories.list_categories'))
