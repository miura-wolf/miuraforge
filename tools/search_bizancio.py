import gspread
from oauth2client.service_account import ServiceAccountCredentials
import sys
from pathlib import Path

# Añadir raíz del proyecto al path
sys.path.append(str(Path(__file__).resolve().parent.parent))
from core.config import CREDENTIALS_PATH


def search_bizancio():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name(str(CREDENTIALS_PATH), scope)
    client = gspread.authorize(creds)
    sheet = client.open("BD_MiuraForge_Engine")

    logistica = sheet.worksheet("LOGISTICA")
    investigacion = sheet.worksheet("INVESTIGACION_PSICOLOGICA")
    ganchos = sheet.worksheet("ARSENAL_GANCHOS")

    print("--- Searching BIZANCIO_202610 ---")

    l_records = logistica.get_all_records()
    l_found = [r for r in l_records if "BIZANCIO" in str(r.get("ID_Sesion", ""))]
    print(f"In LOGISTICA: {l_found}")

    i_records = investigacion.get_all_records()
    i_found = [r for r in i_records if "BIZANCIO" in str(r.get("ID_SEMANA", ""))]
    print(f"In INVESTIGACION_PSICOLOGICA: {len(i_found)} records found")

    g_records = ganchos.get_all_records()
    g_found = [r for r in g_records if "BIZANCIO_202610" in str(r.get("ID_SESION", ""))]
    print(f"In ARSENAL_GANCHOS: {len(g_found)} records found")


if __name__ == "__main__":
    search_bizancio()
