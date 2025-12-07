from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user
from app.models import Project

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    """Home page"""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    return render_template('index.html')

@bp.route('/dashboard')
@login_required
def dashboard():
    """User dashboard"""
    projects = Project.query.filter_by(user_id=current_user.id).order_by(Project.updated_at.desc()).limit(5).all()
    total_projects = Project.query.filter_by(user_id=current_user.id).count()
    
    return render_template('dashboard.html', projects=projects, total_projects=total_projects)
