import gspread
from oauth2client.service_account import ServiceAccountCredentials
import json
import sys
from pathlib import Path

# Añadir raíz del proyecto al path
sys.path.append(str(Path(__file__).resolve().parent.parent))
from core.config import CREDENTIALS_PATH


def review_production():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name(str(CREDENTIALS_PATH), scope)
    client = gspread.authorize(creds)
    sheet = client.open("BD_MiuraForge_Engine")
    ws = sheet.worksheet("PRODUCCION")

    records = ws.get_all_records()
    print(f"Total records in PRODUCCION: {len(records)}")

    # Get last 5 guiones
    last_records = records[-10:]
    for r in last_records:
        print("-" * 50)
        print(f"ID: {r.get('ID_Sesion')}")
        print(f"Fase: {r.get('Fase')}")
        print(f"Estado: {r.get('Estado')}")
        print(f"Guion Content:\n{r.get('Guion')}")
        print("-" * 50)


if __name__ == "__main__":
    review_production()
