import os
import sys
import json
import hashlib
from dotenv import load_dotenv

sys.path.append(os.path.abspath(os.path.dirname(os.path.dirname(__file__))))
from core.database import Database
from rich.console import Console

load_dotenv()
console = Console()
db = Database()

def clear_cache_by_id_robust(id_sesion):
    console.print(f"[bold cyan]🔍 Buscando Guion para ID (Robust): {id_sesion}...[/]")
    
    rows = db.produccion.get_all_records()
    found_guion = None
    for r in rows:
        if str(r.get('ID_Sesion')) == id_sesion:
            # Intentar encontrar guion en cualquier columna que parezca guion
            guion_c = r.get('Guion', '')
            if guion_c and len(guion_c) > 50: # Guiones reales son largos
                found_guion = guion_c
                break
                
    if not found_guion:
        console.print(f"[red]❌ No se encontró guion para ID {id_sesion} en PRODUCCION.[/]")
        return

    # Doctrina Visual
    try:
        with open("prompts/visual.txt", "r", encoding="utf-8") as f:
            doctrina = f.read()
    except:
        doctrina = ""

    # Recoger todos los temas posibles de LOGISTICA y este registro
    temas = [None, r.get('Tema')]
    try:
        log_records = db.sheet.worksheet("LOGISTICA").get_all_records()
        for l in log_records:
            if str(l.get('ID_Sesion')) == id_sesion:
                temas.append(l.get('Tema'))
    except: pass
    
    # Únicos y limpios
    temas = list(set([str(t).strip() if t else None for t in temas]))

    hashes_to_remove = []
    for t in temas:
        # En VisualDirector.py: f"{guion_texto}{tema_global}{instruccion_base}"
        h = hashlib.md5(f"{found_guion}{t}{doctrina}".encode()).hexdigest()
        hashes_to_remove.append(h)
    
    # También probar con 'None' explícito como string y tipo None
    hashes_to_remove.append(hashlib.md5(f"{found_guion}None{doctrina}".encode()).hexdigest())

    cache_path = os.path.join("output", "visual_cache.json")
    if not os.path.exists(cache_path):
        console.print("[yellow]⚠️ La caché está vacía o no existe el archivo.[/]")
        return

    with open(cache_path, "r", encoding="utf-8") as f:
        cache = json.load(f)

    removed = 0
    for h in hashes_to_remove:
        if h in cache:
            del cache[h]
            removed += 1
            console.print(f"[green]✅ Entrada detectada y eliminada ({h}).[/]")

    if removed > 0:
        with open(cache_path, "w", encoding="utf-8") as f:
            json.dump(cache, f, indent=2, ensure_ascii=False)
        console.print(f"[bold green]✨ Caché limpiada con éxito para {id_sesion}.[/]")
        console.print(f"[cyan]Ahora borra la celda 'Prompt_Visual' de este ID en Sheets para forzar la regeneración.[/]")
    else:
        console.print("[yellow]No se encontró el guion específico en la caché.[/]")
        console.print("[dim]Asegúrate de que estás usando el mismo archivo de doctrina que cuando lo generaste.[/]")

if __name__ == "__main__":
    clear_cache_by_id_robust("PROD_20260307_2044")
