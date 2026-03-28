import os
import sys
from rich.console import Console
from rich.table import Table

# Sincronizar con el corazón del sistema
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from core.database import Database

console = Console()

class GanchosLoader:
    def __init__(self):
        self.db = Database()

    def mostrar_ganchos(self):
        console.print("\n[bold yellow]⚓ ARSENAL DE GANCHOS (HOOKS)[/]")
        ganchos = self.db.obtener_ganchos()
        
        if not ganchos:
            console.print("[yellow]⚠️ Arsenal vacío.[/]")
            return

        table = Table(title="Biblioteca de Alto CTR", border_style="yellow")
        table.add_column("Tipo", style="bold cyan")
        table.add_column("Texto", style="white")
        table.add_column("Uso", style="dim")
        table.add_column("Intensidad", justify="center")

        for g in ganchos:
            table.add_row(
                g.get('TIPO_GANCHO', ''),
                g.get('TEXTO', ''),
                g.get('USO_RECOMENDADO', ''),
                str(g.get('INTENSIDAD', ''))
            )
        
        console.print(table)

if __name__ == "__main__":
    loader = GanchosLoader()
    loader.mostrar_ganchos()
