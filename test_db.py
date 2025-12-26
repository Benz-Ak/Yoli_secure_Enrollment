from core.key_manager import KeyManager
from core.crypto_module import YoliCipher
from core.db_controller import DBController

km = KeyManager()
key = km.get_or_create_key()
cipher = YoliCipher(key)

db = DBController(cipher)

print("Testing database save with encrypted data...")
db.save_student("Akoaya Nsengue Benz Brown", "Cyber Security", "benz.nsengue@example.com", "657076332")
