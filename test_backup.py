from core.key_manager import KeyManager
from core.crypto_module import YoliCipher
from core.db_controller import DBController
from core.backup_manager import BackupManager
import os
# 1. Initialisation de la chaîne de confiance
km = KeyManager()
key = km.get_or_create_key()
cipher = YoliCipher(key)
db = DBController(cipher)

# 2. Initialisation du Backup
backup_tool = BackupManager(db)

print("--- Lancement du Backup Sécurisé ---")
backup_tool.create_encrypted_backup("backup_janvier_2026.enc")

print("\n--- Vérification visuelle ---")
if os.path.exists("./backups/backup_janvier_2026.enc"):
    with open("./backups/backup_janvier_2026.enc", "rb") as f:
        print("Aperçu du fichier (données illisibles) :")
        print(f.read(100)) # Affiche les 100 premiers octets