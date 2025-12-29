import mysql.connector

class DBController:
    def __init__(self, cipher_tool):
        """we give it the encryption tool to use."""
        self.cipher_tool = cipher_tool

        self.config = { 
            'host':'localhost',
            'user':'root',
            'password':'',
            'database':'yoli_db'
        }
    
    def save_student(self, full_name, course, email, phone):
        """save a student to the database, encrypting sensitive data."""
        conn = None
        try:
            # connexion to MySQL
            conn = mysql.connector.connect(**self.config)
            cursor = conn.cursor()

            #data encryption using the cipher tool
            enc_email = self.cipher_tool.encrypt_data(email)
            enc_phone = self.cipher_tool.encrypt_data(phone)

            # SQL Insert
            query = "INSERT INTO students (full_name, course, email, phone) VALUES (%s, %s, %s, %s)"
            values = (full_name, course, enc_email, enc_phone)

            #execution
            cursor.execute(query, values)
            conn.commit()
            print(f"Successfull! Student {full_name} saved with data encrypted.")
        except mysql.connector.Error as err:
            print(f"database error: {err}")
        finally:
            if conn and conn.is_connected():
                cursor.close()
                conn.close()
    
    def get_student_by_name(self, full_name):
        """retrieve a student and decrypts his informations for display"""
        conn = None
        try:
            conn = mysql.connector.connect(**self.config)
            cursor = conn.cursor()

            query = "SELECT full_name, course, email, phone FROM students WHERE full_name = %s"
            cursor.execute(query,(full_name,))
            result = cursor.fetchone()

            if result:
                full_name, course, enc_email, enc_phone = result

                #decryption of sensitive data
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
            if conn and conn.is_connected():
                cursor.close()
                conn.close()