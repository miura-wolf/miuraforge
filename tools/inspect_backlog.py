import gspread
from oauth2client.service_account import ServiceAccountCredentials
import re
import sys
from pathlib import Path

# Añadir raíz del proyecto al path
sys.path.append(str(Path(__file__).resolve().parent.parent))
from core.config import CREDENTIALS_PATH


def inspect_backlog():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name(str(CREDENTIALS_PATH), scope)
    client = gspread.authorize(creds)
    sheet = client.open("BD_MiuraForge_Engine")

    ganchos_ws = sheet.worksheet("ARSENAL_GANCHOS")
    records = ganchos_ws.get_all_records()

    # Buscar "francés" o "idiomas" en el backlog
    basura_in_backlog = [
        r
        for r in records
        if re.search(r"francés|idioma|anki|duolingo", str(r.get("GANCHO", "")), re.I)
    ]

    print(f"--- Basura detectada en ARSENAL_GANCHOS ({len(basura_in_backlog)} items) ---")
    for r in basura_in_backlog:
        print(f"ID_SESION: {r.get('ID_SESION')} | GANCHO: {r.get('GANCHO')}")


if __name__ == "__main__":
    inspect_backlog()
