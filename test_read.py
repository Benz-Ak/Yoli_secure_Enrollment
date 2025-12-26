from core.key_manager import KeyManager
from core.crypto_module import YoliCipher
from core.db_controller import DBController

km = KeyManager()
key = km.get_or_create_key()
cipher = YoliCipher(key)

db = DBController(cipher)

print("Testing database selection and decryption...")

student_name = db.get_student_by_name("akoaya nsengue benz brown")

if isinstance(student_name, dict):
    print("Name: {student_name['full_name']}")
    print("Course: {student_name['course']}")
    print("Email: {student_name['email']}")
    print("Phone: {student_name['phone']}")
else:
    print(student_name)
