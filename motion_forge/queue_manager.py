"""
queue_manager.py — MiuraForgeEngine
=====================================
Sistema de colas basado en archivos para el pipeline de video.
Si el proceso se cae a mitad, las tareas no se pierden —
se retoman desde donde quedaron.

Estructura de carpetas:
    queue/
    ├── pendientes/   ← tareas esperando procesarse
    ├── procesando/   ← tarea actualmente en curso
    ├── completados/  ← tareas exitosas
    └── fallidos/     ← tareas que fallaron (para revisar)
"""

import os
import json
import time
from pathlib import Path
from typing import Optional

QUEUE_DIR   = Path("queue")
PENDIENTES  = QUEUE_DIR / "pendientes"
PROCESANDO  = QUEUE_DIR / "procesando"
COMPLETADOS = QUEUE_DIR / "completados"
FALLIDOS    = QUEUE_DIR / "fallidos"

for d in [PENDIENTES, PROCESANDO, COMPLETADOS, FALLIDOS]:
    d.mkdir(parents=True, exist_ok=True)


def obtener_estado_sesion(id_sesion: str) -> Optional[str]:
    """
    Busca en qué parte de la cola se encuentra un id_sesion.
    Retorna 'pendientes', 'procesando', 'completados', 'fallidos' o None.
    """
    for estado, carpeta in [
        ("pendientes", PENDIENTES),
        ("procesando", PROCESANDO),
        ("completados", COMPLETADOS),
        ("fallidos", FALLIDOS)
    ]:
        # Las tareas tienen el formato {timestamp}_{id_sesion}.json
        if any(f.name.endswith(f"_{id_sesion}.json") for f in carpeta.iterdir()):
            return estado
    return None





def agregar_tarea(id_sesion: str, clips: list[dict]) -> str:
    """
    Agrega una tarea a la cola de pendientes.

    Args:
        id_sesion: ID del Short (ej: 'S1_W1_disciplina')
        clips: lista de dicts con 'imagen' y 'prompt_animacion'
                [{'imagen': 'ruta/clip_01.png', 'prompt': '...'},  ...]

    Returns:
        Nombre del archivo de tarea creado.
    """
    filename = f"{int(time.time() * 1000)}_{id_sesion}.json"
    path = PENDIENTES / filename

    data = {
        "id_sesion":  id_sesion,
        "clips":      clips,
        "creado_en":  time.time(),
        "intentos":   0,
    }
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return filename


def cargar_desde_carpeta(carpeta_short: str, id_sesion: str = "") -> str:
    """
    Helper: carga automáticamente los clips de una carpeta de Short.
    Empareja clip_01.png con clip_01_ANIMACION.txt, etc.

    Args:
        carpeta_short: ruta a la carpeta con imágenes y fichas
        id_sesion: nombre del Short (si vacío, usa el nombre de la carpeta)

    Returns:
        Nombre del archivo de tarea creado.
    """
    carpeta = Path(carpeta_short)
    if not id_sesion:
        id_sesion = carpeta.name

    clips = []
    imagenes = sorted(carpeta.glob("clip_*.png"))

    for img in imagenes:
        ficha = img.with_name(img.stem + "_ANIMACION.txt")
        prompt = ""
        if ficha.exists():
            contenido = ficha.read_text(encoding="utf-8")
            # Extraer solo la directiva de animación del .txt
            lines = contenido.splitlines()
            capture = False
            for line in lines:
                if "DIRECTIVA DE ANIMACIÓN" in line:
                    capture = True
                    continue
                if capture:
                    # Si llegamos a otra sección o al final de la ficha, paramos
                    if any(line.startswith(h) for h in ["GUION", "PROMPT ORIGINAL", "==="]):
                        break
                    if line.strip():
                        prompt += line.strip() + " "
            prompt = prompt.strip()

        clips.append({
            "imagen":  str(img),
            "prompt":  prompt,
            "nombre":  img.stem,
        })

    if not clips:
        raise ValueError(f"No se encontraron imágenes clip_*.png en {carpeta_short}")

    # Verificar si ya existe en algun estado de la cola
    estado = obtener_estado_sesion(id_sesion)
    if estado == "completados":
        print(f"  ✅ El Short '{id_sesion}' ya se encuentra COMPLETADO. Omitiendo.")
        return ""
    if estado in ["pendientes", "procesando"]:
        print(f"  ⏳ El Short '{id_sesion}' ya existe en la cola ({estado}). Omitiendo.")
        return ""

    return agregar_tarea(id_sesion, clips)


def obtener_siguiente() -> Optional[tuple[str, dict]]:
    """
    Toma la siguiente tarea pendiente y la mueve a 'procesando'.
    Retorna (filename, data) o None si no hay pendientes.
    """
    archivos = sorted(PENDIENTES.iterdir())
    if not archivos:
        return None

    archivo = archivos[0]
    destino = PROCESANDO / archivo.name
    archivo.rename(destino)

    data = json.loads(destino.read_text(encoding="utf-8"))
    return archivo.name, data


def marcar_completado(filename: str, clips_generados: list[str]):
    """Mueve la tarea a completados y registra los clips generados."""
    src = PROCESANDO / filename
    if not src.exists():
        return

    data = json.loads(src.read_text(encoding="utf-8"))
    data["completado_en"]    = time.time()
    data["clips_generados"]  = clips_generados

    dst = COMPLETADOS / filename
    dst.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    src.unlink()


def marcar_fallido(filename: str, error: str):
    """Mueve la tarea a fallidos con el mensaje de error."""
    src = PROCESANDO / filename
    if not src.exists():
        return

    data = json.loads(src.read_text(encoding="utf-8"))
    data["fallido_en"] = time.time()
    data["error"]      = error
    data["intentos"]   = data.get("intentos", 0) + 1

    dst = FALLIDOS / filename
    dst.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    src.unlink()


def reintentar_fallidos():
    """Mueve todas las tareas fallidas de vuelta a pendientes."""
    fallidos = list(FALLIDOS.iterdir())
    for f in fallidos:
        data = json.loads(f.read_text(encoding="utf-8"))
        if data.get("intentos", 0) < 3:
            dst = PENDIENTES / f.name
            f.rename(dst)
            print(f"  ↩️  Reintentando: {f.name}")
    return len(fallidos)


def estado_cola() -> dict:
    """Retorna un resumen del estado actual de la cola."""
    return {
        "pendientes":  len(list(PENDIENTES.iterdir())),
        "procesando":  len(list(PROCESANDO.iterdir())),
        "completados": len(list(COMPLETADOS.iterdir())),
        "fallidos":    len(list(FALLIDOS.iterdir())),
    }


def limpiar_procesando():
    """
    Recuperación de emergencia: si el proceso se cayó con tareas
    en 'procesando', las mueve de vuelta a pendientes.
    Llamar al inicio de cada sesión.
    """
    huerfanas = list(PROCESANDO.iterdir())
    for f in huerfanas:
        dst = PENDIENTES / f.name
        f.rename(dst)
        print(f"  🔄 Tarea huérfana recuperada: {f.name}")
    return len(huerfanas)


def auditar_directorio(ruta_base: str):
    """
    Analiza una carpeta que contiene múltiples carpetas de Shorts
    y muestra el estado de cada una en la cola.
    """
    ruta = Path(ruta_base)
    if not ruta.is_dir():
        print(f"❌ '{ruta_base}' no es un directorio válido.")
        return

    subcarpetas = sorted([d for d in ruta.iterdir() if d.is_dir()])
    print(f"\n{'='*60}")
    print(f"📊 REPORTE DE ESTADO MIURA FORGE: {ruta.name}")
    print(f"{'='*60}")
    print(f"{'Short/Carpeta':<45} | {'Estado':<12}")
    print(f"{'-'*45} | {'-'*12}")

    stats = {"pendientes": 0, "procesando": 0, "completados": 0, "fallidos": 0, "nuevo": 0}

    for d in subcarpetas:
        estado = obtener_estado_sesion(d.name)
        if not estado:
            estado = "nuevo"
        
        stats[estado] += 1
        iconos = {
            "completados": "✅ LISTO",
            "pendientes":  "⏳ EN COLA",
            "procesando":  "🏃 ACTIVO",
            "fallidos":    "❌ FALLIDO",
            "nuevo":       "📁 NUEVO"
        }
        print(f"{d.name[:45]:<45} | {iconos.get(estado, estado)}")

    print(f"{'='*60}")
    print(f"Resumen: {stats['completados']} listos, {stats['pendientes']} en cola, "
          f"{stats['fallidos']} fallidos, {stats['nuevo']} nuevos.")
    print(f"{'='*60}\n")
