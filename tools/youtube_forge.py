"""
⚔️ MIURA YOUTUBE FORGE — Generador Masivo de Metadatos YouTube
Genera por cada ID_Sesion:
  - Título optimizado (gancho + keywords, máx 60 chars)
  - Descripción (hook + desarrollo + CTA)
  - Hashtags (12-15, branded + nicho + tendencia)
  - Tags de YouTube (15-20, long-tail + branded)
  - Prompt de miniatura (estilo Miura chiaroscuro)
  - Categoría y horario sugerido

Fuente: output/masivo_grok_prompts.md  →  lee guion + ID_Sesion
Salida: output/youtube_metadata/
        ├── {ID_Sesion}_youtube.json    ← datos en bruto por video
        ├── {ID_Sesion}_youtube.txt     ← formato listo para pegar en YouTube
        └── resumen_youtube.md          ← índice completo de todos los videos
"""
import os
import sys
import re
import json
import time
from dotenv import load_dotenv

sys.path.append(os.path.abspath(os.path.dirname(os.path.dirname(__file__))))
from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.table import Table
from rich import box

# Miura Core
from core.database import Database

load_dotenv()
console = Console()
db = Database() # Conexión al Puente de Mando (Sheets)

# ══════════════════════════════════════════════
#  LLM Brain
# ══════════════════════════════════════════════
def get_brain():
    """Obtiene el cerebro LLM disponible (misma lógica que el resto de la Forja)."""
    try:
        from llm.factory import LLMFactory
        return LLMFactory.get_brain("visual")
    except Exception as e:
        console.print(f"[red]❌ Error cargando LLMFactory: {e}[/]")
        return None


# ══════════════════════════════════════════════
#  Parser del .md — Lee guiones por ID_Sesion
# ══════════════════════════════════════════════
def parsear_md_guiones(md_path, target_id=None):
    """
    Lee masivo_grok_prompts.md y extrae (id_sesion, guion_texto) por sección.
    Si se proporciona target_id, solo devuelve esa sesión.
    """
    if not os.path.exists(md_path):
        console.print(f"[red]❌ No se encontró: {md_path}[/]")
        console.print("[yellow]Ejecuta primero: mass_visual_forge.py[/]")
        return []

    with open(md_path, "r", encoding="utf-8") as f:
        contenido = f.read()

    secciones = re.split(r'(?=^## ID:)', contenido, flags=re.MULTILINE)
    resultado = []

    for seccion in secciones:
        seccion = seccion.strip()
        if not seccion.startswith('## ID:'):
            continue

        m_id = re.match(r'^## ID:\s*([^\s(]+)', seccion)
        if not m_id:
            continue
        id_sesion = m_id.group(1).strip()
        
        # Filtro Táctico: Si buscamos un ID específico, ignoramos el resto
        if target_id and id_sesion != target_id:
            continue

        # Extraer todos los [FRAGMENTO] y concatenarlos como guion completo
        fragmentos = re.findall(
            r'\[FRAGMENTO\]:\s*(.+?)(?=\[IMAGEN\]|\[IMAG[ME]NTO\]|\[ANIMACI|---CLIP\s*\d+---|^## ID:|\Z)',
            seccion, re.DOTALL | re.MULTILINE
        )
        guion_completo = " ".join([f.strip() for f in fragmentos if f.strip()])

        if guion_completo:
            resultado.append((id_sesion, guion_completo))
            if target_id: break # Ya encontramos el objetivo

    return resultado


# ══════════════════════════════════════════════
#  Leer doctrina YouTube
# ══════════════════════════════════════════════
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


# ══════════════════════════════════════════════
#  Generador de metadatos con LLM
# ══════════════════════════════════════════════
def generar_metadata_youtube(brain, doctrina, id_sesion, guion_texto):
    """
    Llama al LLM para generar los metadatos completos de YouTube.
    Devuelve dict con titulo, descripcion, hashtags, tags, miniatura_prompt,
    categoria, horario_sugerido.
    """
    num_palabras = len(guion_texto.split())
    duracion_est = round((num_palabras / 155) * 60, 0)

    instruccion = f"""
Eres el estratega SEO de YouTube para el canal "Disciplina en Acero".
Tu misión: Generar los metadatos completos para el siguiente Short.

--- DATOS DEL VIDEO ---
ID_Sesion: {id_sesion}
Duración estimada: {int(duracion_est)} segundos
Guion completo:
{guion_texto}

--- TAREA ---
Genera los metadatos siguiendo EXACTAMENTE la doctrina a continuación.
Responde SOLO con el JSON válido, sin texto adicional, sin markdown, sin explicaciones.
El JSON debe ser parseable directamente con json.loads().

{doctrina}
"""

    max_intentos = 3
    for intento in range(1, max_intentos + 1):
        try:
            respuesta = brain.generate(instruccion).strip()

            # Limpiar posibles bloques de código markdown
            respuesta = re.sub(r'^```(?:json)?\s*', '', respuesta, flags=re.MULTILINE)
            respuesta = re.sub(r'\s*```$', '', respuesta, flags=re.MULTILINE)
            respuesta = respuesta.strip()

            # Extraer JSON si hay texto antes/después
            m_json = re.search(r'\{[\s\S]+\}', respuesta)
            if m_json:
                respuesta = m_json.group(0)

            data = json.loads(respuesta)

            # Validar campos mínimos
            campos_req = ["titulo", "descripcion", "hashtags", "tags", "miniatura_prompt", "categoria", "horario_sugerido"]
            for campo in campos_req:
                if campo not in data:
                    raise ValueError(f"Falta campo: {campo}")

            return data

        except (json.JSONDecodeError, ValueError) as e:
            console.print(f"[yellow]  ⚠️ Intento {intento}/{max_intentos} — Error: {e}[/]")
            if intento < max_intentos:
                time.sleep(2)

    console.print(f"[red]  ❌ No se pudo parsear JSON válido para {id_sesion}[/]")
    return None


# ══════════════════════════════════════════════
#  Formateador de salida lista para YouTube
# ══════════════════════════════════════════════
def formatear_para_youtube(id_sesion, data):
    """
    Convierte el dict de metadatos en texto listo para pegar en YouTube Studio.
    """
    desc = data.get("descripcion", {})
    hook = desc.get("hook", "")
    desarrollo = desc.get("desarrollo", "")
    cta = desc.get("cta", "")
    descripcion_completa = f"{hook}\n\n{desarrollo}\n\n{cta}"

    hashtags_str = " ".join(data.get("hashtags", []))
    tags_str = ", ".join(data.get("tags", []))

    lineas = [
        f"{'═'*60}",
        f"  VIDEO: {id_sesion}",
        f"{'═'*60}",
        f"",
        f"📌 TÍTULO:",
        f"{data.get('titulo', '')}",
        f"",
        f"📝 DESCRIPCIÓN:",
        f"{descripcion_completa}",
        f"",
        f"{hashtags_str}",
        f"",
        f"🏷️ TAGS (pegar en campo Tags de YouTube Studio):",
        f"{tags_str}",
        f"",
        f"🖼️ PROMPT MINIATURA (para NVIDIA Flux / Nebius):",
        f"{data.get('miniatura_prompt', '')}",
        f"",
        f"📂 CATEGORÍA: {data.get('categoria', 'Educación')}",
        f"🕐 HORARIO SUGERIDO: {data.get('horario_sugerido', '')}",
        f"",
        f"{'─'*60}",
    ]
    return "\n".join(lineas)


# ══════════════════════════════════════════════
#  Modo masivo
# ══════════════════════════════════════════════
def modo_masivo(brain, doctrina, forzar=False, target_id=None):
    """
    Genera metadatos YouTube para todos los ID_Sesion del .md.
    Si ya existe el .json, salta (a menos que forzar=True).
    """
    console.print(f"\n[bold cyan]⚔️ YOUTUBE FORGE — MODO MASIVO[/]")

    base = os.path.dirname(os.path.dirname(__file__))
    md_path = os.path.join(base, "output", "masivo_grok_prompts.md")
    sesiones = parsear_md_guiones(md_path, target_id=target_id)

    if not sesiones:
        console.print("[red]❌ No hay sesiones para procesar.[/]")
        return

    out_dir = os.path.join(base, "output", "youtube_metadata")
    os.makedirs(out_dir, exist_ok=True)

    resumen_path = os.path.join(out_dir, "resumen_youtube.md")

    total_gen = 0
    total_skip = 0
    total_error = 0

    console.print(f"[green]✅ {len(sesiones)} sesiones encontradas en el .md[/]\n")

    with open(resumen_path, "w", encoding="utf-8") as resumen_f:
        resumen_f.write("# 📺 RESUMEN YOUTUBE METADATA — Disciplina en Acero\n\n")
        resumen_f.write("> Generado automáticamente por YouTube Forge\n\n")
        resumen_f.write("---\n\n")

        for idx, (id_sesion, guion_texto) in enumerate(sesiones, start=1):
            json_path = os.path.join(out_dir, f"{id_sesion}_youtube.json")
            txt_path = os.path.join(out_dir, f"{id_sesion}_youtube.txt")

            # Normalizar ID para la búsqueda: a veces el ID en el .md tiene espacios o sufijos
            if not id_sesion:
                continue
            id_limpio = str(id_sesion).split()[0].strip()
            json_path_alt = os.path.join(out_dir, f"{id_limpio}_youtube.json")

            console.print(f"[bold]── [{idx}/{len(sesiones)}] {id_sesion} ──[/]")

            # Skip si ya existe (reanudable)
            if (os.path.exists(json_path) or os.path.exists(json_path_alt)) and not forzar:
                console.print(f"  [dim]⏭️  Ya procesado — saltando (usa --forzar para regenerar)[/]")
                total_skip += 1

                # Intentar leer título para el resumen aunque saltemos
                try:
                    p = json_path if os.path.exists(json_path) else json_path_alt
                    with open(p, "r", encoding="utf-8") as jf:
                        data = json.load(jf)
                    resumen_f.write(f"## [{idx}] {id_sesion}\n")
                    resumen_f.write(f"**Título:** {data.get('titulo', 'N/A')}\n")
                    resumen_f.write(f"**Categoría:** {data.get('categoria', 'N/A')}\n")
                    resumen_f.write(f"**Horario:** {data.get('horario_sugerido', 'N/A')}\n\n")
                    resumen_f.write(f"---\n\n")
                except:
                    pass
                continue

            # Generar metadatos
            data = generar_metadata_youtube(brain, doctrina, id_sesion, guion_texto)

            if not data:
                total_error += 1
                console.print(f"  [red]❌ Error generando metadatos[/]")
                continue

            # Guardar JSON (datos en bruto)
            with open(json_path, "w", encoding="utf-8") as jf:
                json.dump(data, jf, ensure_ascii=False, indent=2)

            # Guardar TXT (formato YouTube listo)
            txt_content = formatear_para_youtube(id_sesion, data)
            with open(txt_path, "w", encoding="utf-8") as tf:
                tf.write(txt_content)

            # 🚀 DESPLIEGUE EN GOOGLE SHEETS
            try:
                desc = data.get("descripcion", {})
                despliegue_data = {
                    'id_master': id_sesion,
                    'titulo': data.get('titulo'),
                    'subtitulo': desc.get('hook', ''),
                    'descripcion': desc.get('desarrollo', ''),
                    'hashtags': " ".join(data.get('hashtags', [])),
                    'gancho': data.get('miniatura_prompt', ''),
                    'cta': desc.get('cta', ''),
                    'territorio': data.get('categoria', 'Educación'),
                    'hora_lanzamiento': data.get('horario_sugerido', '')
                }
                db.registrar_despliegue(despliegue_data)
                console.print(f"  [green]🚀 Sincronizado en Sheets (DESPLIEGUE)[/]")
            except Exception as e:
                console.print(f"  [yellow]⚠️ Error sincronizando con Sheets: {e}[/]")

            # Vista previa
            console.print(f"  [green]✅ Título:[/] {data.get('titulo', '???')}")
            console.print(f"  [dim]   Horario: {data.get('horario_sugerido', '???')}[/]")

            # Añadir al resumen maestro
            resumen_f.write(f"## [{idx}] {id_sesion}\n\n")
            resumen_f.write(f"**📌 Título:** {data.get('titulo', 'N/A')}\n\n")
            desc = data.get("descripcion", {})
            resumen_f.write(f"**Hook:** {desc.get('hook', 'N/A')}\n\n")
            resumen_f.write(f"**Hashtags:** {' '.join(data.get('hashtags', []))}\n\n")
            resumen_f.write(f"**Categoría:** {data.get('categoria', 'N/A')} | ")
            resumen_f.write(f"**Horario:** {data.get('horario_sugerido', 'N/A')}\n\n")
            resumen_f.write(f"**🖼️ Miniatura prompt:** _{data.get('miniatura_prompt', 'N/A')}_\n\n")
            resumen_f.write(f"---\n\n")

            total_gen += 1
            time.sleep(1.0)  # Rate limiting cortés

    console.print(f"\n[bold green]✅ YouTube Forge completado.[/]")
    console.print(f"   [green]Generados: {total_gen}[/]  |  [yellow]Saltados: {total_skip}[/]  |  [red]Errores: {total_error}[/]")
    console.print(f"📁 Metadatos en: [cyan]{out_dir}[/]")
    console.print(f"📋 Resumen en:   [cyan]{resumen_path}[/]")


# ══════════════════════════════════════════════
#  Modo individual (1 video a la vez)
# ══════════════════════════════════════════════
def modo_individual(brain, doctrina):
    """Permite elegir un ID_Sesion específico para generar/regenerar."""
    base = os.path.dirname(os.path.dirname(__file__))
    md_path = os.path.join(base, "output", "masivo_grok_prompts.md")
    sesiones = parsear_md_guiones(md_path)

    if not sesiones:
        console.print("[red]❌ No hay sesiones para procesar.[/]")
        return

    # Mostrar tabla de sesiones disponibles
    tabla = Table(title="Sesiones disponibles", box=box.MINIMAL_DOUBLE_HEAD)
    tabla.add_column("#", style="dim", width=4)
    tabla.add_column("ID_Sesion", style="cyan")
    tabla.add_column("Palabras aprox.", style="green")

    for i, (id_s, guion) in enumerate(sesiones, start=1):
        palabras = len(guion.split())
        tabla.add_row(str(i), id_s, str(palabras))

    console.print(tabla)

    idx_str = Prompt.ask("\nNúmero de sesión a generar (o 'q' para salir)", default="q")
    if idx_str.lower() == "q":
        return

    try:
        idx = int(idx_str) - 1
        id_sesion, guion_texto = sesiones[idx]
    except (ValueError, IndexError):
        console.print("[red]Selección inválida.[/]")
        return

    out_dir = os.path.join(base, "output", "youtube_metadata")
    os.makedirs(out_dir, exist_ok=True)

    console.print(f"\n[bold]Generando metadatos para: [cyan]{id_sesion}[/][/]")
    data = generar_metadata_youtube(brain, doctrina, id_sesion, guion_texto)

    if not data:
        console.print("[red]❌ Error generando metadatos.[/]")
        return

    json_path = os.path.join(out_dir, f"{id_sesion}_youtube.json")
    txt_path = os.path.join(out_dir, f"{id_sesion}_youtube.txt")

    with open(json_path, "w", encoding="utf-8") as jf:
        json.dump(data, jf, ensure_ascii=False, indent=2)

    txt_content = formatear_para_youtube(id_sesion, data)
    with open(txt_path, "w", encoding="utf-8") as tf:
        tf.write(txt_content)

    # 🚀 DESPLIEGUE EN GOOGLE SHEETS
    try:
        desc = data.get("descripcion", {})
        despliegue_data = {
            'id_master': id_sesion,
            'titulo': data.get('titulo'),
            'subtitulo': desc.get('hook', ''),
            'descripcion': desc.get('desarrollo', ''),
            'hashtags': " ".join(data.get('hashtags', [])),
            'gancho': data.get('miniatura_prompt', ''),
            'cta': desc.get('cta', ''),
            'territorio': data.get('categoria', 'Educación'),
            'hora_lanzamiento': data.get('horario_sugerido', '')
        }
        db.registrar_despliegue(despliegue_data)
        console.print(f"[green]🚀 Sincronizado en Sheets (DESPLIEGUE)[/]")
    except Exception as e:
        console.print(f"[yellow]⚠️ Error sincronizando con Sheets: {e}[/]")

    # Mostrar resultado completo
    console.print("\n" + txt_content)
    console.print(f"\n[bold green]✅ Guardado en:[/]")
    console.print(f"   JSON: [cyan]{json_path}[/]")
    console.print(f"   TXT:  [cyan]{txt_path}[/]")


# ══════════════════════════════════════════════
#  Vista previa rápida (sin generar)
# ══════════════════════════════════════════════
def modo_preview():
    """Muestra cuántas sesiones hay y sus guiones (sin generar nada)."""
    base = os.path.dirname(os.path.dirname(__file__))
    md_path = os.path.join(base, "output", "masivo_grok_prompts.md")
    sesiones = parsear_md_guiones(md_path)

    out_dir = os.path.join(base, "output", "youtube_metadata")

    tabla = Table(title=f"📺 YouTube Forge — {len(sesiones)} sesiones", box=box.SIMPLE_HEAVY)
    tabla.add_column("#", style="dim", width=4)
    tabla.add_column("ID_Sesion", style="cyan", width=35)
    tabla.add_column("Palabras", style="green", width=10)
    tabla.add_column("Estado", style="yellow", width=15)

    for i, (id_s, guion) in enumerate(sesiones, start=1):
        palabras = len(guion.split())
        json_path = os.path.join(out_dir, f"{id_s}_youtube.json")
        estado = "[green]✅ Generado[/]" if os.path.exists(json_path) else "[yellow]⏳ Pendiente[/]"
        tabla.add_row(str(i), id_s, str(palabras), estado)

    console.print(tabla)

    generados = sum(
        1 for id_s, _ in sesiones
        if os.path.exists(os.path.join(out_dir, f"{id_s}_youtube.json"))
    )
    console.print(f"\n[green]Generados: {generados}[/] / [cyan]Total: {len(sesiones)}[/]")


# ══════════════════════════════════════════════
#  MAIN
# ══════════════════════════════════════════════
def main():
    import argparse
    parser = argparse.ArgumentParser(description="⚔️ MIURA YOUTUBE FORGE")
    parser.add_argument("--forzar", action="store_true",
                        help="Regenerar metadatos aunque ya existan")
    parser.add_argument("--modo", choices=["masivo", "individual", "preview"],
                        default=None, help="Modo de operación directa")
    args = parser.parse_args()

    console.print("\n[bold cyan]📺 MIURA YOUTUBE FORGE — Disciplina en Acero[/]")
    console.print("[dim]Genera títulos, descripciones, hashtags y tags optimizados para YouTube[/]\n")

    doctrina = leer_doctrina_youtube()
    if not doctrina:
        console.print("[red]❌ No se puede continuar sin la doctrina.[/]")
        return

    # Mostrar preview rápido siempre
    modo_preview()

    # Si se pasó modo por argumento, ir directo
    if args.modo:
        modo_elegido = args.modo
    else:
        console.print("\n[bold]¿Qué modo deseas?[/]")
        console.print("  [cyan]1[/]) ⚔️  Forja Masiva (todos los videos pendientes)")
        console.print("  [green]2[/]) 🎯 Individual (elige un video específico)")
        console.print("  [dim]3[/]) 👁️  Preview (solo ver estado, sin generar)")
        opc = Prompt.ask("Modo", choices=["1", "2", "3"], default="1")
        modo_elegido = {"1": "masivo", "2": "individual", "3": "preview"}[opc]

    if modo_elegido == "preview":
        pass  # ya se mostró arriba
    elif modo_elegido == "individual":
        brain = get_brain()
        if not brain:
            return
        modo_individual(brain, doctrina)
    elif modo_elegido == "masivo":
        if args.forzar:
            console.print("[yellow]⚠️  Modo FORZAR: se regenerarán todos los metadatos existentes.[/]")
        brain = get_brain()
        if not brain:
            return
        modo_masivo(brain, doctrina, forzar=args.forzar)


if __name__ == "__main__":
    main()
