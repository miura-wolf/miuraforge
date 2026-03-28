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

def clear_cache_by_id(id_sesion):
    console.print(f"[bold cyan]🔍 Buscando Guion para ID: {id_sesion}...[/]")
    
    # Obtener el guion de PRODUCCION
    records = db.produccion.get_all_records()
    guion_texto = None
    for r in records:
        if r.get('ID_Sesion') == id_sesion and r.get('Fase') == "MASTER":
            guion_texto = r.get('Guion')
            break
            
    if not guion_texto:
        console.print(f"[red]❌ No se encontró guion MASTER para {id_sesion}.[/]")
        return

    # Doctrina Visual
    try:
        with open("prompts/visual.txt", "r", encoding="utf-8") as f:
            doctrina = f.read()
    except:
        doctrina = ""

    # Calcular Hash (tema_global suele ser None o el tema de la sesión)
    # En main.py se pasa tema_global. Vamos a probar con el tema de LOGISTICA.
    tema_global = None
    try:
        logistica = db.sheet.worksheet("LOGISTICA").get_all_records()
        for l in logistica:
            if l.get('ID_Sesion') == id_sesion:
                tema_global = l.get('Tema')
                break
    except: pass

    # Probar hashes con y sin tema
    hashes_to_remove = [
        hashlib.md5(f"{guion_texto}{tema_global}{doctrina}".encode()).hexdigest(),
        hashlib.md5(f"{guion_texto}{None}{doctrina}".encode()).hexdigest()
    ]

    cache_path = "output/visual_cache.json"
    if not os.path.exists(cache_path):
        console.print("[yellow]⚠️ No se encontró archivo de caché.[/]")
        return

    with open(cache_path, "r", encoding="utf-8") as f:
        cache = json.load(f)

    removed = 0
    for h in hashes_to_remove:
        if h in cache:
            del cache[h]
            removed += 1
            console.print(f"[green]✅ Entrada de caché eliminada: {h}[/]")

    if removed > 0:
        with open(cache_path, "w", encoding="utf-8") as f:
            json.dump(cache, f, indent=2, ensure_ascii=False)
        console.print(f"[bold green]✨ Caché actualizada. Ahora puedes re-generar para {id_sesion}.[/]")
    else:
        console.print("[yellow]⚠️ No se encontró ninguna entrada coincidente en la caché para ese guion.[/]")
        console.print("[dim]Esto puede pasar si la doctrina o el tema han cambiado desde la última generación.[/]")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        clear_cache_by_id(sys.argv[1])
    else:
        clear_cache_by_id("PROD_20260307_2044")
