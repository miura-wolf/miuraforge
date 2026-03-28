import os
import sys
import re
import json
import time
from dotenv import load_dotenv

# Configuración de rutas
BASE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
sys.path.append(BASE_DIR)

from rich.console import Console
from rich.progress import track
from core.database import Database
from core.visual_director import VisualDirector
import tools.image_forge as img_forge

load_dotenv()
console = Console()

def parsear_guiones_apertura(md_path):
    """
    Parsea Guiones_Apertura_Canal.md y extrae ID y Guion.
    También captura los prompts de referencia si existen.
    """
    if not os.path.exists(md_path):
        console.print(f"[red]❌ No se encontró: {md_path}[/]")
        return []

    with open(md_path, "r", encoding="utf-8") as f:
        contenido = f.read()

    secciones = re.split(r'(?=^## 🎬)', contenido, flags=re.MULTILINE)
    resultado = []

    for seccion in secciones:
        seccion = seccion.strip()
        if not seccion.startswith('## 🎬'):
            continue

        m_id = re.search(r'\*\*ID:\*\*\s*`([^`]+)`', seccion)
        if not m_id:
            continue
        id_sesion = m_id.group(1).strip()

        # Extraer Guion
        match_guion = re.search(r'Objetivo:.*?\n\s*\n(.*?)(?=\n\n🎬|\n\nCopiar y pegar|\n\n---)', seccion, re.DOTALL)
        if match_guion:
            guion_texto = match_guion.group(1).strip()
            guion_texto = re.sub(r'^>\s*', '', guion_texto, flags=re.MULTILINE)
        else:
            guion_texto = ""

        # Extraer Prompts de Referencia
        prompts_ref = re.findall(r'Cinematic 9:16 vertical video\..*?(?=\n\n|\n---|\Z)', seccion, re.DOTALL)
        prompts_ref_text = "\n".join([p.strip() for p in prompts_ref])

        resultado.append({
            'id_sesion': id_sesion,
            'guion': guion_texto,
            'prompts_referencia': prompts_ref_text
        })

    return resultado

def forjar_apertura():
    console.print("\n[bold cyan]⚔️ APERTURA FULL FORGE — Producción Completa ⚔️[/]")
    db = Database()
    director_v = VisualDirector(db_manager=db)
    
    md_path = os.path.join(BASE_DIR, "Docs", "Guiones_Apertura_Canal.md")
    items = parsear_guiones_apertura(md_path)
    
    if not items:
        console.print("[yellow]⚠️ No hay guiones para procesar.[/]")
        return

    # 1. Guardar en PRODUCCION y Generar Prompts Duales
    console.print(f"\n[bold]🛠️ PASO 1 & 2: Registro en PRODUCCION y Generación de Prompts Duales[/]")
    
    doctrina_visual = director_v.leer_doctrina()
    
    for item in items:
        id_s = item['id_sesion']
        guion = item['guion']
        ref_prompts = item['prompts_referencia']
        
        console.print(f"🔹 Procesando [cyan]{id_s}[/]...")
        
        # Registrar en PRODUCCION (Fase MASTER)
        # Usamos guardar_fase(timestamp, fase, guion, visual, ruta_local, estado="pendiente")
        # En este caso timestamp es el id_s
        db.guardar_fase(id_s, "MASTER", guion, "PENDIENTE", "N/A", "aprobado")
        
        # Generar Prompts Duales (Imagen + Animación)
        # Pedimos al LLM que se base en el guion y que use los prompts de referencia si son útiles
        duracion = director_v.estimar_duracion_segundos(guion)
        num_clips = max(1, round(duracion / 6))
        
        instruccion = f"""
        Misión:
        1. Toma el siguiente guion de APERTURA y divídelo en EXACTAMENTE {num_clips} fragmentos.
        2. Para cada fragmento, genera el bloque dual: [IMAGEN] + [ANIMACIÓN].
        3. IMPORTANTE: Usa estos PROMPTS DE REFERENCIA para inspirar la estética, pero adáptalos al formato dual:
        
        --- PROMPTS DE REFERENCIA ---
        {ref_prompts}
        
        --- GUION A PROCESAR ---
        {guion}
        """
        
        prompt_llm = f"{doctrina_visual}\n\n{instruccion}"
        
        try:
            console.print(f"   📡 Generando prompts duales para {num_clips} clips...")
            respuesta = director_v.brain.generate(prompt_llm).strip()
            
            # Limpiar markdown
            respuesta = re.sub(r'^```(?:json|markdown)?\s*', '', respuesta, flags=re.MULTILINE)
            respuesta = re.sub(r'\s*```$', '', respuesta, flags=re.MULTILINE)
            
            # Guardar en PRODUCCION
            # Buscamos la fila para actualizar el Prompt_Visual
            try:
                # Obtenemos todas las filas para encontrar el índice
                rows = db.produccion.get_all_values()
                headers = rows[0]
                idx_id = headers.index('ID_Sesion') if 'ID_Sesion' in headers else 0
                idx_fase = headers.index('Fase') if 'Fase' in headers else 1
                idx_visual = headers.index('Prompt_Visual') if 'Prompt_Visual' in headers else 3
                
                fila_idx = -1
                for i, r in enumerate(rows):
                    if i == 0: continue
                    if str(r[idx_id]) == id_s and str(r[idx_fase]) == "MASTER":
                        fila_idx = i + 1
                        break
                
                if fila_idx != -1:
                    db.produccion.update_cell(fila_idx, idx_visual + 1, respuesta)
                    console.print(f"   ✅ PRODUCCION actualizada con prompts duales.")
                else:
                    console.print(f"   [yellow]⚠️ No se encontró la fila en PRODUCCION para actualizar visuales.[/]")
            except Exception as e:
                console.print(f"   [red]⚠️ Error actualizando celda: {e}[/]")

            # 3. Generar Imágenes y TXT (Fichas de Animación)
            console.print(f"   🎨 Generando imágenes...")
            clips = img_forge.parsear_clips_duales(respuesta)
            
            out_base = os.path.join(BASE_DIR, "output", "imagenes_shorts", id_s)
            os.makedirs(out_base, exist_ok=True)
            
            for j, clip in enumerate(clips, start=1):
                img_path = os.path.join(out_base, f"clip_{j:02d}.png")
                ficha_path = os.path.join(out_base, f"clip_{j:02d}_ANIMACION.txt")
                
                # Usamos motor AUTO (NVIDIA -> Google -> Nebius)
                exito = img_forge.generar_imagen(clip["imagen_prompt"], img_path, motor="auto")
                
                if exito:
                    with open(ficha_path, "w", encoding="utf-8") as f:
                        f.write(f"=== FICHA DE ANIMACIÓN — {id_s} — Clip {j} ===\n\n")
                        f.write(f"GUION:\n{clip['fragmento']}\n\n")
                        f.write(f"DIRECTIVA DE ANIMACIÓN:\n{clip['animacion']}\n\n")
                        f.write(f"PROMPT ORIGINAL:\n{clip['imagen_prompt']}\n")
                    console.print(f"      🖼️  Clip {j}: OK")
                else:
                    console.print(f"      ❌ Clip {j}: FALLÓ")
                    
        except Exception as e:
            console.print(f"   [red]❌ Fallo en {id_s}: {e}[/]")

    console.print("\n[bold green]🏁 Apertura Full Forge completado exitosamente.[/]")

if __name__ == "__main__":
    forjar_apertura()
