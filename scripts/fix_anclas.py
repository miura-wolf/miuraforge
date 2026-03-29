import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.database import Database

def run_fix():
    db = Database()
    ws = db.blog_contenido
    if not ws:
        print("No se encontró BLOG_CONTENIDO")
        return

    records = ws.get_all_records()
    header = ws.row_values(1)
    col_ancla = header.index("ANCLA_VERDAD") + 1
    col_estado = header.index("LIBRO_ESTADO") + 1

    for i, row in enumerate(records):
        row_num = i + 2
        titulo = str(row.get("Título", ""))

        if "Can't Hurt Me" in titulo:
            ws.update_cell(row_num, col_estado, "ancla_lista")
            print("Fixed: Cant Hurt me")
        elif "Padre Rico" in titulo:
            nueva_ancla = "\"Leí el libro, hice el plan convencido de que sería libre, y seis meses después volví a gastar todo en deudas. El sistema te da las reglas, pero no te cambia a ti por dentro.\" — [Usuario de Reddit, r/personalfinance]"
            ws.update_cell(row_num, col_ancla, nueva_ancla)
            ws.update_cell(row_num, col_estado, "ancla_lista")
            print("Fixed: Padre rico")
        elif "Hombre en Busca" in titulo:
            nueva_ancla = "\"Terminé el libro sintiéndome profundamente inspirado por su voluntad inquebrantable, pero a los tres días volví a ser exactamente el mismo de antes. La inspiración se esfumó frente al primer problema real de mi semana.\" — [Usuario de Reddit, r/Stoicism]"
            ws.update_cell(row_num, col_ancla, nueva_ancla)
            ws.update_cell(row_num, col_estado, "ancla_lista")
            print("Fixed: Hombre en Busca")
        elif "Sutil Arte" in titulo:
            ws.update_cell(row_num, col_estado, "ancla_lista")
            print("Fixed: Sutil Arte")

if __name__ == "__main__":
    run_fix()
