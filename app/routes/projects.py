from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, send_file, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from app import db
from app.models import Project, PDFFile
from app.pdf_processor import PDFProcessor
import os
from datetime import datetime

bp = Blueprint('projects', __name__, url_prefix='/projects')

ALLOWED_EXTENSIONS = {'pdf'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@bp.route('/')
@login_required
def list_projects():
    """List all projects for current user"""
    projects = Project.query.filter_by(user_id=current_user.id).order_by(Project.updated_at.desc()).all()
    return render_template('projects.html', projects=projects)

@bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_project():
    """Create a new project"""
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description', '')
        
        if not name:
            flash('Project name is required', 'error')
            return render_template('create_project.html')
        
        project = Project(name=name, description=description, user_id=current_user.id)
        db.session.add(project)
        db.session.commit()
        
        flash('Project created successfully', 'success')
        return redirect(url_for('projects.view_project', project_id=project.id))
    
    return render_template('create_project.html')

@bp.route('/<int:project_id>')
@login_required
def view_project(project_id):
    """View project details"""
    project = Project.query.get_or_404(project_id)
    
    # Check if user owns this project
    if project.user_id != current_user.id:
        flash('You do not have access to this project', 'error')
        return redirect(url_for('projects.list_projects'))
    
    return render_template('project_detail.html', project=project)

@bp.route('/<int:project_id>/upload', methods=['POST'])
@login_required
def upload_file(project_id):
    """Upload PDF file to project"""
    project = Project.query.get_or_404(project_id)
    
    if project.user_id != current_user.id:
        flash('You do not have access to this project', 'error')
        return redirect(url_for('projects.list_projects'))
    
    if 'file' not in request.files:
        flash('No file selected', 'error')
        return redirect(url_for('projects.view_project', project_id=project_id))
    
    file = request.files['file']
    
    if file.filename == '':
        flash('No file selected', 'error')
        return redirect(url_for('projects.view_project', project_id=project_id))
    
    if file and allowed_file(file.filename):
        original_filename = secure_filename(file.filename)
        filename = f"{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{original_filename}"
        
        # Save PDF file
        upload_folder = current_app.config['UPLOAD_FOLDER']
        project_folder = os.path.join(upload_folder, str(project_id))
        os.makedirs(project_folder, exist_ok=True)
        
        file_path = os.path.join(project_folder, filename)
        file.save(file_path)
        
        # Create PDF file record
        pdf_file = PDFFile(
            filename=filename,
            original_filename=original_filename,
            file_path=file_path,
            project_id=project_id
        )
        db.session.add(pdf_file)
        db.session.commit()
        
        # Process PDF
        try:
            processor = PDFProcessor()
            excel_filename = filename.rsplit('.', 1)[0] + '.xlsx'
            excel_path = os.path.join(project_folder, excel_filename)
            
            pdf_file.status = 'processing'
            db.session.commit()
            
            result = processor.process_pdf(file_path, excel_path)
            
            if result['success']:
                pdf_file.status = 'completed'
                pdf_file.excel_path = excel_path
                pdf_file.processed_at = datetime.utcnow()
                flash(f'File processed successfully! Found {result["unique_groups"]} unique groups from {result["total_lines"]} lines.', 'success')
            else:
                pdf_file.status = 'error'
                pdf_file.error_message = result['error']
                flash(f'Error processing file: {result["error"]}', 'error')
            
            db.session.commit()
        except Exception as e:
            pdf_file.status = 'error'
            pdf_file.error_message = str(e)
            db.session.commit()
            flash(f'Error processing file: {str(e)}', 'error')
        
        return redirect(url_for('projects.view_project', project_id=project_id))
    else:
        flash('Invalid file type. Only PDF files are allowed.', 'error')
        return redirect(url_for('projects.view_project', project_id=project_id))

@bp.route('/<int:project_id>/delete', methods=['POST'])
@login_required
def delete_project(project_id):
    """Delete a project"""
    project = Project.query.get_or_404(project_id)
    
    if project.user_id != current_user.id:
        flash('You do not have access to this project', 'error')
        return redirect(url_for('projects.list_projects'))
    
    # Delete associated files
    project_folder = os.path.join(current_app.config['UPLOAD_FOLDER'], str(project_id))
    if os.path.exists(project_folder):
        import shutil
        shutil.rmtree(project_folder)
    
    db.session.delete(project)
    db.session.commit()
    
    flash('Project deleted successfully', 'success')
    return redirect(url_for('projects.list_projects'))

@bp.route('/download/<int:file_id>')
@login_required
def download_file(file_id):
    """Download Excel file"""
    pdf_file = PDFFile.query.get_or_404(file_id)
    project = Project.query.get(pdf_file.project_id)
    
    if project.user_id != current_user.id:
        flash('You do not have access to this file', 'error')
        return redirect(url_for('projects.list_projects'))
    
    if pdf_file.excel_path and os.path.exists(pdf_file.excel_path):
        return send_file(pdf_file.excel_path, as_attachment=True, download_name=os.path.basename(pdf_file.excel_path))
    else:
        flash('Excel file not found', 'error')
        return redirect(url_for('projects.view_project', project_id=pdf_file.project_id))

# API endpoints
@bp.route('/api/projects', methods=['GET'])
@login_required
def api_list_projects():
    """API endpoint to list all projects"""
    projects = Project.query.filter_by(user_id=current_user.id).order_by(Project.updated_at.desc()).all()
    return jsonify({'projects': [p.to_dict() for p in projects]}), 200

@bp.route('/api/projects', methods=['POST'])
@login_required
def api_create_project():
    """API endpoint to create a new project"""
    data = request.get_json()
    
    name = data.get('name')
    description = data.get('description', '')
    
    if not name:
        return jsonify({'error': 'Project name is required'}), 400
    
    project = Project(name=name, description=description, user_id=current_user.id)
    db.session.add(project)
    db.session.commit()
    
    return jsonify({'message': 'Project created successfully', 'project': project.to_dict()}), 201

@bp.route('/api/projects/<int:project_id>', methods=['GET'])
@login_required
def api_get_project(project_id):
    """API endpoint to get project details"""
    project = Project.query.get_or_404(project_id)
    
    if project.user_id != current_user.id:
        return jsonify({'error': 'Access denied'}), 403
    
    project_dict = project.to_dict()
    project_dict['files'] = [f.to_dict() for f in project.pdf_files]
    
    return jsonify({'project': project_dict}), 200

@bp.route('/api/projects/<int:project_id>', methods=['DELETE'])
@login_required
def api_delete_project(project_id):
    """API endpoint to delete a project"""
    project = Project.query.get_or_404(project_id)
    
    if project.user_id != current_user.id:
        return jsonify({'error': 'Access denied'}), 403
    
    # Delete associated files
    project_folder = os.path.join(current_app.config['UPLOAD_FOLDER'], str(project_id))
    if os.path.exists(project_folder):
        import shutil
        shutil.rmtree(project_folder)
    
    db.session.delete(project)
    db.session.commit()
    
    return jsonify({'message': 'Project deleted successfully'}), 200
