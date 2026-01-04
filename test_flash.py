import pymysql
import sys

print("--- TEST DE CONNEXION ---")
try:
    # Test avec 127.0.0.1 (évite les bugs DNS de localhost sur Windows)
    db = pymysql.connect(
        host="127.0.0.1",
        user="root",
        password="",
        database="yoli_db",
        connect_timeout=3
    )
    print("✅ CONNEXION RÉUSSIE !")
    db.close()
except Exception as e:
    print(f"❌ ÉCHEC : {e}")