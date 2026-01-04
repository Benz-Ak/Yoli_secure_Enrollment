print("--- START ---")
from core.key_manager import KeyManager
print("1. KeyManager imported")

from core.crypto_module import YoliCipher
print("2. YoliCipher imported")

from core.db_controller import DBController
print("3. DBController imported")

km = KeyManager()
key = km.get_or_create_key()
print(f"4. Key retrieved. Type: {type(key)}")

cipher = YoliCipher(key)
print("5. Cipher tool initialized")

db = DBController(cipher)
print("6. DBController initialized")

print("7. Calling save_student...")
db.save_student(
    full_name="Jean Eone", 
    course="Cybersecurity", 
    email="jean.eone@ecole.com", 
    phone="+237 612 345 678"
)
print("--- END ---")
