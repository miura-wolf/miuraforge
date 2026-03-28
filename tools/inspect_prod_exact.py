import os
import sys
from dotenv import load_dotenv

sys.path.append(os.path.abspath(os.path.dirname(os.path.dirname(__file__))))
from core.database import Database
from rich.console import Console

load_dotenv()
console = Console()
db = Database()

def inspect_prod_id(id_sesion):
    records = db.produccion.get_all_records()
    for r in records:
        if r.get('ID_Sesion') == id_sesion:
            console.print(f"ID: {r.get('ID_Sesion')}")
            console.print(f"Fase: '{r.get('Fase')}'")
            console.print(f"Guion: {str(r.get('Guion'))[:50]}...")

if __name__ == "__main__":
    inspect_prod_id("PROD_20260307_2044")
