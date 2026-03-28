import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os
import json
import sys
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

# Añadir raíz del proyecto al path
sys.path.append(str(Path(__file__).resolve().parent.parent))
from core.config import CREDENTIALS_PATH

console = Console()


def auditar_google_sheets():
    console.print(
        Panel(
            "⚔️ [bold red]AUDITORÍA TÁCTICA: PUENTE DE MANDO (GOOGLE SHEETS)[/]", border_style="red"
        )
    )

    # 1. Definir Estructura Maestra (Lo que el código espera)
    mapeo_maestro = {
        "LOGISTICA": ["ID_Sesion", "Tema", "Fecha", "Estado", "Metricas"],
        "PRODUCCION": ["ID_Sesion", "Fase", "Guion", "Prompt_Visual", "Voz_Status", "Estado"],
        "MEMORIA": ["Metafora"],
        "AUDITORIA": [
            "ID_Master",
            "Guion_Original",
            "Guion_Optimizado",
            "Intensidad",
            "Ritmo",
            "Coherencia",
            "ADN",
            "Fallas",
            "Ajustes",
            "Fecha",
        ],
        "FUENTES": [
            "ID",
            "ID_SESION",
            "PLATAFORMA",
            "ORIGEN",
            "URL",
            "AUTOR",
            "ENGAGEMENT",
            "FECHA",
            "QUERY",
            "FECHA_EXTRACCION",
        ],
        "INVESTIGACION_PSICOLOGICA": [
            "ID_SEMANA",
            "TEMA",
            "DOLOR_PRINCIPAL",
            "PROBLEMA_RAIZ",
            "FRASES_POTENTES",
            "CREENCIAS",
            "SOLUCION_MIURA",
            "PLATAFORMA",
            "FECHA",
            "ARQUETIPO_SUGERIDO",
        ],
        "DOLORES_MASCULINOS": [
            "ID_DOLOR",
            "CATEGORIA",
            "DESCRIPCION",
            "CREENCIAS",
            "VERDAD",
            "INTENSIDAD",
            "FRECUENCIA",
            "EJEMPLO",
        ],
        "ARSENAL_GANCHOS": ["GANCHO", "PLANTILLA", "INTENSIDAD", "ID_SESION", "FECHA"],
        "CLUSTERS_DOLOR": [
            "cluster_id",
            "nombre_cluster",
            "frecuencia",
            "temas_relacionados",
            "frase_dominante",
            "ultima_actualizacion",
            "freq_7d",
            "freq_30d",
            "tendencia_estado",
        ],
        "FRASES_VIRALES": ["id_frase", "frase", "dolor_asociado", "plataforma", "tema"],
    }

    # 2. Conexión
    try:
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = ServiceAccountCredentials.from_json_keyfile_name(str(CREDENTIALS_PATH), scope)
        client = gspread.authorize(creds)
        spreadsheet_name = "BD_MiuraForge_Engine"
        sheet = client.open(spreadsheet_name)
        worksheets = {w.title.strip().upper(): w for w in sheet.worksheets()}

        table = Table(
            title="📊 ESTADO DE SINCRONIZACIÓN - GOOGLE SHEETS", border_style="bright_black"
        )
        table.add_column("Tabla", style="cyan")
        table.add_column("Estado", style="white")
        table.add_column("Columnas Actuales", style="dim")
        table.add_column("Columnas Requeridas", style="dim")
        table.add_column("Sincronía", justify="center")

        reporte_hallazgos = []

        for nombre_esperado, headers_esperados in mapeo_maestro.items():
            ws = worksheets.get(nombre_esperado.upper())
            if not ws:
                table.add_row(
                    nombre_esperado,
                    "[red]DESAPARECIDA[/]",
                    "N/A",
                    ", ".join(headers_esperados),
                    "❌",
                )
                reporte_hallazgos.append(
                    f"CRÍTICO: Tabla {nombre_esperado} no existe en el documento."
                )
                continue

            headers_reales = [h.strip() for h in ws.row_values(1) if h.strip()]

            # Comparación (Case-insensitive)
            reales_upper = [h.upper() for h in headers_reales]
            esperados_upper = [h.upper() for h in headers_esperados]

            sincronia = "✅"
            missing = [h for h in headers_esperados if h.upper() not in reales_upper]
            extra = [h for h in headers_reales if h.upper() not in esperados_upper]

            if missing:
                sincronia = "⚠️"
                reporte_hallazgos.append(
                    f"DESALINEADA: {nombre_esperado} le faltan: {', '.join(missing)}"
                )

            if extra:
                sincronia = "⚠️"
                reporte_hallazgos.append(
                    f"ADVERTENCIA: {nombre_esperado} tiene columnas extra: {', '.join(extra)}"
                )

            table.add_row(
                nombre_esperado,
                "[green]PRESENTE[/]",
                str(len(headers_reales)),
                str(len(headers_esperados)),
                sincronia,
            )

        console.print(table)

        # Guardar Documentación de Auditoría
        with open("Docs/auditoria_sheets_results.txt", "w", encoding="utf-8") as f:
            f.write("--- REPORTE DE SINCRONÍA GOOGLE SHEETS ---\n")
            f.write(f"Fecha: {json.dumps(str(os.times()))}\n\n")
            for h in reporte_hallazgos:
                f.write(f"- {h}\n")

        console.print(
            f"\n[bold green]✅ Auditoría finalizada. Resultados documentados en Docs/auditoria_sheets_results.txt[/]"
        )

    except Exception as e:
        console.print(f"❌ [Auditor] Error en acceso a Sheets: {e}")


if __name__ == "__main__":
    auditar_google_sheets()
