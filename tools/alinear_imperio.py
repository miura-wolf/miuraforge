import sys
import os

# Asegurar que el script encuentre el core del sistema
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.database import Database
from rich.console import Console

console = Console()

def alinear_imperio():
    console.print("\n[bold cyan]⚔️ ALINEADOR DEL IMPERIO: Restauración de Estructura[/]")
    console.print("[cyan]===================================================[/]\n")
    
    db = Database()
    if not db.sheet:
        console.print("[bold red]❌ Error: No se pudo conectar al Puente de Mando.[/]")
        return

    # Mapeo Maestro de Alineación Sagrada
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

    for nombre_hoja, headers_correctos in mapeo_maestro.items():
        try:
            ws = db.sheet.worksheet(nombre_hoja)
            current_headers = [h.strip() for h in ws.row_values(1) if h.strip()]
            
            # Verificación flexible (solo reordenar o añadir si faltan)
            headers_correctos_upper = [h.upper() for h in headers_correctos]
            current_headers_upper = [h.upper() for h in current_headers]
            
            necesita_alinear = False
            if len(current_headers) < len(headers_correctos):
                necesita_alinear = True
            else:
                for i, h in enumerate(headers_correctos_upper):
                    if i >= len(current_headers_upper) or current_headers_upper[i] != h:
                        necesita_alinear = True
                        break

            if necesita_alinear:
                console.print(f"🛠️ [Alineación] Corrigiendo: [bold yellow]{nombre_hoja}[/]")
                ws.update('A1', [headers_correctos])
                console.print(f"✅ [Alineación] {nombre_hoja} sincronizada.")
            else:
                console.print(f"💎 [Alineación] {nombre_hoja} en estado puro.")
        except Exception as e:
            console.print(f"⚠️ [Alineación] Error en {nombre_hoja}: {e}")

    console.print("\n[bold green]✨ Estructura restaurada. Los datos volverán a fluir con orden, Soberano.[/]")

if __name__ == "__main__":
    alinear_imperio()
