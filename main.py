import customtkinter as ctk
from tkinter import messagebox

# Import de tes modules
from core.key_manager import KeyManager
from core.crypto_module import YoliCipher
from core.db_controller import DBController
from core.backup_manager import BackupManager
from main_gui import YoliSecureApp

class LoginWindow(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("Authentification YOLI SECURE")
        self.geometry("400x350")
        
        # Centrer la fenêtre
        self.after(100, self.lift) # Aide à corriger les erreurs de focus

        ctk.CTkLabel(self, text="🛡️ Accès Système", font=("Arial", 24, "bold")).pack(pady=30)
        
        self.pwd_entry = ctk.CTkEntry(self, placeholder_text="Mot de passe admin", show="*", width=280, height=40)
        self.pwd_entry.pack(pady=10)
        self.pwd_entry.bind("<Return>", lambda event: self.check_password()) # Entrée pour valider

        self.btn_login = ctk.CTkButton(self, text="Déverrouiller", command=self.check_password, height=40)
        self.btn_login.pack(pady=20)

    def check_password(self):
        # Vérification simple (admin123)
        if self.pwd_entry.get() == "admin123":
            self.withdraw() # Cache la fenêtre de login proprement au lieu de destroy()
            self.launch_main_app()
        else:
            messagebox.showerror("Échec", "Mot de passe incorrect !")

    def launch_main_app(self):
        try:
            # Initialisation des modules
            km = KeyManager()
            key = km.get_or_create_key()
            cipher = YoliCipher(key)
            db = DBController(cipher)
            backup = BackupManager(db)
            
            # Lancement de l'interface principale
            main_app = YoliSecureApp(cipher, db, backup)
            
            # Si on ferme l'app principale, on ferme tout
            main_app.protocol("WM_DELETE_WINDOW", lambda: self.quit_all(main_app))
            main_app.mainloop()
            
        except Exception as e:
            messagebox.showerror("Erreur Système", f"Erreur d'initialisation : {e}")
            self.destroy()

    def quit_all(self, main_app):
        main_app.destroy()
        self.destroy()

if __name__ == "__main__":
    login = LoginWindow()
    login.mainloop()