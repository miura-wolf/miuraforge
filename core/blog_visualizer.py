"""
core/blog_visualizer.py — MiuraForgeEngine / Blog Visualizer
=============================================================
Módulo MF-003-Visual: Estética del Blog
Misión: Generar imágenes impactantes para las reseñas del blog usando Flux.

Motores en Cascada:
  1. NVIDIA Flux 2 Klein (Gratis / Filtro AGRESIVO)
  2. Nebius Flux Dev      (Créditos / Sin Filtro)
  3. Replicate Flux       (Económico / Sin Filtro)

Flujo:
  1. Toma Título y Resumen del Blog.
  2. Gemma 3 genera 1-3 prompts Ultra-Cinemáticos (Estilo Miura).
  3. Motor Flux forja la imagen y la guarda en el repo web.
"""

import os
import sys
import re
import base64
import requests
import time
import io
from pathlib import Path
from dotenv import load_dotenv

sys.path.append(str(Path(__file__).resolve().parent.parent))

from llm.factory import LLMFactory

load_dotenv()

# ---------------------------------------------------------------------------
# CONFIGURACIÓN DE RUTAS Y MOTORES
# ---------------------------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent
# La salida va directamente a la carpeta public del proyecto Astro
BLOG_IMAGES_BASE = BASE_DIR / "disciplinaenacero" / "public" / "images" / "blog"

# ---------------------------------------------------------------------------
# PROMPT: DISEÑADOR VISUAL (GEMMA 3)
# ---------------------------------------------------------------------------

PROMPT_VISUAL_DESIGNER = """Eres el Director Visual de Disciplina en Acero.
Tu misión es diseñar un PROMPT DE IMAGEN para Flux que capture la esencia de esta reseña de libro.

ESTÉTICA MIURA:
- Chiaroscuro (fuertes contrastes de luz y sombra).
- Colores: Gris acero, negro profundo, toques de naranja brasa, azul industrial frío.
- Atmósfera: Humo, metal, brutalismo arquitectónico, soledad, poder, peso.
- NO queremos: Personas sonriendo, colores brillantes, estética de stock photo, "inspiración" genérica.

INSTRUCCIONES PARA EL PROMPT:
- Escribe el prompt en INGLÉS.
- Sé descriptivo: texturas, tipo de iluminación, composición de cámara.
- Temática: Enfócate en la FILOSOFÍA del libro (ej: si es sobre hábitos, no dibujes a alguien corriendo, dibuja un yunque bajo presión o un engranaje de acero masivo).

ARTÍCULO: {titulo}
SINOPSIS: {resumen}

ENTREGA SOLO EL PROMPT EN INGLÉS. Sin introducciones.
"""

# ---------------------------------------------------------------------------
# MOTORES DE IMAGEN (Cascada Flux)
# ---------------------------------------------------------------------------

def _get_nvidia_keys():
    keys = []
    env_path = BASE_DIR / ".env"
    if env_path.exists():
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                if "OPENAI_API_KEY=" in line and "nvapi-" in line:
                    match = re.search(r'OPENAI_API_KEY=([a-zA-Z0-9_-]+)', line)
                    if match:
                        keys.append(match.group(1))
    return list(dict.fromkeys(keys))

NVIDIA_KEYS = _get_nvidia_keys()
_key_cursor = 0

def _generar_nvidia(prompt, output_path):
    global _key_cursor
    if not NVIDIA_KEYS: return False
    
    url = "https://ai.api.nvidia.com/v1/genai/black-forest-labs/flux.2-klein-4b"
    key = NVIDIA_KEYS[_key_cursor % len(NVIDIA_KEYS)]
    headers = {"Authorization": f"Bearer {key}", "Accept": "application/json"}
    payload = {"prompt": prompt, "width": 1024, "height": 1024, "seed": int(time.time()), "steps": 4}

    try:
        r = requests.post(url, headers=headers, json=payload)
        if r.status_code == 200:
            data = r.json()
            # Flux v1 or v2 artifacts mapping
            img_b64 = None
            if "artifacts" in data and data["artifacts"]:
                if data["artifacts"][0].get("finishReason") == "CONTENT_FILTERED":
                    print("  ⚠️ NVIDIA filtró el prompt.")
                    return False
                img_b64 = data["artifacts"][0].get("base64")
            elif "image" in data:
                img_b64 = data["image"]

            if img_b64:
                with open(output_path, "wb") as f:
                    f.write(base64.b64decode(img_b64))
                return True
        elif r.status_code in [401, 403, 429]:
            _key_cursor += 1 # Rotar key para el próximo intento
    except:
        pass
    return False

def _generar_replicate(prompt, output_path):
    token = os.getenv("REPLICATE_API_TOKEN")
    if not token: return False
    
    headers = {"Authorization": f"Token {token}", "Content-Type": "application/json"}
    payload = {
        "version": "131d9e185621b4b4d349fd262e363420a6f74081d8c27966c9c5bcf120fa3985", # Flux Schnell
        "input": {"prompt": prompt, "aspect_ratio": "1:1", "output_format": "png", "seed": int(time.time())}
    }
    try:
        r = requests.post("https://api.replicate.com/v1/predictions", json=payload, headers=headers)
        if r.status_code != 201: return False
        
        url_poll = r.json()["urls"]["get"]
        for _ in range(20):
            poll = requests.get(url_poll, headers=headers).json()
            if poll["status"] == "succeeded":
                img_url = poll["output"][0]
                img_data = requests.get(img_url).content
                with open(output_path, "wb") as f:
                    f.write(img_data)
                return True
            if poll["status"] in ["failed", "canceled"]: return False
            time.sleep(1.5)
    except:
        pass
    return False

def _generar_nebius(prompt, output_path):
    token = os.getenv("NEBIUS_API_KEY")
    if not token: return False
    
    url = "https://api.studio.nebius.ai/v1/images/generations"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    payload = {
        "model": "black-forest-labs/flux-dev",
        "prompt": prompt,
        "width": 1024,
        "height": 1024,
        "response_format": "b64_json",
        "seed": int(time.time()),
        "scheduler": "auto"
    }
    try:
        r = requests.post(url, headers=headers, json=payload)
        if r.status_code == 200:
            data = r.json()
            if "data" in data and len(data["data"]) > 0:
                img_b64 = data["data"][0]["b64_json"]
                with open(output_path, "wb") as f:
                    f.write(base64.b64decode(img_b64))
                return True
    except Exception as e:
        print(f"  ⚠️ Nebius falló: {e}")
    return False

def forjar_imagen_blog(prompt, output_path):
    """Ejecuta la cascada: Nebius -> NVIDIA -> Replicate."""
    print(f"🚀 Intentando Nebius (Flux Dev)...")
    if _generar_nebius(prompt, output_path):
        return True

    print(f"🎨 Intentando NVIDIA (Flux)...")
    if _generar_nvidia(prompt, output_path):
        return True
    
    print(f"💸 NVIDIA falló/filtró. Intentando Replicate (Flux Schnell)...")
    if _generar_replicate(prompt, output_path):
        return True
    
    return False

# ---------------------------------------------------------------------------
# PIPELINE: Diseñar + Forjar
# ---------------------------------------------------------------------------

def crear_visual_blog(titulo: str, resumen: str, slug: str = None) -> str:
    """
    Pipeline completo de visualización para el blog.
    Genera el prompt con Gemma 3 y la imagen con Flux.
    """
    # 1. Diseñar Prompt
    print(f"🧠 Gemma 3 diseñando estética para: {titulo}...")
    designer = LLMFactory.get_brain("merch")
    prompt_flux = designer.generate(PROMPT_VISUAL_DESIGNER.format(titulo=titulo, resumen=resumen))
    print(f"📝 Prompt forjado: {prompt_flux[:100]}...")

    # 2. Forjar Imagen
    filename = f"hero.png"
    target_dir = BLOG_IMAGES_BASE / (slug or "temp")
    target_dir.mkdir(parents=True, exist_ok=True)
    target_path = target_dir / filename

    if forjar_imagen_blog(prompt_flux.strip(), target_path):
        rel_path = f"/images/blog/{slug or 'temp'}/{filename}"
        print(f"✅ Imagen guardada: {target_path}")
        return rel_path
    else:
        print("❌ Error fatal: Todos los motores de imagen han fallado.")
        return ""

# ---------------------------------------------------------------------------
# TEST
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("🎨 Miura Blog Visualizer — Iniciando Test")
    test_titulo = "Habitos Atomicos"
    test_resumen = "Reseña sobre la disciplina de los pequeños habitos y la identidad de acero."
    crear_visual_blog(test_titulo, test_resumen, "test-visual")
