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
        path = os.path.join(self.backup_dir, filename)
        if not os.path.exists(path):
            print(" File not found.")
            return

        print(f"--- Restoring from {filename} ---")
        try:
            with open(path, "r") as f:
                for line in f:
                    parts = line.strip().split("|")
                    if len(parts) < 4: continue

                    name, course = parts[0], parts[1]
                    # Convert Base64 back to encrypted bytes
                    enc_email = base64.b64decode(parts[2])
                    enc_phone = base64.b64decode(parts[3])

                    # Decrypt the bytes back to plain text
                    dec_email = cipher_tool.decrypt_data(enc_email)
                    dec_phone = cipher_tool.decrypt_data(enc_phone)

                    print(f" Restored: {name} | {course} | Email: {dec_email} | Tel: {dec_phone}")
        except Exception as e:
            print(f" Restoration Error: {type(e).__name__} - {e}")