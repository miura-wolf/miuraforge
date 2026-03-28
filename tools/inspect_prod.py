import os
import sys
from dotenv import load_dotenv

sys.path.append(os.path.abspath(os.path.dirname(os.path.dirname(__file__))))
from core.database import Database
from rich.console import Console

load_dotenv()
console = Console()
db = Database()

def inspect_record(id_sesion):
    records = db.produccion.get_all_records()
    found = False
    for r in records:
        if r.get('ID_Sesion') == id_sesion:
            found = True
            console.print(f"[bold cyan]ID: {id_sesion}[/]")
            console.print(f"Fase: {r.get('Fase')}")
            visual = r.get('Prompt_Visual', '')
            console.print(f"Visual (first 100 chars): {visual[:100]}...")
            console.print(f"Clips detectados: {visual.count('---CLIP')}")
    if not found:
        console.print(f"[red]ID {id_sesion} no encontrado en PRODUCCION.[/]")

if __name__ == "__main__":
    inspect_record("MASIVA_SEMANA_202609_9_1703")
