import os
import sys
from dotenv import load_dotenv

sys.path.append(os.path.abspath(os.path.dirname(os.path.dirname(__file__))))
from core.database import Database
from rich.console import Console

load_dotenv()
console = Console()
db = Database()

def dump_record(id_sesion):
    rows = db.produccion.get_all_values()
    headers = rows[0]
    for r in rows[1:]:
        if r[0] == id_sesion:
            console.print(f"Row: {r}")

if __name__ == "__main__":
    dump_record("PROD_20260307_2044")
