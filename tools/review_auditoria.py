import gspread
from oauth2client.service_account import ServiceAccountCredentials
import sys
from pathlib import Path

# Añadir raíz del proyecto al path
sys.path.append(str(Path(__file__).resolve().parent.parent))
from core.config import CREDENTIALS_PATH


def review_auditoria():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name(str(CREDENTIALS_PATH), scope)
    client = gspread.authorize(creds)
    sheet = client.open("BD_MiuraForge_Engine")
    ws = sheet.worksheet("AUDITORIA")

    records = ws.get_all_records()
    print(f"Total records in AUDITORIA: {len(records)}")

    # Get last 5
    for r in records[-5:]:
        print("-" * 50)
        print(f"ID: {r.get('ID_Master')}")
        print(f"ADN: {r.get('ADN')} | Coherencia: {r.get('Coherencia')}")
        print(f"Fallas: {r.get('Fallas')}")
        print(f"Ajustes: {r.get('Ajustes')}")
        print(f"Guion Optimizado:\n{r.get('Guion_Optimizado')[:150]}...")


if __name__ == "__main__":
    review_auditoria()
