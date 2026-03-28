import sys
import os
sys.path.append(r'd:\YT\MiuraForge')
from core.database import Database

def check():
    db = Database()
    rows = db.produccion.get_all_values()
    headers = rows[0]
    idx_id = headers.index('ID_Sesion')
    idx_fase = headers.index('Fase')
    idx_visual = headers.index('Prompt_Visual')
    
    for row in rows[-5:]:
        if len(row) > idx_id and row[idx_fase] == "MASTER":
            print(f"ID: {row[idx_id][:20]}")
            visual = row[idx_visual] if len(row) > idx_visual else ""
            print(f"Visual: {visual[:100]}...\n")

if __name__ == '__main__':
    check()
