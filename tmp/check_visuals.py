import sys
import os
sys.path.append(r'd:\YT\MiuraForge')
from core.database import Database

def check():
    db = Database()
    rows = db.produccion.get_all_values()
    headers = rows[0]
    idx_id = headers.index('ID_Sesion')
    idx_visual = headers.index('Prompt_Visual')
    
    print("Revisando los guiones solicitados...")
    for row in rows[1:]:
        if len(row) > idx_id:
            row_id = row[idx_id]
            visual = row[idx_visual] if len(row) > idx_visual else ""
            if row_id in ("PROD_20260310_2320", "PROD_20260307_2118", "MASIVA_SEMANA_202609_8"):
                print(f"ID: {row_id}")
                print(f"Visual (primeros 100 caracteres): {visual[:100]}...")
                print("-" * 40)

if __name__ == '__main__':
    check()
