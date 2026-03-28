import os
import sys
from dotenv import load_dotenv

sys.path.append(os.path.abspath(os.path.dirname(os.path.dirname(__file__))))
from core.database import Database
from rich.console import Console

load_dotenv()
console = Console()
db = Database()

def list_ids_fast():
    # Solo leer la primera columna (ID_Sesion)
    ids = db.produccion.col_values(1)
    console.print(f"Total IDs en PRODUCCION: {len(ids) - 1}") # menos encabezado
    console.print(f"Últimos 10 IDs: {ids[-10:]}")
    
    id_buscado = "MASIVA_SEMANA_202609_9_1703"
    if id_buscado in ids:
        row_idx = ids.index(id_buscado) + 1
        console.print(f"[green]✅ ID {id_buscado} encontrado en fila {row_idx}[/]")
    else:
        console.print(f"[red]❌ ID {id_buscado} no encontrado.[/]")

if __name__ == "__main__":
    list_ids_fast()
