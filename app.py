from flask import Flask, render_template, request, redirect, url_for, flash, send_file,session
import os

# Import de tes classes backend existantes
from core.key_manager import KeyManager
from core.crypto_module import YoliCipher
from core.db_controller import DBController
from core.backup_manager import BackupManager

app = Flask(__name__)
app.secret_key = "yoli_secure_master_key_123" # Nécessaire pour les messages flash

# Identifiants administrateur (En production, ils seraient hachés en BDD)
ADMIN_USER = "admin"
ADMIN_PASS = "YoliSecure2026"

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if username == ADMIN_USER and password == ADMIN_PASS:
            session['logged_in'] = True
            flash("Welcome back, Administrator.", "success")
            return redirect(url_for('index'))
        else:
            flash("Invalid credentials. Access denied.", "danger")
            
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('login'))

# --- PROTECTEUR D'ACCÈS (Middleware) ---
@app.before_request
def require_login():
    allowed_routes = ['login', 'static']
    if 'logged_in' not in session and request.endpoint not in allowed_routes:
        return redirect(url_for('login'))

# --- INITIALISATION DU BACKEND ---
try:
    km = KeyManager()
    key = km.get_or_create_key()
    cipher = YoliCipher(key)
    db = DBController(cipher)
    backup = BackupManager(db)
    print("[OK] Backend Yoli Secure initialisé avec succès.")
except Exception as e:
    print(f"[ERREUR] Échec de l'initialisation : {e}")

# --- ROUTES ---

@app.route('/')
def index():
    """Page d'accueil : Formulaire d'enrôlement."""
    return render_template('index.html', active_page='enrollment')

@app.route('/enroll', methods=['POST'])
def enroll():
    """Traite l'inscription d'un nouvel étudiant (Chiffrement + Save)."""
    full_name = request.form.get('full_name')
    course = request.form.get('course')
    email = request.form.get('email')
    phone = request.form.get('phone')

    if not all([full_name, course, email, phone]):
        flash("All fields are required!", "danger")
        return redirect(url_for('index'))

    # Appel à ton DBController (qui utilise YoliCipher en interne)
    result = db.save_student(full_name, course, email, phone)

    if result == "DUPLICATE":
        flash(f"Security Alert: Email {email} already exists in database!", "warning")
    elif result is True:
        flash("Student data successfully encrypted (AES-GCM) and saved.", "success")
    else:
        flash("A technical error occurred during encryption.", "danger")
    
    return redirect(url_for('index'))

@app.after_request
def add_header(response):
    """
    Force le navigateur à ne pas mettre les pages en cache.
    Ceci empêche l'accès via le bouton 'Retour' après déconnexion.
    """
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response

@app.route('/database')
def database():
    """Affiche les données déchiffrées en temps réel."""
    students = db.get_all_students() # Ton backend déchiffre déjà ici
    return render_template('database.html', students=students, active_page='database')

@app.route('/delete/<email>')
def delete_student(email):
    """Supprime un étudiant."""
    if db.delete_student(email):
        flash(f"Record for {email} deleted successfully.", "success")
    else:
        flash("Error during deletion.", "danger")
    return redirect(url_for('database'))

@app.route('/keymanager')
def key_manager():
    """Affiche les infos sur la clé de chiffrement."""
    # On récupère quelques infos via KeyManager
    key_info = {
        "status": "Active",
        "algorithm": "AES-256-GCM",
        "location": "Local Storage (Encrypted)",
        "key_preview": "************************" # Ne jamais afficher la vraie clé !
    }
    return render_template('keymanager.html', key_info=key_info, active_page='keymanager')

@app.route('/backup')
def backup_view():
    """Gestion des sauvegardes."""
    return render_template('backup.html', active_page='backup')

@app.route('/run-backup')
def run_backup():
    """Exécute la création du backup chiffré."""
    try:
        backup.create_encrypted_backup()
        flash("Encrypted backup file created: students_backup.enc", "success")
    except Exception as e:
        flash(f"Backup failed: {e}", "danger")
    return redirect(url_for('backup_view'))

if __name__ == '__main__':
    app.run(debug=True, port=5000)