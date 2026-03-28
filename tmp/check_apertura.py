import os
import sys
import json
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from core.database import Database

db = Database()
try:
    # Intentar obtener todos los registros de PRODUCCION
    records = db.produccion.get_all_records()
    apertura_records = [r for r in records if "Apertura" in str(r.get("id_master", ""))]
    print(json.dumps(apertura_records, indent=2))
except Exception as e:
    print(f"Error: {e}")
