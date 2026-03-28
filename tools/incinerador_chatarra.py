import gspread
from oauth2client.service_account import ServiceAccountCredentials
import re
import sys
from pathlib import Path

# Añadir raíz del proyecto al path
sys.path.append(str(Path(__file__).resolve().parent.parent))
from core.config import CREDENTIALS_PATH


def incinerar_basura():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name(str(CREDENTIALS_PATH), scope)
    client = gspread.authorize(creds)
    sheet = client.open("BD_MiuraForge_Engine")

    # Lista de términos basura (Fuera de foco)
    basura_patterns = [
        r"francés",
        r"idiomas",
        r"duolingo",
        r"cocina",
        r"recetas",
        r"maquillaje",
        r"belleza",
        r"farándula",
        r"política",
        r"salud pública",
        r"Ahab",
        r"ballena",
        r"Capitán Ahab",
        r"Anki",
        r"curso",
        r"clase de",
        r"puntuación global",
        r"supera el umbral",
        r"guion es operativo",
        r"ya es óptimo",
        r"fase individual poderosa",
    ]
    regex_basura = re.compile("|".join(basura_patterns), re.IGNORECASE)

    tablas = [
        "PRODUCCION",
        "AUDITORIA",
        "INVESTIGACION_PSICOLOGICA",
        "LOGISTICA",
        "ARSENAL_GANCHOS",
    ]

    for nombre in tablas:
        try:
            ws = sheet.worksheet(nombre)
            records = ws.get_all_values()
            if not records:
                continue

            headers = records[0]
            filas_a_borrar = []

            print(f"🔍 Escaneando {nombre}...")

            # Recorremos de abajo hacia arriba para no alterar índices al borrar (aunque aquí limpiaremos celdas o eliminaremos filas)
            for i, row in enumerate(records[1:], start=2):
                contenido_fila = " ".join([str(val) for val in row])
                if regex_basura.search(contenido_fila):
                    print(f"🗑️ Detectada basura en {nombre} (Fila {i}): {contenido_fila[:50]}...")
                    filas_a_borrar.append(i)

            if filas_a_borrar:
                # Borrarlos de uno en uno desde el final para mantener estabilidad
                for row_idx in sorted(filas_a_borrar, reverse=True):
                    ws.delete_rows(row_idx)
                print(f"✅ Se han incinerado {len(filas_a_borrar)} registros de {nombre}.")
            else:
                print(f"✨ {nombre} está limpio de chatarra.")

        except Exception as e:
            print(f"⚠️ Error procesando {nombre}: {e}")


if __name__ == "__main__":
    incinerar_basura()
