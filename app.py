from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename
from datetime import datetime
import os
from functools import wraps

from config import config
from models import db, User, Hostel, Room, Student, Application

# Initialize Flask app
app = Flask(__name__)
app.config.from_object(config['development'])

# Create upload folder if it doesn't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Initialize database
db.init_app(app)

# Initialize login manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to access this page.'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def admin_required(f):
    """Decorator to check if user is admin"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            flash('You do not have permission to access this page.', 'danger')
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated_function

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

# ==================== AUTHENTICATION ROUTES ====================

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if not username or not password:
            flash('Please enter username and password.', 'danger')
            return redirect(url_for('login'))
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password) and user.is_active:
            login_user(user, remember=request.form.get('remember'))
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password.', 'danger')
    
    return render_template('auth/login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'success')
    return redirect(url_for('login'))

# ==================== DASHBOARD ROUTE ====================

@app.route('/')
@app.route('/dashboard')
@login_required
def dashboard():
    # Get statistics
    total_students = Student.query.count()
    total_hostels = Hostel.query.count()
    total_rooms = Room.query.count()
    total_applications = Application.query.count()
    
    # Get occupancy data
    hostels = Hostel.query.all()
    occupancy_data = {
        'labels': [h.name for h in hostels],
        'data': [h.current_occupancy for h in hostels],
        'capacity': [h.total_capacity for h in hostels]
    }
    
    # Get application status data
    pending_apps = Application.query.filter_by(status='Pending').count()
    approved_apps = Application.query.filter_by(status='Approved').count()
    rejected_apps = Application.query.filter_by(status='Rejected').count()
    
    app_status_data = {
        'labels': ['Pending', 'Approved', 'Rejected'],
        'data': [pending_apps, approved_apps, rejected_apps]
    }
    
    # Get recent applications
    recent_applications = Application.query.order_by(Application.application_date.desc()).limit(5).all()
    
    return render_template('dashboard.html',
                         total_students=total_students,
                         total_hostels=total_hostels,
                         total_rooms=total_rooms,
                         total_applications=total_applications,
                         occupancy_data=occupancy_data,
                         app_status_data=app_status_data,
                         recent_applications=recent_applications,
                         pending_apps=pending_apps)

# ==================== STUDENT ROUTES ====================

@app.route('/students')
@login_required
def list_students():
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '', type=str)
    
    query = Student.query
    if search:
        query = query.filter(
            (Student.name.ilike(f'%{search}%')) |
            (Student.email.ilike(f'%{search}%')) |
            (Student.roll_number.ilike(f'%{search}%'))
        )
    
    students = query.paginate(page=page, per_page=10)
    return render_template('students/list.html', students=students, search=search)

@app.route('/students/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_student():
    if request.method == 'POST':
        try:
            name = request.form.get('name')
            email = request.form.get('email')
            phone = request.form.get('phone')
            roll_number = request.form.get('roll_number')
            department = request.form.get('department')
            year = request.form.get('year', type=int)
            hostel_id = request.form.get('hostel_id', type=int)
            room_id = request.form.get('room_id', type=int)
            guardian_name = request.form.get('guardian_name')
            guardian_phone = request.form.get('guardian_phone')
            address = request.form.get('address')
            
            # Check if student already exists
            if Student.query.filter_by(email=email).first():
                flash('Student with this email already exists.', 'danger')
                return redirect(url_for('add_student'))
            
            if Student.query.filter_by(roll_number=roll_number).first():
                flash('Student with this roll number already exists.', 'danger')
                return redirect(url_for('add_student'))
            
            student = Student(
                name=name,
                email=email,
                phone=phone,
                roll_number=roll_number,
                department=department,
                year=year,
                hostel_id=hostel_id if hostel_id else None,
                room_id=room_id if room_id else None,
                guardian_name=guardian_name,
                guardian_phone=guardian_phone,
                address=address
            )
            
            # Handle photo upload
            if 'photo' in request.files:
                file = request.files['photo']
                if file and file.filename and allowed_file(file.filename):
                    filename = secure_filename(f"student_{roll_number}_{datetime.now().timestamp()}.{file.filename.rsplit('.', 1)[1].lower()}")
                    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                    student.photo_url = f'/static/uploads/{filename}'
            
            db.session.add(student)
            db.session.commit()
            
            flash('Student added successfully!', 'success')
            return redirect(url_for('list_students'))
        
        except Exception as e:
            db.session.rollback()
            flash(f'Error adding student: {str(e)}', 'danger')
    
    hostels = Hostel.query.all()
    return render_template('students/add.html', hostels=hostels)

@app.route('/students/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_student(id):
    student = Student.query.get_or_404(id)
    
    if request.method == 'POST':
        try:
            student.name = request.form.get('name')
            student.email = request.form.get('email')
            student.phone = request.form.get('phone')
            student.department = request.form.get('department')
            student.year = request.form.get('year', type=int)
            student.hostel_id = request.form.get('hostel_id', type=int) or None
            student.room_id = request.form.get('room_id', type=int) or None
            student.guardian_name = request.form.get('guardian_name')
            student.guardian_phone = request.form.get('guardian_phone')
            student.address = request.form.get('address')
            student.status = request.form.get('status')
            
            # Handle photo upload
            if 'photo' in request.files:
                file = request.files['photo']
                if file and file.filename and allowed_file(file.filename):
                    # Delete old photo if exists
                    if student.photo_url:
                        old_file_path = student.photo_url.replace('/static/uploads/', '')
                        old_file_full_path = os.path.join(app.config['UPLOAD_FOLDER'], old_file_path)
                        if os.path.exists(old_file_full_path):
                            os.remove(old_file_full_path)
                    
                    filename = secure_filename(f"student_{student.roll_number}_{datetime.now().timestamp()}.{file.filename.rsplit('.', 1)[1].lower()}")
                    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                    student.photo_url = f'/static/uploads/{filename}'
            
            student.updated_at = datetime.utcnow()
            db.session.commit()
            
            flash('Student updated successfully!', 'success')
            return redirect(url_for('list_students'))
        
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating student: {str(e)}', 'danger')
    
    hostels = Hostel.query.all()
    rooms = Room.query.all() if student.hostel_id else []
    return render_template('students/edit.html', student=student, hostels=hostels, rooms=rooms)

@app.route('/students/delete/<int:id>', methods=['POST'])
@login_required
@admin_required
def delete_student(id):
    student = Student.query.get_or_404(id)
    
    try:
        # Delete photo if exists
        if student.photo_url:
            file_path = student.photo_url.replace('/static/uploads/', '')
            file_full_path = os.path.join(app.config['UPLOAD_FOLDER'], file_path)
            if os.path.exists(file_full_path):
                os.remove(file_full_path)
        
        db.session.delete(student)
        db.session.commit()
        flash('Student deleted successfully!', 'success')
    
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting student: {str(e)}', 'danger')
    
    return redirect(url_for('list_students'))

# ==================== HOSTEL ROUTES ====================

@app.route('/hostels')
@login_required
def list_hostels():
    page = request.args.get('page', 1, type=int)
    hostels = Hostel.query.paginate(page=page, per_page=10)
    return render_template('hostels/list.html', hostels=hostels)

@app.route('/hostels/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_hostel():
    if request.method == 'POST':
        try:
            name = request.form.get('name')
            location = request.form.get('location')
            address = request.form.get('address')
            phone = request.form.get('phone')
            email = request.form.get('email')
            manager_id = request.form.get('manager_id', type=int)
            total_capacity = request.form.get('total_capacity', type=int)
            description = request.form.get('description')
            amenities = request.form.get('amenities')
            
            # Check if hostel already exists
            if Hostel.query.filter_by(name=name).first():
                flash('Hostel with this name already exists.', 'danger')
                return redirect(url_for('add_hostel'))
            
            hostel = Hostel(
                name=name,
                location=location,
                address=address,
                phone=phone,
                email=email,
                manager_id=manager_id if manager_id else None,
                total_capacity=total_capacity,
                description=description,
                amenities=amenities
            )
            
            db.session.add(hostel)
            db.session.commit()
            
            flash('Hostel added successfully!', 'success')
            return redirect(url_for('list_hostels'))
        
        except Exception as e:
            db.session.rollback()
            flash(f'Error adding hostel: {str(e)}', 'danger')
    
    managers = User.query.filter_by(role='manager').all()
    return render_template('hostels/add.html', managers=managers)

@app.route('/hostels/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_hostel(id):
    hostel = Hostel.query.get_or_404(id)
    
    if request.method == 'POST':
        try:
            hostel.name = request.form.get('name')
            hostel.location = request.form.get('location')
            hostel.address = request.form.get('address')
            hostel.phone = request.form.get('phone')
            hostel.email = request.form.get('email')
            hostel.manager_id = request.form.get('manager_id', type=int) or None
            hostel.total_capacity = request.form.get('total_capacity', type=int)
            hostel.description = request.form.get('description')
            hostel.amenities = request.form.get('amenities')
            hostel.updated_at = datetime.utcnow()
            
            db.session.commit()
            
            flash('Hostel updated successfully!', 'success')
            return redirect(url_for('list_hostels'))
        
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating hostel: {str(e)}', 'danger')
    
    managers = User.query.filter_by(role='manager').all()
    return render_template('hostels/edit.html', hostel=hostel, managers=managers)

@app.route('/hostels/delete/<int:id>', methods=['POST'])
@login_required
@admin_required
def delete_hostel(id):
    hostel = Hostel.query.get_or_404(id)
    
    try:
        db.session.delete(hostel)
        db.session.commit()
        flash('Hostel deleted successfully!', 'success')
    
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting hostel: {str(e)}', 'danger')
    
    return redirect(url_for('list_hostels'))

# ==================== ROOM ROUTES ====================

@app.route('/rooms')
@login_required
def list_rooms():
    page = request.args.get('page', 1, type=int)
    hostel_id = request.args.get('hostel_id', type=int)
    
    query = Room.query
    if hostel_id:
        query = query.filter_by(hostel_id=hostel_id)
    
    rooms = query.paginate(page=page, per_page=10)
    hostels = Hostel.query.all()
    
    return render_template('rooms/list.html', rooms=rooms, hostels=hostels, selected_hostel=hostel_id)

@app.route('/rooms/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_room():
    if request.method == 'POST':
        try:
            hostel_id = request.form.get('hostel_id', type=int)
            floor_number = request.form.get('floor_number', type=int)
            room_number = request.form.get('room_number')
            room_type = request.form.get('room_type')
            capacity = request.form.get('capacity', type=int)
            rent = request.form.get('rent', type=float)
            description = request.form.get('description')
            
            # Check if room already exists
            if Room.query.filter_by(hostel_id=hostel_id, room_number=room_number).first():
                flash('Room with this number already exists in this hostel.', 'danger')
                return redirect(url_for('add_room'))
            
            room = Room(
                hostel_id=hostel_id,
                floor_number=floor_number,
                room_number=room_number,
                room_type=room_type,
                capacity=capacity,
                rent=rent,
                description=description,
                status='Available'
            )
            
            db.session.add(room)
            db.session.commit()
            
            flash('Room added successfully!', 'success')
            return redirect(url_for('list_rooms'))
        
        except Exception as e:
            db.session.rollback()
            flash(f'Error adding room: {str(e)}', 'danger')
    
    hostels = Hostel.query.all()
    return render_template('rooms/add.html', hostels=hostels)

@app.route('/rooms/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_room(id):
    room = Room.query.get_or_404(id)
    
    if request.method == 'POST':
        try:
            room.floor_number = request.form.get('floor_number', type=int)
            room.room_number = request.form.get('room_number')
            room.room_type = request.form.get('room_type')
            room.capacity = request.form.get('capacity', type=int)
            room.rent = request.form.get('rent', type=float)
            room.status = request.form.get('status')
            room.description = request.form.get('description')
            room.updated_at = datetime.utcnow()
            
            db.session.commit()
            
            flash('Room updated successfully!', 'success')
            return redirect(url_for('list_rooms'))
        
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating room: {str(e)}', 'danger')
    
    hostels = Hostel.query.all()
    return render_template('rooms/edit.html', room=room, hostels=hostels)

@app.route('/rooms/delete/<int:id>', methods=['POST'])
@login_required
@admin_required
def delete_room(id):
    room = Room.query.get_or_404(id)
    
    try:
        db.session.delete(room)
        db.session.commit()
        flash('Room deleted successfully!', 'success')
    
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting room: {str(e)}', 'danger')
    
    return redirect(url_for('list_rooms'))

# ==================== APPLICATION ROUTES ====================

@app.route('/applications')
@login_required
def list_applications():
    page = request.args.get('page', 1, type=int)
    status = request.args.get('status', '', type=str)
    
    query = Application.query
    if status:
        query = query.filter_by(status=status)
    
    applications = query.order_by(Application.application_date.desc()).paginate(page=page, per_page=10)
    return render_template('applications/list.html', applications=applications, selected_status=status)

@app.route('/applications/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_application(id):
    application = Application.query.get_or_404(id)
    
    if request.method == 'POST':
        try:
            application.status = request.form.get('status')
            application.reason = request.form.get('reason')
            application.decision_date = datetime.utcnow()
            
            # If approved, assign room to student
            if application.status == 'Approved':
                student = application.student
                student.hostel_id = application.hostel_id
                # Find available room of preferred type
                room = Room.query.filter_by(
                    hostel_id=application.hostel_id,
                    room_type=application.room_preference,
                    status='Available'
                ).first()
                if room and room.is_available():
                    student.room_id = room.id
                    room.current_occupancy += 1
                    if room.current_occupancy >= room.capacity:
                        room.status = 'Occupied'
                    application.hostel.update_occupancy()
            
            application.updated_at = datetime.utcnow()
            db.session.commit()
            
            flash('Application updated successfully!', 'success')
            return redirect(url_for('list_applications'))
        
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating application: {str(e)}', 'danger')
    
    return render_template('applications/edit.html', application=application)

@app.route('/applications/delete/<int:id>', methods=['POST'])
@login_required
@admin_required
def delete_application(id):
    application = Application.query.get_or_404(id)
    
    try:
        db.session.delete(application)
        db.session.commit()
        flash('Application deleted successfully!', 'success')
    
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting application: {str(e)}', 'danger')
    
    return redirect(url_for('list_applications'))

# ==================== API ROUTES ====================

@app.route('/api/rooms/<int:hostel_id>')
@login_required
def get_hostel_rooms(hostel_id):
    """Get rooms for a specific hostel"""
    rooms = Room.query.filter_by(hostel_id=hostel_id).all()
    return jsonify([{
        'id': room.id,
        'room_number': room.room_number,
        'room_type': room.room_type,
        'capacity': room.capacity,
        'current_occupancy': room.current_occupancy,
        'status': room.status
    } for room in rooms])

# ==================== ERROR HANDLERS ====================

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(e):
    db.session.rollback()
    return render_template('500.html'), 500

# ==================== INITIALIZATION ====================

def init_db():
    """Initialize database with default data"""
    with app.app_context():
        db.create_all()
        
        # Check if admin user already exists
        if not User.query.filter_by(username='admin').first():
            admin = User(
                username='admin',
                email='admin@hostel.com',
                full_name='Administrator',
                role='admin',
                is_active=True
            )
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()
            print('Admin user created: admin / admin123')

if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0', port=5000)
