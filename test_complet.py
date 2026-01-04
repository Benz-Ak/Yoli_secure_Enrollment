from core.key_manager import KeyManager
from core.crypto_module import YoliCipher
from core.db_controller import DBController
from core.backup_manager import BackupManager

# 1. SETUP
km = KeyManager()
key = km.get_or_create_key()
cipher = YoliCipher(key)
db = DBController(cipher)
backup_tool = BackupManager(db)

# 2. ACTIONS
print("--- ÉTAPE 1 : Sauvegarde en Base de Données ---")
db.save_student("John Doe", "M1 Network", "benz@yoli.com", "237000000")

print("\n--- ÉTAPE 2 : Création du Backup Chiffré ---")
backup_name = "demo_fin.enc"
backup_tool.create_encrypted_backup(backup_name)

print("\n--- ÉTAPE 3 : Test de Restauration (Déchiffrement du Backup) ---")
backup_tool.restore_from_file(backup_name, cipher)