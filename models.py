from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os

db = SQLAlchemy()

class User(UserMixin, db.Model):
    """User model for authentication"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(120))
    role = db.Column(db.String(20), default='admin')  # admin, manager, staff
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    hostels = db.relationship('Hostel', backref='manager', lazy=True, foreign_keys='Hostel.manager_id')
    
    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check if provided password matches hash"""
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.username}>'

class Hostel(db.Model):
    """Hostel model"""
    __tablename__ = 'hostels'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False, unique=True, index=True)
    location = db.Column(db.String(255), nullable=False)
    address = db.Column(db.Text)
    phone = db.Column(db.String(20))
    email = db.Column(db.String(120))
    manager_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    total_capacity = db.Column(db.Integer, default=0)
    current_occupancy = db.Column(db.Integer, default=0)
    description = db.Column(db.Text)
    amenities = db.Column(db.Text)  # JSON or comma-separated
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    rooms = db.relationship('Room', backref='hostel', lazy=True, cascade='all, delete-orphan')
    students = db.relationship('Student', backref='hostel', lazy=True)
    applications = db.relationship('Application', backref='hostel', lazy=True, cascade='all, delete-orphan')
    
    def get_occupancy_percentage(self):
        """Calculate occupancy percentage"""
        if self.total_capacity == 0:
            return 0
        return round((self.current_occupancy / self.total_capacity) * 100, 2)
    
    def update_occupancy(self):
        """Update occupancy from rooms"""
        self.current_occupancy = sum(room.current_occupancy for room in self.rooms)
    
    def __repr__(self):
        return f'<Hostel {self.name}>'

class Room(db.Model):
    """Room model"""
    __tablename__ = 'rooms'
    
    id = db.Column(db.Integer, primary_key=True)
    hostel_id = db.Column(db.Integer, db.ForeignKey('hostels.id'), nullable=False, index=True)
    floor_number = db.Column(db.Integer, nullable=False)
    room_number = db.Column(db.String(20), nullable=False)
    room_type = db.Column(db.String(20), nullable=False)  # Single, Double, Triple
    capacity = db.Column(db.Integer, default=1)
    current_occupancy = db.Column(db.Integer, default=0)
    status = db.Column(db.String(20), default='Available')  # Available, Occupied, Maintenance
    rent = db.Column(db.Float, default=0)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    students = db.relationship('Student', backref='room', lazy=True)
    
    # Unique constraint on hostel_id and room_number
    __table_args__ = (db.UniqueConstraint('hostel_id', 'room_number', name='_hostel_room_uc'),)
    
    def get_occupancy_percentage(self):
        """Calculate occupancy percentage"""
        if self.capacity == 0:
            return 0
        return round((self.current_occupancy / self.capacity) * 100, 2)
    
    def is_available(self):
        """Check if room has available space"""
        return self.current_occupancy < self.capacity and self.status == 'Available'
    
    def __repr__(self):
        return f'<Room {self.hostel_id}-{self.room_number}>'

class Student(db.Model):
    """Student model"""
    __tablename__ = 'students'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    phone = db.Column(db.String(20), nullable=False)
    roll_number = db.Column(db.String(20), unique=True, nullable=False)
    department = db.Column(db.String(100))
    year = db.Column(db.Integer)  # 1st year, 2nd year, etc.
    hostel_id = db.Column(db.Integer, db.ForeignKey('hostels.id'), nullable=True)
    room_id = db.Column(db.Integer, db.ForeignKey('rooms.id'), nullable=True)
    photo_url = db.Column(db.String(255))
    guardian_name = db.Column(db.String(120))
    guardian_phone = db.Column(db.String(20))
    address = db.Column(db.Text)
    admission_date = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='Active')  # Active, Inactive, Graduated
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    applications = db.relationship('Application', backref='student', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Student {self.name}>'

class Application(db.Model):
    """Hostel application model"""
    __tablename__ = 'applications'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False, index=True)
    hostel_id = db.Column(db.Integer, db.ForeignKey('hostels.id'), nullable=False, index=True)
    room_preference = db.Column(db.String(20))  # Single, Double, Triple
    application_date = db.Column(db.DateTime, default=datetime.utcnow)
    decision_date = db.Column(db.DateTime, nullable=True)
    status = db.Column(db.String(20), default='Pending')  # Pending, Approved, Rejected
    reason = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Application {self.student_id}-{self.hostel_id}>'
