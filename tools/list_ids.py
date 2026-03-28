import os
import sys
from dotenv import load_dotenv

sys.path.append(os.path.abspath(os.path.dirname(os.path.dirname(__file__))))
from core.database import Database
from rich.console import Console

load_dotenv()
console = Console()
db = Database()

def list_ids():
    records = db.produccion.get_all_records()
    ids = [r.get('ID_Sesion') for r in records if r.get('ID_Sesion')]
    console.print(f"Total IDs: {len(ids)}")
    console.print(f"Unique IDs: {len(set(ids))}")
    console.print(f"Sample IDs: {list(set(ids))[:10]}")

if __name__ == "__main__":
    list_ids()
