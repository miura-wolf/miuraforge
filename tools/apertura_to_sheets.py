import os
import sys
import re
import json
import time
from dotenv import load_dotenv

# Añadir el directorio raíz al path para importar core y llm
sys.path.append(os.path.abspath(os.path.dirname(os.path.dirname(__file__))))

from rich.console import Console
from core.database import Database
from llm.factory import LLMFactory

load_dotenv()
console = Console()
db = Database()

def parsear_guiones_apertura(md_path):
    """
    Parsea Guiones_Apertura_Canal.md y extrae ID, Título, Objetivo, Guion y Prompts.
    """
    if not os.path.exists(md_path):
        console.print(f"[red]❌ No se encontró: {md_path}[/]")
        return []

    with open(md_path, "r", encoding="utf-8") as f:
        contenido = f.read()

    # Dividir por separadores --- o por títulos ## 🎬
    secciones = re.split(r'(?=^## 🎬)', contenido, flags=re.MULTILINE)
    resultado = []

    for seccion in secciones:
        seccion = seccion.strip()
        if not seccion.startswith('## 🎬'):
            continue

        # Extraer ID: **ID:** `Apertura_01`
        m_id = re.search(r'\*\*ID:\*\*\s*`([^`]+)`', seccion)
        if not m_id:
            continue
        id_sesion = m_id.group(1).strip()

        # Extraer Guion (texto después de Objetivo: y antes de 🎬 o Copiar y pegar)
        # El guion suele empezar con > o simplemente líneas de texto
        # Buscamos el bloque de texto que empieza con > o después del Objetivo
        match_guion = re.search(r'Objetivo:.*?\n\s*\n(.*?)(?=\n\n🎬|\n\nCopiar y pegar)', seccion, re.DOTALL)
        if match_guion:
            guion_texto = match_guion.group(1).strip()
            # Limpiar el guion de > iniciales
            guion_texto = re.sub(r'^>\s*', '', guion_texto, flags=re.MULTILINE)
        else:
            guion_texto = ""

        # Extraer Prompts (lo que sigue a 'Copiar y pegar en Grok Imagine:')
        prompts = re.findall(r'Cinematic 9:16 vertical video\..*?(?=\n\n|\n---|\Z)', seccion, re.DOTALL)
        prompt_visual = " | ".join([p.strip().replace('\n', ' ') for p in prompts])

        resultado.append({
            'id_master': id_sesion,
            'guion': guion_texto,
            'visual_prompt_ref': prompt_visual
        })

    return resultado

def leer_doctrina_youtube():
    """Lee el archivo de doctrina para YouTube."""
    ruta = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        "prompts", "youtube_forge.txt"
    )
    if not os.path.exists(ruta):
        console.print(f"[red]❌ No se encontró la doctrina: {ruta}[/]")
        return ""
    with open(ruta, "r", encoding="utf-8") as f:
        return f.read()

def generar_metadata_apertura(brain, doctrina, guion_data):
    """
    Genera metadatos específicos para los videos de apertura.
    """
    id_sesion = guion_data['id_master']
    guion_texto = guion_data['guion']
    
    instruccion = f"""
Eres el estratega SEO de YouTube para el canal "Disciplina en Acero".
Tu misión: Generar los metadatos completos para un video de APERTURA (Lanzamiento del canal).
Estos videos son fundamentales para establecer el tono y la autoridad.

--- DATOS DEL VIDEO ---
ID_Sesion: {id_sesion}
Guion completo:
{guion_texto}

--- TAREA ---
Genera los metadatos siguiendo EXACTAMENTE la doctrina a continuación.
Dado que es apertura, los títulos deben ser BRUTALES y EPÍCOS.
Responde SOLO con el JSON válido, sin texto adicional.

{doctrina}
"""

    try:
        respuesta = brain.generate(instruccion).strip()
        # Limpiar markdown
        respuesta = re.sub(r'^```(?:json)?\s*', '', respuesta, flags=re.MULTILINE)
        respuesta = re.sub(r'\s*```$', '', respuesta, flags=re.MULTILINE)
        data = json.loads(respuesta)
        return data
    except Exception as e:
        console.print(f"[red]❌ Error LLM para {id_sesion}: {e}[/]")
        return None

def main():
    console.print("[bold cyan]⚔️ APERTURA FORGE — Trasladando Guiones a Sheets[/]")
    
    md_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "Docs", "Guiones_Apertura_Canal.md")
    guiones = parsear_guiones_apertura(md_path)
    
    if not guiones:
        console.print("[yellow]⚠️ No se detectaron guiones válidos en el MD.[/]")
        return

    doctrina = leer_doctrina_youtube()
    brain = LLMFactory.get_brain("visual")
    
    for item in guiones:
        id_m = item['id_master']
        console.print(f"\n[bold]🚀 Procesando {id_m}...[/]")
        
        metadata = generar_metadata_apertura(brain, doctrina, item)
        if not metadata:
            continue
            
        # Preparar para DESPLIEGUE
        desc = metadata.get("descripcion", {})
        despliegue_data = {
            'id_master': id_m,
            'titulo': metadata.get('titulo'),
            'subtitulo': desc.get('hook', ''),
            'descripcion': desc.get('desarrollo', ''),
            'hashtags': " ".join(metadata.get('hashtags', [])),
            'gancho': metadata.get('miniatura_prompt', ''),
            'cta': desc.get('cta', ''),
            'territorio': metadata.get('categoria', 'Educación'),
            'hora_lanzamiento': metadata.get('horario_sugerido', '')
        }
        
        # Registrar en Sheets
        try:
            db.registrar_despliegue(despliegue_data)
            console.print(f"  [green]✅ Sincronizado en DESPLIEGUE: {metadata.get('titulo')}[/]")
        except Exception as e:
            console.print(f"  [red]❌ Error sincronizando: {e}[/]")

    console.print("\n[bold green]🏁 Proceso de Apertura completado.[/]")

if __name__ == "__main__":
    main()
