import sys
import os

# Asegurar que el script encuentre el core del sistema
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.database import Database
from rich.console import Console
from rich.table import Table

console = Console()

def inspeccionar_imperio():
    console.print("\n[bold cyan]🔍 INSPECTOR MIURA: Auditoría de Salud de Datos[/]")
    console.print("[cyan]==============================================[/]\n")
    
    db = Database()
    if not db.sheet:
        console.print("[bold red]❌ Error: No se pudo conectar a Google Sheets.[/]")
        return

    worksheets = db.sheet.worksheets()
    
    table = Table(title="Radiografía del Puente de Mando")
    table.add_column("Tabla (Hoja)", style="cyan")
    table.add_column("Headers Detectados", style="yellow")
    table.add_column("Estado de Salud", style="green")

    # Estructura Sagrada (Referencia Maestra)
    mapeo_maestro = {
        "LOGISTICA": ["ID_Sesion", "Tema", "Fecha", "Estado", "Metricas"],
        "PRODUCCION": ["ID_Sesion", "Fase", "Guion", "Prompt_Visual", "Voz_Status"],
        "MEMORIA": ["Metafora"],
        "AUDITORIA": ["ID_Master", "Guion_Original", "Guion_Optimizado", "Intensidad", "Ritmo", "Coherencia", "ADN", "Fallas", "Ajustes", "Fecha"],
        "FUENTES": ["ID", "ID_SESION", "PLATAFORMA", "ORIGEN", "URL", "AUTOR", "ENGAGEMENT", "FECHA", "QUERY", "FECHA_EXTRACCION"],
        "INVESTIGACION_PSICOLOGICA": ["ID_SEMANA", "TEMA", "DOLOR_PRINCIPAL", "PROBLEMA_RAIZ", "FRASES_POTENTES", "CREENCIAS", "SOLUCION_MIURA"],
        "DOLORES_MASCULINOS": ["ID_DOLOR", "CATEGORIA", "DESCRIPCION", "CREENCIAS", "VERDAD", "INTENSIDAD", "FRECUENCIA", "EJEMPLO"],
        "ARSENAL_GANCHOS": ["GANCHO", "PLANTILLA", "ID_SESION", "FECHA"]
    }

    for ws in worksheets:
        nombre = ws.title.strip()
        try:
            headers = [h.strip() for h in ws.row_values(1) if h.strip()]
            headers_upper = [h.upper() for h in headers]
            
            esperados = mapeo_maestro.get(nombre)
            if not esperados:
                table.add_row(nombre, f"{len(headers)} cols", "[yellow]Opcional/Auxiliar[/]")
                continue

            # Verificación de integridad
            faltantes = [h for h in esperados if h.upper() not in headers_upper]
            
            if not faltantes:
                resumen = f"✅ ÓPTIMA ({len(headers)} cols)"
            else:
                resumen = f"⚠️ CRÍTICA (Faltan: {', '.join(faltantes)})"

            table.add_row(nombre, ", ".join(headers[:3]) + "...", resumen)
        except Exception as e:
            table.add_row(nombre, "ERROR", f"[red]{str(e)}[/]")

    console.print(table)
    console.print("\n[bold cyan]Uso:[/] Use 'python tools/alinear_imperio.py' para corregir cualquier desvío detectado.")

if __name__ == "__main__":
    inspeccionar_imperio()
