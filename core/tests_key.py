from key_manager import KeyManager

km = KeyManager()

try:
    key = km.get_or_create_key()
    print(f"success! the key was retrieve.")
    print(f"size of the key: {len(key)*8} bits")
    print(f"Content (hex) : {key.hex()[:10]}...")
except Exception as e:
    print(f"error while executing: {e}")