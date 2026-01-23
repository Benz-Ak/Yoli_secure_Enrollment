from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.security import check_password_hash, generate_password_hash
import os

# Backend logic imports
from core.key_manager import KeyManager
from core.crypto_module import YoliCipher
from core.db_controller import DBController
from core.backup_manager import BackupManager

app = Flask(__name__)
app.secret_key = "yoli_secure_master_key_123" # Required for session security

# Static Admin Credentials
ADMIN_USER = "admin"
ADMIN_PASS = "YoliSecure2026"

# --- BACKEND INITIALIZATION ---
try:
    km = KeyManager()
    key = km.get_or_create_key()
    cipher = YoliCipher(key)
    db = DBController(cipher)
    backup = BackupManager(db)
    print("[OK] Yoli Secure Backend successfully initialized.")
except Exception as e:
    print(f"[ERROR] Critical failure during initialization: {e}")

# --- SECURITY MIDDLEWARE ---
@app.before_request
def require_login():
    """Protects admin pages while keeping enrollment public."""
    # List of routes that do NOT require authentication
    public_routes = ['login', 'static', 'index_public', 'enroll']
    
    if 'logged_in' not in session and request.endpoint not in public_routes:
        return redirect(url_for('login'))

@app.after_request
def add_security_headers(response):
    """Prevents back-button caching of sensitive encrypted data."""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response

# --- AUTHENTICATION ROUTES ---

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        role = request.form.get('role')

        if role == 'admin':
            if username == ADMIN_USER and password == ADMIN_PASS:
                session['logged_in'] = True
                session['role'] = 'admin'
                flash("Admin Authentication Successful.", "success")
                return redirect(url_for('index_admin'))
            else:
                flash("Invalid Admin Credentials.", "danger")

        elif role == 'student':
            student = db.get_student_by_email(username)
            # Assuming you stored a hashed password for students
            if student and check_password_hash(student.get('password_hash', ''), password):
                session['logged_in'] = True
                session['role'] = 'student'
                session['user_data'] = student
                flash(f"Welcome back, {student['full_name']}!", "success")
                return redirect(url_for('index_public'))
            else:
                flash("Student Access Denied: Incorrect email or password.", "danger")
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# --- NAVIGATION ROUTES ---

@app.route('/')
def index_public():
    """The Landing Page for all students (public_enroll.html)."""
    return render_template('public_enroll.html')

@app.route('/admin/dashboard')
def index_admin():
    """The Admin main page for staff enrollment (index.html)."""
    return render_template('index.html', active_page='enrollment')

# --- UNIFIED LOGIC: ENROLLMENT + AUTO-BACKUP ---

@app.route('/enroll', methods=['POST'])
def enroll():
    # 1. Fetch form data
    full_name = request.form.get('full_name')
    course = request.form.get('course')
    email = request.form.get('email')
    phone = request.form.get('phone')

    if not all([full_name, course, email, phone]):
        flash("Registration Error: All fields are mandatory.", "danger")
        return redirect(request.referrer)

    # 2. Encrypt & Save (AES-256 GCM logic via Controller)
    result = db.save_student(full_name, course, email, phone)

    if result == "DUPLICATE":
        flash(f"Security Conflict: Email {email} is already in the system.", "warning")
    elif result is True:
        # --- AUTOMATIC BACKUP TRIGGER ---
        try:
            # Generates an encrypted .enc file immediately after save
            backup.create_encrypted_backup() 
            flash("Success: Student data encrypted and Auto-Backup created.", "success")
        except Exception as e:
            flash("Data saved, but automated backup failed.", "warning")
            print(f"Backup Error: {e}")
    else:
        flash("Encryption Failure: System unable to process sensitive data.", "danger")
    
    # Stay on the same page (Public or Admin) after submission
    return redirect(request.referrer)

# --- ADMINISTRATIVE DATA VIEWS ---

@app.route('/database')
def database_view():
    """Admin view to see decrypted records (database.html)."""
    students = db.get_all_students()
    return render_template('database.html', students=students, active_page='database')

@app.route('/delete/<email>')
def delete_student(email):
    if db.delete_student(email):
        flash("Encrypted record successfully purged.", "success")
        backup.create_encrypted_backup() # Refresh backup after deletion
    return redirect(url_for('database_view'))

# --- BACKUP RESTORATION LOGIC ---

@app.route('/restoration')
def restoration_view():
    """View for manual file restoration (restore.html)."""
    return render_template('restore.html', active_page='restoration')

@app.route('/restore', methods=['POST'])
def restore_database():
    if 'backup_file' not in request.files:
        flash("No backup file selected.", "danger")
        return redirect(url_for('restoration_view'))
    
    file = request.files['backup_file']
    if file and file.filename.endswith('.enc'):
        # Secure temp storage for restoration
        temp_path = os.path.join(os.getcwd(), "temp_restore", file.filename)
        os.makedirs(os.path.dirname(temp_path), exist_ok=True)
        file.save(temp_path)
        
        # Restoration call using the YoliCipher instance
        if backup.restore_from_file(temp_path, cipher):
            flash("Database integrity restored successfully!", "success")
            os.remove(temp_path) # Clean up
            return redirect(url_for('database_view'))
        else:
            flash("Restoration Error: Key mismatch or corrupted file.", "danger")
            
    return redirect(url_for('restoration_view'))

# --- SERVER BOOT ---
if __name__ == '__main__':
    # Running on default port 5000
    app.run(debug=True, port=5000)