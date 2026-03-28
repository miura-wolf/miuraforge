import gspread
from oauth2client.service_account import ServiceAccountCredentials
import sys
from pathlib import Path

# Añadir raíz del proyecto al path
sys.path.append(str(Path(__file__).resolve().parent.parent))
from core.config import CREDENTIALS_PATH


def search_arquetipos_in_prod():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name(str(CREDENTIALS_PATH), scope)
    client = gspread.authorize(creds)
    sheet = client.open("BD_MiuraForge_Engine")
    ws = sheet.worksheet("PRODUCCION")

    records = ws.get_all_records()
    found = []
    arquetipos = [
        "Arthur Morgan",
        "Joel",
        "Walter White",
        "Maximus",
        "Rocky",
        "Tony Soprano",
        "Chris Gardner",
        "Geralt",
    ]

    for r in records[-20:]:  # Last 20
        guion = str(r.get("Guion", ""))
        for arq in arquetipos:
            if arq.lower() in guion.lower():
                found.append((r.get("ID_Sesion"), arq, guion))

    if found:
        print(f"Found {len(found)} scripts with arquetipos in last 20 records.")
        for id_sesion, arq, guion in found:
            print(f"ID: {id_sesion} | Arquetipo: {arq}\nGuion:\n{guion}\n")
    else:
        print("No arquetipos found in last 20 records.")


if __name__ == "__main__":
    search_arquetipos_in_prod()
