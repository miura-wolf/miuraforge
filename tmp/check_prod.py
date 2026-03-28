import sys
import os
sys.path.append(r'd:\YT\MiuraForge')
from core.database import Database

def check():
    db = Database()
    rows = db.produccion.get_all_values()
    print("Headers:", rows[0] if rows else "Empty")
    for i in range(1, len(rows)):
        fase = rows[i][1] if len(rows[i]) > 1 else ""
        visual = rows[i][3] if len(rows[i]) > 3 else ""
        if fase == "MASTER":
            print(f"Row {i} - Fase: {fase} | Visual: '{visual}'")

if __name__ == '__main__':
    check()
