from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.exceptions import InvalidTag # Import nécessaire pour détecter la modification
import os

class YoliCipher:
    def __init__(self, key):
        self.aesgcm = AESGCM(key)
    
    def encrypt_data(self, plaintext: str) -> bytes:
        """take a string and return bytes (nonce + ciphertext + tag)."""
        nonce = os.urandom(12) 
        # AESGCM.encrypt génère le ciphertext ET le tag d'authentification automatiquement
        ciphertext = self.aesgcm.encrypt(nonce, plaintext.encode(), None)
        return nonce + ciphertext
    
    def decrypt_data(self, encrypted_data: bytes) -> str:
        """take bytes and return a string. Validates integrity via the GCM tag."""
        try:
            nonce = encrypted_data[:12]
            ciphertext = encrypted_data[12:]
            
            # La méthode decrypt vérifie automatiquement le tag. 
            # Si un seul bit a changé, elle lèvera une exception InvalidTag.
            plaintext = self.aesgcm.decrypt(nonce, ciphertext, None)
            return plaintext.decode('utf-8')
            
        except InvalidTag:
            # C'est ici que tu prouves la sécurité de ton système au jury
            return "ERROR: Integrity compromised - Data modified!"
        except Exception as e:
            return f"Decryption error: {str(e)}"