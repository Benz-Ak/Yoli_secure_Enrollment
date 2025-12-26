from core.key_manager import KeyManager
from core.crypto_module import YoliCipher

km = KeyManager()
key = km.get_or_create_key()

cipher = YoliCipher(key)

email = "user@example.com"
print(f"Original Email: {email}")
encrypted_email = cipher.encrypt_data(email)
print(f"Encrypted Email: {encrypted_email.hex()}")

decrypted_email = cipher.decrypt_data(encrypted_email)
print(f"Decrypted Email: {decrypted_email}")
