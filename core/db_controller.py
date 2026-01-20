import pymysql

class DBController:
    def __init__(self, cipher_tool):
        self.cipher_tool = cipher_tool

        self.config = { 
            'host': '127.0.0.1', 
            'user': 'root',
            'password': '',
            'database': 'yoli_db',
            'connect_timeout': 5,
            'autocommit': True 
        }


    def is_already_enrolled(self, email_to_check):
        """Checks if an email already exists by decrypting entries."""
        conn = self.get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("SELECT email FROM students")
                rows = cursor.fetchall()
                for row in rows:
                    decrypted_email = self.cipher_tool.decrypt_data(row[0])
                    if decrypted_email == email_to_check:
                        return True
            return False
        finally:
            conn.close()

    def get_student_by_name(self, full_name):
        """Retrieve and decipher a student's information."""
        conn = None
        try:
            conn = pymysql.connect(**self.config)
            cursor = conn.cursor()

            query = "SELECT full_name, course, email, phone FROM students WHERE full_name = %s"
            cursor.execute(query, (full_name,))
            result = cursor.fetchone()

            if result:
                full_name, course, enc_email, enc_phone = result

                # Déchiffrement
                dec_email = self.cipher_tool.decrypt_data(enc_email)
                dec_phone = self.cipher_tool.decrypt_data(enc_phone)

                student_info = {
                    'full_name': full_name,
                    'course': course,
                    'email': dec_email,
                    'phone': dec_phone
                }
                return f"{student_info}"
            else:
                print("Student not found.")
                return None
        except Exception as err:
            print(f"Error when reading: {err}")
            return None
        finally:
            if conn:
                cursor.close()
                conn.close()

    def get_connection(self):
        """Returns a new PyMySQL connection for external operations."""
        return pymysql.connect(**self.config)
    
    def get_all_students(self):
        """Retrieves all students and decrypts their data."""
        conn = self.get_connection()
        students = []
        try:
            with conn.cursor() as cursor:
                cursor.execute("SELECT full_name, course, email, phone FROM students")
                rows = cursor.fetchall()
                for row in rows:
                    students.append({
                        'full_name': row[0],
                        'course': row[1],
                        'email': self.cipher_tool.decrypt_data(row[2]),
                        'phone': self.cipher_tool.decrypt_data(row[3])
                    })
            return students
        finally:
            conn.close()
    
    def save_student(self, full_name, course, email, phone):
        """Encrypt and save a student."""
        conn = None
        try:
            conn = self.get_connection()
            # 1. Vérification des doublons
            if self.is_already_enrolled(email):
                return "DUPLICATE" # On retourne un code spécifique

            # 2. Chiffrement et Insertion
            with conn.cursor() as cursor:
                enc_email = self.cipher_tool.encrypt_data(email)
                enc_phone = self.cipher_tool.encrypt_data(phone)
                query = "INSERT INTO students (full_name, course, email, phone) VALUES (%s, %s, %s, %s)"
                cursor.execute(query, (full_name, course, enc_email, enc_phone))
            return True

        except Exception as e:
            print(f"Erreur: {e}")
            return False
        finally:
            if conn: conn.close()

    def delete_student(self, email_to_delete):
        """Supprime un étudiant en déchiffrant pour trouver le bon email."""
        conn = self.get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("SELECT id, email FROM students")
                rows = cursor.fetchall()
                for row in rows:
                    if self.cipher_tool.decrypt_data(row[1]) == email_to_delete:
                        cursor.execute("DELETE FROM students WHERE id = %s", (row[0],))
                        return True
            return False
        finally:
            conn.close()
    
    
    def update_student(self, old_email, new_name, new_course, new_phone):
        conn = self.get_connection()
        try:
            with conn.cursor() as cursor:
                # On retrouve l'étudiant par son email déchiffré
                cursor.execute("SELECT id, email FROM students")
                rows = cursor.fetchall()
                for row in rows:
                    if self.cipher_tool.decrypt_data(row[1]) == old_email:
                        # Re-chiffrement du nouveau téléphone
                        enc_phone = self.cipher_tool.encrypt_data(new_phone)
                        cursor.execute("UPDATE students SET full_name=%s, course=%s, phone=%s WHERE id=%s", 
                                    (new_name, new_course, enc_phone, row[0]))
                        return True
            return False
        finally:
            conn.close()