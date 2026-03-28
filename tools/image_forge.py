"""
⚔️ MIURA IMAGE FORGE — Generador de Imágenes + Fichas de Animación
Motores disponibles:
  - NVIDIA Flux 2 Klein  (GRATIS, rápido, filtro agresivo)
  - Nebius Flux Schnell  (créditos, sin filtro)
  - Replicate Flux        (Económico, alta compatibilidad)
  - AUTO                 (NVIDIA → Nebius → Replicate)

Fuente de prompts: Google Sheets (FUENTE PRIMARIA)
Registro de estado: Google Sheets (Trazabilidad)
"""
import os
import sys
import re
import base64
import requests
import time
import io
from PIL import Image
from dotenv import load_dotenv

sys.path.append(os.path.abspath(os.path.dirname(os.path.dirname(__file__))))
from rich.console import Console
from rich.prompt import Prompt
from rich.progress import track

load_dotenv()
console = Console()

# ══════════════════════════════════════════════
#  MOTOR 1: NVIDIA Flux 2 Klein (GRATIS)
# ══════════════════════════════════════════════
def cargar_nvidia_keys():
    keys = []
    env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env")
    if os.path.exists(env_path):
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line.startswith("OPENAI_API_KEY=") and "nvapi-" in line:
                    key = line.split("=", 1)[1].split("#")[0].strip()
                    if key.startswith("nvapi-") and key not in keys:
                        keys.append(key)
    return keys

NVIDIA_KEYS = cargar_nvidia_keys()
current_nvidia_idx = 0

def get_nvidia_key():
    global current_nvidia_idx
    if not NVIDIA_KEYS:
        return None
    return NVIDIA_KEYS[current_nvidia_idx % len(NVIDIA_KEYS)]

def rotate_nvidia_key():
    global current_nvidia_idx
    current_nvidia_idx = (current_nvidia_idx + 1) % len(NVIDIA_KEYS)


# ══════════════════════════════════════════════
#  Carga de Keys NVIDIA
# ══════════════════════════════════════════════
NVIDIA_KEYS = cargar_nvidia_keys()
current_nvidia_idx = 0

def get_nvidia_key():
    global current_nvidia_idx
    if not NVIDIA_KEYS:
        return None
    return NVIDIA_KEYS[current_nvidia_idx % len(NVIDIA_KEYS)]

def rotate_nvidia_key():
    global current_nvidia_idx
    current_nvidia_idx = (current_nvidia_idx + 1) % len(NVIDIA_KEYS)

def generar_imagen_nvidia(prompt, output_path, width=752, height=1392):
    """Genera imagen con NVIDIA Flux 2 Klein. GRATIS pero tiene filtro de contenido."""
    url = "https://ai.api.nvidia.com/v1/genai/black-forest-labs/flux.2-klein-4b"
    
    for _ in range(len(NVIDIA_KEYS)):
        key = get_nvidia_key()
        headers = {"Authorization": f"Bearer {key}", "Accept": "application/json"}
        payload = {"prompt": prompt, "width": width, "height": height, "seed": 0, "steps": 4}
        
        try:
            response = requests.post(url, headers=headers, json=payload)
            
            if response.status_code == 200:
                data = response.json()
                img_b64 = None
                
                if "artifacts" in data and isinstance(data["artifacts"], list) and len(data["artifacts"]) > 0:
                    artifact = data["artifacts"][0]
                    # Verificar si fue filtrado
                    if artifact.get("finishReason") == "CONTENT_FILTERED":
                        console.print("[yellow]⚠️ NVIDIA filtró el contenido. Usa motor Nebius para este prompt.[/]")
                        return False
                    img_b64 = artifact.get("base64", "")
                elif "image" in data:
                    img_b64 = data["image"]
                
                if not img_b64:
                    console.print(f"[yellow]⚠️ Respuesta sin imagen[/]")
                    return False
                
                os.makedirs(os.path.dirname(output_path), exist_ok=True)
                with open(output_path, "wb") as f:
                    f.write(base64.b64decode(img_b64))
                return True
                
            elif response.status_code in [429, 402]:
                rotate_nvidia_key()
            else:
                console.print(f"[red]❌ Error NVIDIA ({response.status_code}): {response.text[:150]}[/]")
                rotate_nvidia_key()
                
        except Exception as e:
            console.print(f"[red]❌ Error: {e}[/]")
            rotate_nvidia_key()
    
    return False

# ══════════════════════════════════════════════
#  MOTOR 2: Nebius Flux Schnell (Créditos)
# ══════════════════════════════════════════════
def generar_imagen_nebius(prompt, output_path, size="1024x1024"):
    """Genera imagen con Nebius Flux Dev. Mayor calidad, consume saldo actual."""
    nebius_key = os.getenv("NEBIUS_API_KEY")
    if not nebius_key:
        console.print("[red]❌ NEBIUS_API_KEY no encontrada en .env[/]")
        return False
    
    try:
        from openai import OpenAI
        client = OpenAI(
            base_url="https://api.tokenfactory.nebius.com/v1/",
            api_key=nebius_key
        )
        response = client.images.generate(
            model="black-forest-labs/flux-dev",
            prompt=prompt,
            size=size
        )
        if response.data and len(response.data) > 0:
            img_data = response.data[0]
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            if hasattr(img_data, 'b64_json') and img_data.b64_json:
                with open(output_path, "wb") as f:
                    f.write(base64.b64decode(img_data.b64_json))
                return True
            elif hasattr(img_data, 'url') and img_data.url:
                img_response = requests.get(img_data.url)
                if img_response.status_code == 200:
                    with open(output_path, "wb") as f:
                        f.write(img_response.content)
                    return True
        console.print("[yellow]⚠️ Nebius respondió pero sin imagen válida[/]")
        return False
    except Exception as e:
        console.print(f"[red]❌ Error Nebius: {e}[/]")
        return False


# ══════════════════════════════════════════════
#  MOTOR 3: Replicate Flux Schnell (Muy Económico)
# ══════════════════════════════════════════════
def generar_imagen_replicate(prompt, output_path, width=768, height=1024):
    """
    Genera imagen con Replicate (Flux Schnell) vía API Directa (Requests).
    Evita problemas de compatibilidad de la SDK con Python 3.14.
    Costo: ~$0.003 por imagen.
    """
    replicate_token = os.getenv("REPLICATE_API_TOKEN")
    if not replicate_token:
        console.print("[red]❌ REPLICATE_API_TOKEN no encontrada en .env[/]")
        return False

    headers = {
        "Authorization": f"Token {replicate_token}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "version": "131d9e185621b4b4d349fd262e363420a6f74081d8c27966c9c5bcf120fa3985",
        "input": {
            "prompt": prompt,
            "aspect_ratio": "9:16",
            "output_format": "webp",
            "output_quality": 90
        }
    }

    try:
        # 1. Crear Predicción
        resp = requests.post("https://api.replicate.com/v1/predictions", json=payload, headers=headers)
        if resp.status_code != 201:
            console.print(f"[red]❌ Error Replicate API ({resp.status_code}): {resp.text}[/]")
            return False
        
        prediction = resp.json()
        prediction_id = prediction["id"]
        
        # 2. Polling (Esperar resultado)
        max_attempts = 30
        for _ in range(max_attempts):
            poll_resp = requests.get(f"https://api.replicate.com/v1/predictions/{prediction_id}", headers=headers)
            status_data = poll_resp.json()
            status = status_data["status"]
            
            if status == "succeeded":
                output = status_data.get("output")
                if output and isinstance(output, list):
                    img_url = output[0]
                    img_data = requests.get(img_url).content
                    
                    # CONVERSIÓN TÁCTICA: WebP -> PNG para compatibilidad Miura
                    try:
                        with Image.open(io.BytesIO(img_data)) as img:
                            img.save(output_path, "PNG")
                        return True
                    except Exception as e:
                        console.print(f"[yellow]⚠️ Falló conversión a PNG, guardando crudo: {e}[/]")
                        with open(output_path, "wb") as f:
                            f.write(img_data)
                        return True
                break
            elif status in ["failed", "canceled"]:
                console.print(f"[red]❌ Replicate: predicción {status}[/]")
                return False
            
            time.sleep(1.5)
            
        console.print("[yellow]⚠️ Replicate: tiempo de espera agotado[/]")
        return False
    except Exception as e:
        console.print(f"[red]❌ Error en conexión Replicate: {e}[/]")
        return False


# ══════════════════════════════════════════════
#  Función unificada: elige motor y ejecuta
# ══════════════════════════════════════════════
def generar_imagen(prompt, output_path, width=752, height=1392, motor="nvidia"):
    """Genera imagen con el motor seleccionado.
    AUTO: NVIDIA (gratis) → Nebius (saldo) → Replicate (barato)
    """
    if motor == "nvidia":
        return generar_imagen_nvidia(prompt, output_path, width, height)
    elif motor == "nebius":
        return generar_imagen_nebius(prompt, output_path, f"{width}x{height}")
    elif motor == "replicate":
        return generar_imagen_replicate(prompt, output_path, width, height)
    elif motor == "auto":
        # Cascada: NVIDIA gratis → Nebius (saldo) → Replicate (barato)
        ok = generar_imagen_nvidia(prompt, output_path, width, height)
        if not ok:
            console.print("[cyan]🔄 NVIDIA filtró → intentando Nebius (Flux Dev / Saldo)...[/]")
            ok = generar_imagen_nebius(prompt, output_path, f"{width}x{height}")
        if not ok:
            console.print("[cyan]🔄 Nebius falló → intentando Replicate (Flux Schnell)...[/]")
            ok = generar_imagen_replicate(prompt, output_path, width, height)
        return ok
    return False

# ══════════════════════════════════════════════
#  Parser del formato dual ---CLIP X---
# ══════════════════════════════════════════════
def parsear_clips_duales(visual_text):
    """Extrae los bloques duales del formato ---CLIP X---."""
    clips = []
    bloques = re.split(r'---CLIP\s*\d+---', visual_text)
    
    for bloque in bloques:
        if not bloque.strip():
            continue
        
        fragmento = ""
        imagen = ""
        animacion = ""
        
        m_frag = re.search(r'\[FRAGMENTO\]:\s*(.+?)(?=\[IMAGEN\]|\[IMAG[ME]NTO\]|\[ANIMACI|$)', bloque, re.DOTALL)
        if m_frag:
            fragmento = m_frag.group(1).strip()
        
        # Acepta variantes: [IMAGEN], [IMAGMENTO], [IMAGENTO], [IMAGMENT]
        m_img = re.search(r'\[IMAG(?:EN|MENTO|ENTO|MENT)\]:\s*(.+?)(?=\[ANIMACI[OÓ]N\]|\[ANIMACION\]|$)', bloque, re.DOTALL)
        if m_img:
            imagen = m_img.group(1).strip()
        
        m_anim = re.search(r'\[ANIMACI[OÓ]N\]:\s*(.+?)$', bloque, re.DOTALL)
        if m_anim:
            animacion = m_anim.group(1).strip()
        
        if imagen:
            clips.append({
                "fragmento": fragmento,
                "imagen_prompt": imagen,
                "animacion": animacion
            })
    
    return clips


def parsear_md_completo(md_path):
    """
    Lee masivo_grok_prompts.md y devuelve lista de (id_sesion, visual_text).
    Esta es la FUENTE PRIMARIA de prompts para la generación de imágenes.
    """
    if not os.path.exists(md_path):
        console.print(f"[red]❌ No se encontró el archivo: {md_path}[/]")
        console.print("[yellow]Ejecuta primero: mass_visual_forge.py[/]")
        return []
    
    with open(md_path, "r", encoding="utf-8") as f:
        contenido = f.read()
    
    # Separar por secciones ## ID: ...
    # Cada sección termina donde empiece la siguiente o al final
    secciones = re.split(r'(?=^## ID:)', contenido, flags=re.MULTILINE)
    
    resultado = []
    for seccion in secciones:
        seccion = seccion.strip()
        if not seccion or not seccion.startswith('## ID:'):
            continue
        
        # Extraer el ID_Sesion del encabezado ## ID: XXXX (Fila: N | ...)
        m_id = re.match(r'^## ID:\s*([^\s(]+)', seccion)
        if not m_id:
            continue
        
        id_sesion = m_id.group(1).strip()
        
        # El cuerpo visual son los clips (después del encabezado hasta el ---)
        # Remove the header line
        cuerpo = re.sub(r'^## ID:.*?\n', '', seccion, count=1).strip()
        # Remove trailing horizontal rule
        cuerpo = re.sub(r'\n---\s*$', '', cuerpo).strip()
        
        if '---CLIP' in cuerpo:
            resultado.append((id_sesion, cuerpo))
    
    return resultado

# ══════════════════════════════════════════════
#  Modos de operación
# ══════════════════════════════════════════════
def seleccionar_motor():
    """Permite al usuario elegir el motor de generación."""
    nebius_key = os.getenv("NEBIUS_API_KEY")
    replicate_token = os.getenv("REPLICATE_API_TOKEN")
    
    console.print("\n[bold]Seleccione motor de imagen:[/]")
    console.print(f"  [green]N[/]) NVIDIA Flux Klein    — GRATIS (filtro agresivo) [{len(NVIDIA_KEYS)} keys]")
    console.print(f"  [yellow]B[/]) Nebius Flux Dev      — Saldo Actual (Mejor Calidad) {'[green]✅[/]' if nebius_key else '[red]❌ Sin NEBIUS_API_KEY[/]'}")
    console.print(f"  [blue]R[/]) Replicate Flux Schnell — Muy Barato (~$0.003) {'[green]✅[/]' if replicate_token else '[red]❌ Sin REPLICATE_API_TOKEN[/]'}")
    console.print( "  [cyan]A[/]) AUTO                 — NVIDIA → Nebius → Replicate (recomendado)")
    
    opc = Prompt.ask("Motor", choices=["N", "B", "R", "A"], default="A").upper()
    return {"N": "nvidia", "B": "nebius", "R": "replicate", "A": "auto"}[opc]

def modo_prueba(motor):
    """Genera una sola imagen de prueba."""
    console.print(f"\n[bold cyan]🧪 MODO PRUEBA — Motor: {motor.upper()}[/]")
    
    prompt = "Dark industrial forge workshop interior, cold steel anvil under single harsh spotlight beam, heavy atmospheric smoke drifting upward, rust textures on concrete walls, ember orange accent glow from dying furnace coals, pitch black background, brutalist architecture, 4k hyperrealistic photography"
    
    out = os.path.join(os.path.dirname(os.path.dirname(__file__)), "output", "PRUEBA_IMAGEN_FORGE.png")
    
    console.print(f"📡 Enviando prompt...")
    exito = generar_imagen(prompt, out, motor=motor)
    
    if exito:
        console.print(f"\n[bold green]✅ ¡IMAGEN GENERADA![/] → [cyan]{out}[/]")
        try:
            os.startfile(out)
        except:
            pass
    else:
        console.print("[red]❌ Falló la generación.[/]")

def modo_masivo(motor, target_id=None):
    """
    LEE desde Google Sheets (FUENTE PRIMARIA), parsea los clips duales
    y genera imágenes + fichas de animación por ID_Sesion o por ID específico.
    """
    console.print(f"\n[bold cyan]⚔️ FORJA MASIVA (MODO SHEETS) — Motor: {motor.upper()}[/]")
    
    from core.database import Database
    db = Database()
    
    try:
        rows = db.produccion.get_all_records()
    except Exception as e:
        console.print(f"[red]❌ Error leyendo Sheets: {e}[/]")
        return

    # Filtrar sesiones con visuales generados (contienen ---CLIP)
    pendientes = []
    for r in rows:
        id_s = str(r.get('ID_Sesion', '')).strip()
        visual_text = str(r.get('Prompt_Visual', '')).strip()
        
        # Si hay target_id, solo ese. Si no, todos los que tengan ---CLIP
        if target_id:
            if id_s == target_id and "---CLIP" in visual_text:
                pendientes.append((id_s, visual_text))
                break
        elif id_s and "---CLIP" in visual_text:
            pendientes.append((id_s, visual_text))
    
    if not pendientes:
        console.print("[red]❌ No hay sesiones listas (con prompts duales) en la tabla PRODUCCION.[/]")
        console.print("[yellow]Asegúrate de ejecutar mass_visual_forge.py primero para generar los prompts.[/]")
        return
    
    console.print(f"[green]✅ {len(pendientes)} sesiones encontradas en el Puente de Mando (Sheets).[/]")
    
    out_base = os.path.join(os.path.dirname(os.path.dirname(__file__)), "output", "imagenes_shorts")
    os.makedirs(out_base, exist_ok=True)
    
    total_gen = 0
    total_skip = 0
    total_error = 0
    
    for idx, (id_sesion, visual_text) in enumerate(pendientes, start=1):
        console.print(f"\n[bold]── [{idx}/{len(pendientes)}] {id_sesion} ──[/]")
        clips = parsear_clips_duales(visual_text)
        
        if not clips:
            console.print(f"[yellow]⚠️ No se pudieron parsear clips de {id_sesion}[/]")
            total_error += 1
            continue
        
        carpeta = os.path.join(out_base, id_sesion)
        os.makedirs(carpeta, exist_ok=True)
        
        for j, clip in enumerate(clips, start=1):
            img_path = os.path.join(carpeta, f"clip_{j:02d}.png")
            ficha_path = os.path.join(carpeta, f"clip_{j:02d}_ANIMACION.txt")
            
            # Skip si ya existe la imagen (reanudable sin pérdida)
            if os.path.exists(img_path):
                total_skip += 1
                console.print(f"  [dim]⏭️  clip_{j:02d}.png ya existe — saltando[/]")
                continue
            
            exito = generar_imagen(clip["imagen_prompt"], img_path, motor=motor)
            
            if exito:
                total_gen += 1
                with open(ficha_path, "w", encoding="utf-8") as f:
                    f.write(f"=== FICHA DE ANIMACIÓN — {id_sesion} — Clip {j} ===\n\n")
                    f.write(f"GUION (lo que dice la voz):\n{clip['fragmento']}\n\n")
                    f.write(f"DIRECTIVA DE ANIMACIÓN (pegar en Grok/Qwen al subir la imagen):\n{clip['animacion']}\n\n")
                    f.write(f"PROMPT ORIGINAL DE IMAGEN:\n{clip['imagen_prompt']}\n")
                console.print(f"  [green]✅ clip_{j:02d}.png[/]")
            else:
                total_error += 1
                console.print(f"  [red]❌ clip_{j:02d}.png falló[/]")
            
            time.sleep(0.5)
    
    console.print(f"\n[bold green]✅ Forja Masiva completada.[/]")
    console.print(f"   [green]Generadas: {total_gen}[/]  |  [yellow]Saltadas: {total_skip}[/]  |  [red]Errores: {total_error}[/]")
    console.print(f"📁 Revisa: [cyan]{out_base}[/]")

def modo_manual(motor):
    """Prompt manual con directiva de animación."""
    prompt = console.input("[bold green]📝 Prompt de imagen (en inglés):[/]\n")
    animacion = console.input("[bold yellow]🎬 Directiva de animación (en inglés, opcional):[/]\n")
    nombre = Prompt.ask("Nombre del archivo (sin extensión)", default="custom_image")
    
    out_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "output")
    img_path = os.path.join(out_dir, f"{nombre}.png")
    
    exito = generar_imagen(prompt, img_path, motor=motor)
    if exito:
        console.print(f"[bold green]✅ Imagen: {img_path}[/]")
        if animacion.strip():
            ficha_path = os.path.join(out_dir, f"{nombre}_ANIMACION.txt")
            with open(ficha_path, "w", encoding="utf-8") as f:
                f.write(f"DIRECTIVA DE ANIMACIÓN:\n{animacion}\n\nPROMPT:\n{prompt}\n")
            console.print(f"[bold green]✅ Ficha: {ficha_path}[/]")
        try:
            os.startfile(img_path)
        except:
            pass

# ══════════════════════════════════════════════
#  Modo Reparar: regenera solo los clips faltantes
# ══════════════════════════════════════════════
def modo_reparar(motor):
    """
    Escanea el .md y las carpetas de imagenes_shorts.
    Detecta clips que existen en el .md pero NO tienen .png.
    Los regenera con el motor elegido.
    """
    console.print(f"\n[bold yellow]🔧 MODO REPARAR — Motor: {motor.upper()}[/]")
    console.print("[dim]Buscando clips faltantes comparando .md vs carpetas...[/]\n")
    
    base = os.path.dirname(os.path.dirname(__file__))
    md_path = os.path.join(base, "output", "masivo_grok_prompts.md")
    out_base = os.path.join(base, "output", "imagenes_shorts")
    
    sesiones = parsear_md_completo(md_path)
    if not sesiones:
        console.print("[red]❌ No hay datos en el .md.[/]")
        return
    
    # Inventario de clips faltantes
    faltantes = []  # (id_sesion, num_clip, clip_data)
    total_esperados = 0
    
    for id_sesion, visual_text in sesiones:
        clips = parsear_clips_duales(visual_text)
        carpeta = os.path.join(out_base, id_sesion)
        
        for j, clip in enumerate(clips, start=1):
            total_esperados += 1
            img_path = os.path.join(carpeta, f"clip_{j:02d}.png")
            if not os.path.exists(img_path):
                faltantes.append((id_sesion, j, clip, img_path))
    
    if not faltantes:
        console.print("[bold green]✅ ¡No hay clips faltantes! Todos los clips están completos.[/]")
        console.print(f"[dim]Total verificados: {total_esperados}[/]")
        return
    
    console.print(f"[yellow]📋 Clips faltantes: [bold]{len(faltantes)}[/] de {total_esperados} totales[/]")
    console.print()
    
    # Agrupar por sesión para mostrar resumen
    sesion_counts = {}
    for id_s, j, _, _ in faltantes:
        sesion_counts[id_s] = sesion_counts.get(id_s, 0) + 1
    for id_s, count in sesion_counts.items():
        console.print(f"  [cyan]{id_s}[/]: [red]{count} faltantes[/]")
    
    console.print()
    confirmar = Prompt.ask(
        f"¿Reparar [bold]{len(faltantes)}[/] clips con motor [bold]{motor.upper()}[/]?",
        choices=["s", "n"], default="s"
    )
    if confirmar.lower() != "s":
        console.print("[dim]Reparación cancelada.[/]")
        return
    
    total_ok = 0
    total_err = 0
    
    for idx, (id_sesion, j, clip, img_path) in enumerate(faltantes, start=1):
        carpeta = os.path.join(out_base, id_sesion)
        os.makedirs(carpeta, exist_ok=True)
        ficha_path = os.path.join(carpeta, f"clip_{j:02d}_ANIMACION.txt")
        
        console.print(f"[{idx}/{len(faltantes)}] [cyan]{id_sesion}[/] / clip_{j:02d}")
        
        exito = generar_imagen(clip["imagen_prompt"], img_path, motor=motor)
        
        if exito:
            total_ok += 1
            # Generar ficha si no existe
            if not os.path.exists(ficha_path):
                with open(ficha_path, "w", encoding="utf-8") as f:
                    f.write(f"=== FICHA DE ANIMACIÓN — {id_sesion} — Clip {j} ===\n\n")
                    f.write(f"GUION (lo que dice la voz):\n{clip['fragmento']}\n\n")
                    f.write(f"DIRECTIVA DE ANIMACIÓN:\n{clip['animacion']}\n\n")
                    f.write(f"PROMPT ORIGINAL DE IMAGEN:\n{clip['imagen_prompt']}\n")
            console.print(f"  [green]✅ Reparado[/]")
        else:
            total_err += 1
            console.print(f"  [red]❌ Sigue fallando[/]")
        
        time.sleep(0.5)
    
    console.print(f"\n[bold green]🔧 Reparación completada.[/]")
    console.print(f"   [green]Reparados: {total_ok}[/]  |  [red]Sin reparar: {total_err}[/]")
    if total_err > 0:
        console.print(f"[yellow]Los {total_err} restantes pueden necesitar motor diferente.[/]")
        console.print("[dim]Ejecuta nuevamente con motor distinto para completarlos.[/]")


def main():
    nebius_key = os.getenv("NEBIUS_API_KEY")

    console.print("\n[bold cyan]🖼️ MIURA IMAGE FORGE — Sistema Triple Motor[/]")
    console.print(f"  NVIDIA  : [green]{len(NVIDIA_KEYS)} keys[/]")
    console.print(f"  Replicate: {'[green]✅ Configurado[/]' if os.getenv('REPLICATE_API_TOKEN') else '[red]❌ Sin Token[/]'}")
    console.print(f"  Nebius  : {'[green]✅ Configurado[/]' if nebius_key else '[red]❌ Sin NEBIUS_API_KEY[/]'}")
    
    replicate_token = os.getenv("REPLICATE_API_TOKEN")

    if not NVIDIA_KEYS and not nebius_key and not replicate_token:
        console.print("[red]❌ No hay motores configurados en el .env (NVIDIA, Nebius o Replicate)[/]")
        return
    
    motor = seleccionar_motor()
    
    console.print(f"\n[bold]Modos de operación:[/]")
    console.print(f"  [cyan]1[/]) 🧪 Prueba Rápida      — 1 imagen de test")
    console.print(f"  [cyan]2[/]) ⚔️  Forja Masiva       — Genera TODOS desde el .md")
    console.print(f"  [yellow]3[/]) 🔧 Reparar Faltantes  — Solo regenera los clips que fallaron")
    console.print(f"  [cyan]4[/]) 🎨 Prompt Manual       — Escribe tu propio prompt")
    
    opc = Prompt.ask("Seleccione modo", choices=["1", "2", "3", "4"])
    
    if opc == "1":
        modo_prueba(motor)
    elif opc == "2":
        modo_masivo(motor)
    elif opc == "3":
        modo_reparar(motor)
    elif opc == "4":
        modo_manual(motor)

if __name__ == "__main__":
    main()
