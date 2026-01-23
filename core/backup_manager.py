import os
import base64

class BackupManager:
    def __init__(self, db_controller):
        self.db = db_controller
        self.backup_dir = "./backups/"
        if not os.path.exists(self.backup_dir):
            os.makedirs(self.backup_dir)

    def create_encrypted_backup(self, filename="students_backup.enc"):
        """Extracts data from DB and stores it as Base64 encoded strings."""
        path = os.path.join(self.backup_dir, filename)
        conn = None
        try:
            conn = self.db.get_connection()
            with conn.cursor() as cursor:
                cursor.execute("SELECT full_name, course, email, phone FROM students")
                rows = cursor.fetchall()

            with open(path, "w") as f: # Opening in text mode
                for row in rows:
                    # Encode binary encrypted data to Base64 (Safe for text files)
                    b64_email = base64.b64encode(row[2]).decode()
                    b64_phone = base64.b64encode(row[3]).decode()
                    # Use | as a separator to avoid issues with commas in names
                    f.write(f"{row[0]}|{row[1]}|{b64_email}|{b64_phone}\n")
            
            print(f" Encrypted Backup created successfully: {path}")
        except Exception as e:
            print(f" Backup failed: {e}")
        finally:
            if conn: conn.close()

    def restore_from_file(self, filename, cipher_tool):
        """Reads the backup file, decodes Base64, and decrypts the data."""
        # 1. Vérifier si le chemin est complet ou relatif
        if os.path.isabs(filename):
            path = filename
        else:
            path = os.path.join(self.backup_dir, filename)

        if not os.path.exists(path):
            print(f" [!] File not found at: {path}")
            return False

        print(f"--- Restoring from {os.path.basename(path)} ---")
        
        try:
            # 2. On utilise 'r' car les données sont en Base64 (texte) 
            # mais on gère l'encodage pour éviter les erreurs de caractères
            with open(path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line: continue  # Saute les lignes vides
                    
                    parts = line.split("|")
                    if len(parts) < 4: 
                        print(" [!] Skipping malformed line.")
                        continue

                    name, course = parts[0], parts[1]
                    
                    try:
                        # 3. Décodage Base64 vers Bytes
                        enc_email = base64.b64decode(parts[2])
                        enc_phone = base64.b64decode(parts[3])

                        # 4. Déchiffrement AES-GCM
                        dec_email = cipher_tool.decrypt_data(enc_email)
                        dec_phone = cipher_tool.decrypt_data(enc_phone)

                        # 5. Réinsertion en base de données (Crucial pour la restauration)
                        self.db.save_student(name, course, dec_email, dec_phone)
                        
                        print(f" [+] Decrypted: {name} | {dec_email}")
                        
                    except Exception as e:
                        print(f" [!] Decryption failed for {name}: {e}")
                        return False # Arrêt si la clé est invalide
            return True
            
        except Exception as e:
            print(f" [!] File Access Error: {e}")
            return False