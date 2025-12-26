from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import os

class YoliCipher:
    def __init__(self, key):
        self.aesgcm = AESGCM(key)
    
    def encrypt_data(self, plaintext: str)->bytes:
        """take a string a return bytes."""
        nonce = os.urandom(12) #
        ciphertext = self.aesgcm.encrypt(nonce, plaintext.encode(), None)
        return nonce + ciphertext
    
    def decrypt_data(self, encrypted_data: bytes)-> str:
        """take bytes and return a string."""
        nonce = encrypted_data[:12]
        ciphertext = encrypted_data[12:]
        plaintext = self.aesgcm.decrypt(nonce, ciphertext, None)
        return plaintext.decode('utf-8')
    
