import os
import sys
from dotenv import load_dotenv

sys.path.append(os.path.abspath(os.path.dirname(os.path.dirname(__file__))))
from core.database import Database
from rich.console import Console

load_dotenv()
console = Console()
db = Database()

def search_id_everywhere(id_sesion):
    console.print(f"Buscando {id_sesion} en todas las tablas...")
    for sheet_name in ["LOGISTICA", "PRODUCCION", "MEMORIA", "AUDITORIA", "DESPLIEGUE"]:
        try:
            ws = db.sheet.worksheet(sheet_name)
            col1 = ws.col_values(1)
            if id_sesion in col1:
                console.print(f"[green]✅ Encontrado en {sheet_name}![/]")
        except: pass

if __name__ == "__main__":
    search_id_everywhere("PROD_20260307_2044")
