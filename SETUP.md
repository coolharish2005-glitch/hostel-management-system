# Hostel Management System - Setup & Installation Guide

## 🚀 Quick Start Guide

Follow these steps to set up and run the Hostel Management System on your local machine.

### Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.8 or higher** - [Download Python](https://www.python.org/downloads/)
- **pip** (Python package installer) - Usually comes with Python
- **Git** - [Download Git](https://git-scm.com/)
- **Text Editor or IDE** - VSCode, PyCharm, etc. (optional)

### Step 1: Clone the Repository

```bash
git clone https://github.com/coolharish2005-glitch/hostel-management-system.git
cd hostel-management-system
```

### Step 2: Create Virtual Environment

#### On Windows:
```bash
python -m venv venv
venv\Scripts\activate
```

#### On macOS/Linux:
```bash
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Configure Environment Variables

Edit the `.env` file and update the following (optional):

```env
FLASK_APP=app.py
FLASK_ENV=development
SECRET_KEY=your-secret-key-here-change-in-production
DATABASE_URL=sqlite:///hostel_management.db
```

### Step 5: Initialize Database

```bash
python
```

Then in the Python shell:

```python
from app import app, db
with app.app_context():
    db.create_all()
print("Database initialized!")
exit()
```

### Step 6: Run the Application

```bash
python app.py
```

The application will start at: **http://localhost:5000**

### Step 7: Login

Use the default credentials:

- **Username:** `admin`
- **Password:** `admin123`

> ⚠️ **Important:** Change the default credentials in production!

---

## 📁 Project Structure Explained

```
hostel-management-system/
├── app.py                    # Main Flask application with all routes
├── config.py                 # Configuration management
├── models.py                 # Database models (User, Student, Hostel, Room, Application)
├── requirements.txt          # Python dependencies
├── .env                      # Environment variables
├── .gitignore               # Git ignore file
├── README.md                # Project documentation
├── SETUP.md                 # This file
│
├── templates/               # HTML templates
│   ├── base.html           # Base template with sidebar & header
│   ├── dashboard.html      # Main dashboard
│   ├── 404.html            # 404 error page
│   ├── 500.html            # 500 error page
│   ├── auth/
│   │   └── login.html      # Login page
│   ├── students/
│   │   ├── list.html       # List all students
│   │   ├── add.html        # Add new student
│   │   └── edit.html       # Edit student
│   ├── hostels/
│   │   ├── list.html       # List all hostels
│   │   ├── add.html        # Add new hostel
│   │   └── edit.html       # Edit hostel
│   ├── rooms/
│   │   ├── list.html       # List all rooms
│   │   ├── add.html        # Add new room
│   │   └── edit.html       # Edit room
│   └── applications/
│       ├── list.html       # List applications
│       └── edit.html       # Review application
│
├── static/                  # Static files
│   ├── css/
│   │   └── style.css       # Main stylesheet
│   ├── js/
│   │   └── script.js       # JavaScript functionality
│   └── uploads/            # Student photos directory
│       └── .gitkeep
│
└── migrations/              # Database migrations (optional)
```

---

## 🔧 Features & Functionality

### 🎨 Dashboard
- View system statistics (students, hostels, rooms, applications)
- Interactive charts for occupancy and application status
- Quick action buttons for fast navigation
- Recent applications display

### 👨‍🎓 Student Management
- **List Students:** View all students with search and filter
- **Add Student:** Register new students with photo upload
- **Edit Student:** Update student information
- **Delete Student:** Remove student records
- **Search:** Search by name, email, or roll number
- **Pagination:** Navigate through large datasets
- **Photo Upload:** Upload and manage student photographs

### 🏠 Hostel Management
- **Add Hostel:** Create new hostel records
- **Edit Hostel:** Update hostel details
- **Delete Hostel:** Remove hostels
- **View Details:** See hostel information and capacity
- **Manager Assignment:** Assign managers to hostels
- **Occupancy Tracking:** Monitor room occupancy percentage
- **Amenities Management:** List hostel amenities

### 🛏️ Room Management
- **Add Room:** Create new room records
- **Edit Room:** Update room details and status
- **Delete Room:** Remove room records
- **Room Types:** Single, Double, Triple rooms
- **Status Tracking:** Available, Occupied, Maintenance statuses
- **Floor Organization:** Organize by floor number
- **Occupancy Management:** Track capacity and current occupancy

### 📋 Application Management
- **View Applications:** See all hostel applications
- **Filter by Status:** Pending, Approved, Rejected
- **Review Applications:** Approve or reject applications
- **Decision Comments:** Add comments for applications
- **Auto Room Assignment:** Assign rooms when approving
- **Occupancy Updates:** Automatically update room occupancy

---

## 🗄️ Database Schema

### Users Table
```sql
- id (Primary Key)
- username (Unique)
- email (Unique)
- password_hash
- full_name
- role (admin, manager, staff)
- is_active
- created_at
- updated_at
```

### Students Table
```sql
- id (Primary Key)
- name
- email (Unique)
- phone
- roll_number (Unique)
- department
- year
- hostel_id (Foreign Key)
- room_id (Foreign Key)
- photo_url
- guardian_name
- guardian_phone
- address
- admission_date
- status (Active, Inactive, Graduated)
- created_at
- updated_at
```

### Hostels Table
```sql
- id (Primary Key)
- name (Unique)
- location
- address
- phone
- email
- manager_id (Foreign Key)
- total_capacity
- current_occupancy
- description
- amenities
- created_at
- updated_at
```

### Rooms Table
```sql
- id (Primary Key)
- hostel_id (Foreign Key)
- floor_number
- room_number (Unique per hostel)
- room_type (Single, Double, Triple)
- capacity
- current_occupancy
- status (Available, Occupied, Maintenance)
- rent
- description
- created_at
- updated_at
```

### Applications Table
```sql
- id (Primary Key)
- student_id (Foreign Key)
- hostel_id (Foreign Key)
- room_preference
- application_date
- decision_date
- status (Pending, Approved, Rejected)
- reason
- created_at
- updated_at
```

---

## 🔐 Security Features

✅ **Password Hashing** - Using Werkzeug's secure password hashing
✅ **CSRF Protection** - Flask-WTF CSRF tokens
✅ **SQL Injection Prevention** - SQLAlchemy ORM protection
✅ **Session Management** - Secure session handling
✅ **Login Required** - Protected routes with @login_required
✅ **Role-Based Access** - Admin-only operations with @admin_required
✅ **HTTPONLY Cookies** - Session cookies set as HTTPONLY

---

## 🌐 API Endpoints

### Authentication
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET/POST | `/login` | User login |
| GET | `/logout` | User logout |

### Dashboard
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Main dashboard |
| GET | `/dashboard` | Dashboard view |

### Students
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/students` | List all students |
| GET/POST | `/students/add` | Add new student |
| GET/POST | `/students/edit/<id>` | Edit student |
| POST | `/students/delete/<id>` | Delete student |
| GET | `/students/search` | Search students |

### Hostels
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/hostels` | List all hostels |
| GET/POST | `/hostels/add` | Add new hostel |
| GET/POST | `/hostels/edit/<id>` | Edit hostel |
| POST | `/hostels/delete/<id>` | Delete hostel |

### Rooms
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/rooms` | List all rooms |
| GET/POST | `/rooms/add` | Add new room |
| GET/POST | `/rooms/edit/<id>` | Edit room |
| POST | `/rooms/delete/<id>` | Delete room |

### Applications
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/applications` | List applications |
| GET/POST | `/applications/edit/<id>` | Review application |
| POST | `/applications/delete/<id>` | Delete application |

### API Routes
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/rooms/<hostel_id>` | Get rooms for a hostel |

---

## 🎯 Common Tasks

### Adding a New Student
1. Go to Dashboard
2. Click "Add Student" or go to Students → Add Student
3. Fill in the student details
4. Upload a photo (optional)
5. Click "Add Student"

### Creating a Hostel
1. Go to Hostels section
2. Click "Add Hostel"
3. Enter hostel name, location, and capacity
4. Assign a manager
5. Add amenities and description
6. Click "Add Hostel"

### Adding Rooms to Hostel
1. Go to Rooms section
2. Click "Add Room"
3. Select hostel
4. Enter floor number and room number
5. Select room type (Single/Double/Triple)
6. Set capacity and rent
7. Click "Add Room"

### Reviewing Applications
1. Go to Applications section
2. Filter by "Pending" status
3. Click edit button on an application
4. Review student details
5. Choose decision (Approve/Reject)
6. Add comments if needed
7. Click "Submit Decision"

---

## 🐛 Troubleshooting

### Issue: "Port 5000 already in use"
**Solution:** Change the port in `app.py`:
```python
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)  # Change port
```

### Issue: "Database locked" error
**Solution:** 
1. Close the application
2. Delete `hostel_management.db`
3. Reinitialize the database

### Issue: "Module not found" error
**Solution:**
```bash
# Make sure virtual environment is activated
# Reinstall dependencies
pip install -r requirements.txt
```

### Issue: "Photo upload not working"
**Solution:**
1. Create `static/uploads/` directory
2. Check file permissions
3. Verify upload folder path in `app.py`

---

## 📊 Production Deployment

### Before Going Live:

1. **Change Secret Key**
   ```python
   SECRET_KEY = 'your-production-secret-key'
   ```

2. **Update Configuration**
   ```python
   app.config.from_object(config['production'])
   ```

3. **Use Production Database**
   - PostgreSQL recommended
   - Update DATABASE_URL in `.env`

4. **Set Debug to False**
   ```python
   DEBUG = False
   ```

5. **Use HTTPS**
   - Install SSL certificate
   - Configure nginx/Apache

### Deployment Options:

- **Heroku** - Easy cloud deployment
- **AWS** - Scalable cloud hosting
- **DigitalOcean** - Affordable VPS
- **PythonAnywhere** - Python-specific hosting

---

## 📚 Additional Resources

- [Flask Documentation](https://flask.palletsprojects.com/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Bootstrap Documentation](https://getbootstrap.com/docs/)
- [Chart.js Documentation](https://www.chartjs.org/)

---

## 👨‍💻 Contributing

We welcome contributions! Please feel free to submit a Pull Request.

---

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

## 📧 Support

For support and questions:
- Create an Issue on GitHub
- Contact: support@hostelmanagement.com

---

**Made with ❤️ by Harish Kumar**

Last Updated: July 3, 2026
