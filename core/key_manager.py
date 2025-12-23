import os 
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

class KeyManager:
    def __init__(self, key_directory="./data/keys/", key_name="secret.key"):
        self.key_path = os.path.join(key_directory, key_name)
        # create directory if it doesn't exist
        if not os.path.exists(key_directory):
            os.makedirs(key_directory)
    def get_or_create_key(self):
        #collect the existing key or create a new one
        if os.path.exists(self.key_path):
            with open(self.key_path, "rb") as key_file:
                return key_file.read()
        else:
            #create a AES-256 key(32 bytes / 256 bits)
            new_key = AESGCM.generate_key(bit_length = 256)
            with open(self.key_path, "wb") as key_file:
                key_file.write(new_key)
            print(f"new key generated and save in {self.key_path}")
        return new_key
