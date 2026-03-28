import os
import sys
from rich.console import Console
from rich.table import Table

# Sincronizar con el corazón del sistema
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from core.database import Database

console = Console()

class TerritoriosLoader:
    def __init__(self):
        self.db = Database()

    def mostrar_territorios(self):
        console.print("\n[bold cyan]🗺️  MAPA DE TERRITORIOS DOCTRINALES[/]")
        territorios = self.db.obtener_territorios()
        
        if not territorios:
            console.print("[yellow]⚠️ No hay territorios cargados en Sheets.[/]")
            return

        table = Table(title="Doctrina de Acero", border_style="cyan")
        table.add_column("ID", style="dim")
        table.add_column("Nombre", style="bold white")
        table.add_column("Verdad Doctrinal", style="italic")
        table.add_column("Prioridad", justify="center")

        for t in territorios:
            table.add_row(
                str(t.get('ID_TERRITORIO', '')),
                t.get('NOMBRE_TERRITORIO', ''),
                t.get('VERDAD_DOCTRINAL', ''),
                str(t.get('PRIORIDAD_CONTENIDO', ''))
            )
        
        console.print(table)

if __name__ == "__main__":
    loader = TerritoriosLoader()
    loader.mostrar_territorios()
