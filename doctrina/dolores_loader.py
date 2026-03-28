import os
import sys
from rich.console import Console
from rich.table import Table

# Sincronizar con el corazón del sistema
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from core.database import Database

console = Console()

class DoloresLoader:
    def __init__(self):
        self.db = Database()

    def mostrar_dolores(self, categoria=None):
        console.print("\n[bold red]🩸 BIBLIOTECA DE DOLORES MASCULINOS[/]")
        dolores = self.db.obtener_dolores()
        
        if not dolores:
            console.print("[yellow]⚠️ No hay dolores registrados.[/]")
            return

        table = Table(title="Conflictos de Acero", border_style="red")
        table.add_column("Categoría", style="bold cyan")
        table.add_column("Dolor", style="white")
        table.add_column("Creencia Errónea", style="dim")
        table.add_column("Verdad de Acero", style="bold green")

        for d in dolores:
            if categoria and d.get('CATEGORIA', '').lower() != categoria.lower():
                continue
            table.add_row(
                d.get('CATEGORIA', ''),
                d.get('DESCRIPCION_DOLOR', ''),
                d.get('CREENCIA_ERRONEA', ''),
                d.get('VERDAD_ACERO', '')
            )
        
        console.print(table)

if __name__ == "__main__":
    loader = DoloresLoader()
    loader.mostrar_dolores()
