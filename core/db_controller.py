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

    def save_student(self, full_name, course, email, phone):
        """Encrypt and save a student."""
        conn = None
        try:
            # 1. Connexion
            conn = pymysql.connect(**self.config)
            cursor = conn.cursor()

            if self.is_already_enrolled(email):
                print(f" Insertion aborted: {email} is already in the database.")
                return

            # 2. Chiffrement
            enc_email = self.cipher_tool.encrypt_data(email)
            enc_phone = self.cipher_tool.encrypt_data(phone)

            # 3. Insertion SQL
            query = "INSERT INTO students (full_name, course, email, phone) VALUES (%s, %s, %s, %s)"
            values = (full_name, course, enc_email, enc_phone)

            cursor.execute(query, values)
            print(f"Successfull! Student {full_name} saved with data encrypted.")

        except pymysql.Error as err:
            print(f"Database error: {err}")
        except Exception as e:
            print(f"Autre erreur: {e}")
        finally:
            if conn:
                cursor.close()
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