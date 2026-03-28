"""
audio_cleaner.py — MiuraForgeEngine
=====================================
Limpiador de WAVs descargados manualmente de MiniMax.

Corrige dos defectos conocidos de MiniMax al exportar:

  1. HEADER CORRUPTO — MiniMax escribe 2,147,483,647 (0x7FFFFFFF)
     en el campo de frames cuando el audio supera cierto umbral.
     Cualquier librería que lea el header reporta 18.6 horas de duración.
     Este script recalcula el número real de frames desde el tamaño
     del archivo y reescribe el header correctamente.

  2. COLA ESPURIA — Después del guion, el modelo a veces genera
     fragmentos adicionales de voz (ráfagas de 0.3-0.8s separadas
     por silencio profundo). Suenan como murmullos o sílabas sueltas.
     Este script detecta el último momento de voz sostenida real
     y trunca el audio ahí, dejando solo un fade-out limpio.

Uso:
  # Limpiar un solo archivo (sobreescribe el original):
  python audio_cleaner.py archivo.wav

  # Limpiar un archivo y guardar la versión limpia por separado:
  python audio_cleaner.py archivo.wav --sufijo _clean

  # Limpiar toda una carpeta:
  python audio_cleaner.py carpeta/ --sufijo _clean

  # Limpiar toda una carpeta sobreescribiendo los originales:
  python audio_cleaner.py carpeta/

  # Ver diagnóstico sin modificar nada:
  python audio_cleaner.py archivo.wav --solo-diagnostico
"""

import os
import sys
import wave
import math
import struct
import argparse
import numpy as np
from pathlib import Path


# ---------------------------------------------------------------------------
# CONFIGURACIÓN
# ---------------------------------------------------------------------------

# Umbral para considerar un frame como "activo" (tiene voz)
UMBRAL_ACTIVIDAD    = 0.008   # amplitud RMS mínima (~-42 dBFS)

# Duración mínima de silencio para considerar que el guion terminó
# MiniMax pausa naturalmente entre frases (~0.3-0.8s)
# Pero la cola espuria viene después de silencio profundo (>1s)
SILENCIO_MIN_FIN    = 1.2     # segundos de silencio que marca fin del guion

# Duración mínima de voz sostenida para NO considerar algo como cola espuria
# (evita cortar pausas largas dentro del guion)
VOZ_MIN_SOSTENIDA   = 0.4     # segundos mínimos de voz continua para ser "real"

# Fade-out al final del corte (evita click abrupto)
FADE_OUT_MS         = 80      # milisegundos

# Valor máximo de frames en header MiniMax corrupto
FRAMES_CORRUPTO     = 2_147_483_647   # 0x7FFFFFFF


# ---------------------------------------------------------------------------
# DIAGNÓSTICO
# ---------------------------------------------------------------------------

def diagnosticar(path: Path) -> dict:
    """
    Analiza un WAV y retorna un dict con los problemas encontrados.
    No modifica el archivo.
    """
    resultado = {
        "path":            str(path),
        "header_corrupto": False,
        "cola_espuria":    False,
        "duracion_header": 0.0,
        "duracion_real":   0.0,
        "duracion_util":   0.0,
        "segundos_cola":   0.0,
        "rate":            0,
        "canales":         0,
        "sampwidth":       0,
    }

    with wave.open(str(path), 'r') as w:
        rate      = w.getframerate()
        ch        = w.getnchannels()
        sw        = w.getsampwidth()
        frames_hdr = w.getnframes()
        raw       = w.readframes(frames_hdr)

    resultado["rate"]      = rate
    resultado["canales"]   = ch
    resultado["sampwidth"] = sw

    # Duración según header
    resultado["duracion_header"] = frames_hdr / rate

    # Duración real desde el tamaño de los datos
    bytes_audio = len(raw)
    frames_real = bytes_audio // (ch * sw)
    resultado["duracion_real"] = frames_real / rate

    # Detectar header corrupto
    if frames_hdr == FRAMES_CORRUPTO:
        resultado["header_corrupto"] = True

    # Convertir a float mono
    dtype = np.int16 if sw == 2 else np.int32
    s = np.frombuffer(raw, dtype=dtype).astype(np.float64)
    if sw == 2:
        s /= 32768.0
    else:
        s /= 2147483648.0

    # Si es estéreo, mezclar a mono
    if ch == 2:
        s = s.reshape(-1, 2).mean(axis=1)

    # Detectar dónde termina el guion real
    duracion_util = _encontrar_fin_guion(s, rate)
    resultado["duracion_util"] = duracion_util

    cola = resultado["duracion_real"] - duracion_util
    resultado["segundos_cola"] = max(0.0, cola)

    # Hay cola espuria si hay más de 1 segundo después del fin del guion
    if cola > 1.0:
        resultado["cola_espuria"] = True

    return resultado


def _encontrar_fin_guion(samples: np.ndarray, rate: int) -> float:
    """
    Encuentra el punto real donde termina el guion (última voz sostenida).

    Algoritmo:
    1. Divide el audio en ventanas de 20ms
    2. Calcula la energía de cada ventana
    3. Busca el último bloque de voz sostenida (>= VOZ_MIN_SOSTENIDA)
       seguido de silencio largo (>= SILENCIO_MIN_FIN)
    4. Retorna el tiempo en segundos de ese punto
    """
    fsz = int(rate * 0.02)  # ventana de 20ms
    n_frames = len(samples) // fsz

    # Energía por ventana
    energias = np.array([
        math.sqrt(np.mean(samples[i*fsz:(i+1)*fsz]**2) + 1e-12)
        for i in range(n_frames)
    ])

    activo = energias > UMBRAL_ACTIVIDAD

    # Buscar desde el final hacia atrás el último bloque de voz sostenida
    # seguido de silencio profundo
    min_frames_silencio = int(SILENCIO_MIN_FIN / 0.02)
    min_frames_voz      = int(VOZ_MIN_SOSTENIDA / 0.02)

    # Recorrer de atrás hacia adelante buscando el patrón:
    # [voz sostenida] → [silencio largo] → [más cosas]
    i = n_frames - 1
    while i >= min_frames_voz:
        # ¿Hay silencio largo terminando aquí?
        bloque = activo[max(0, i - min_frames_silencio):i]
        if len(bloque) > 0 and not np.any(bloque):
            # Hay silencio. ¿Hay voz sostenida antes?
            inicio_silencio = i - min_frames_silencio
            if inicio_silencio >= min_frames_voz:
                bloque_voz = activo[max(0, inicio_silencio - min_frames_voz):inicio_silencio]
                if np.sum(bloque_voz) >= min_frames_voz * 0.6:
                    # Encontrado: fin del guion en inicio_silencio
                    return (inicio_silencio * fsz) / rate
        i -= 1

    # Si no se detectó patrón, retornar la duración completa
    return len(samples) / rate


# ---------------------------------------------------------------------------
# CORRECCIÓN
# ---------------------------------------------------------------------------

def limpiar_wav(path: Path, sufijo: str = "") -> Path:
    """
    Corrige el header corrupto y elimina la cola espuria de un WAV de MiniMax.

    Args:
        path:   ruta al WAV original
        sufijo: si vacío, sobreescribe el original
                si no vacío (ej: '_clean'), guarda como archivo nuevo

    Returns:
        Ruta del archivo corregido.
    """
    diag = diagnosticar(path)

    if not diag["header_corrupto"] and not diag["cola_espuria"]:
        print(f"  ✅ {path.name} — sin problemas detectados")
        return path

    # Leer audio crudo
    with wave.open(str(path), 'r') as w:
        rate = w.getframerate()
        ch   = w.getnchannels()
        sw   = w.getsampwidth()
        raw  = w.readframes(w.getnframes())

    # Calcular frames reales
    frames_real = len(raw) // (ch * sw)

    # Convertir a float para procesamiento
    dtype = np.int16 if sw == 2 else np.int32
    s_raw = np.frombuffer(raw, dtype=dtype).copy()

    # Convertir a float mono para análisis
    s_float = s_raw.astype(np.float64)
    if sw == 2:
        s_float /= 32768.0
    else:
        s_float /= 2147483648.0

    s_mono = s_float.reshape(-1, ch).mean(axis=1) if ch == 2 else s_float

    # Encontrar fin del guion
    fin_guion_s  = _encontrar_fin_guion(s_mono, rate)
    fin_guion_f  = int(fin_guion_s * rate)  # en frames

    # Añadir fade-out
    fade_frames = int(rate * FADE_OUT_MS / 1000)
    fin_con_fade = min(fin_guion_f + fade_frames, frames_real)

    # Construir fade-out
    fade_lineal = np.linspace(1.0, 0.0, fade_frames)

    # Recortar el audio crudo al punto de corte + fade
    samples_por_frame = ch  # muestras por frame
    corte_muestras    = fin_guion_f * samples_por_frame
    fade_muestras     = fade_frames * samples_por_frame

    s_recortado = s_raw[:corte_muestras + fade_muestras].copy()

    # Aplicar fade-out en el canal(es)
    for canal in range(ch):
        indices_fade = np.arange(canal, min(len(s_recortado), corte_muestras + fade_muestras), ch)
        indices_voz  = indices_fade[:len(indices_fade) - fade_frames * 1]
        indices_fade_solo = indices_fade[len(indices_voz):]

        if len(indices_fade_solo) > 0:
            fade_aplicado = fade_lineal[:len(indices_fade_solo)]
            s_recortado[indices_fade_solo] = (
                s_recortado[indices_fade_solo].astype(np.float64) * fade_aplicado
            ).astype(dtype)

    # Determinar ruta de salida
    if sufijo:
        output_path = path.parent / (path.stem + sufijo + path.suffix)
    else:
        output_path = path

    # Escribir WAV corregido con header correcto
    frames_finales = len(s_recortado) // ch
    with wave.open(str(output_path), 'w') as w_out:
        w_out.setnchannels(ch)
        w_out.setsampwidth(sw)
        w_out.setframerate(rate)
        w_out.writeframes(s_recortado.tobytes())

    # Verificar que el header quedó bien
    with wave.open(str(output_path), 'r') as w_check:
        frames_escritos = w_check.getnframes()

    # Reporte
    dur_original = diag["duracion_real"]
    dur_final    = frames_finales / rate
    cola_cortada = dur_original - dur_final

    acciones = []
    if diag["header_corrupto"]:
        acciones.append("header corregido")
    if diag["cola_espuria"]:
        acciones.append(f"cola cortada ({cola_cortada:.1f}s)")

    print(f"  🔧 {path.name}")
    print(f"     Duración: {dur_original:.1f}s → {dur_final:.1f}s")
    print(f"     Acciones: {', '.join(acciones)}")
    if sufijo:
        print(f"     Guardado: {output_path.name}")

    return output_path


# ---------------------------------------------------------------------------
# PROCESAMIENTO EN LOTE
# ---------------------------------------------------------------------------

def limpiar_carpeta(carpeta: Path, sufijo: str = "", recursivo: bool = False):
    """
    Limpia todos los WAVs en una carpeta.
    """
    patron   = "**/*.wav" if recursivo else "*.wav"
    archivos = sorted(carpeta.glob(patron))

    if not archivos:
        print(f"❌ No se encontraron WAVs en {carpeta}")
        return

    print(f"\n🔩 Limpiando {len(archivos)} WAV(s) en {carpeta}")
    print(f"{'─'*60}")

    limpios   = 0
    corregidos = 0
    errores    = 0

    for wav in archivos:
        try:
            diag = diagnosticar(wav)
            tiene_problemas = diag["header_corrupto"] or diag["cola_espuria"]

            if tiene_problemas:
                limpiar_wav(wav, sufijo)
                corregidos += 1
            else:
                print(f"  ✅ {wav.name} — sin problemas")
                limpios += 1
        except Exception as e:
            print(f"  ❌ {wav.name} — error: {e}")
            errores += 1

    print(f"\n{'─'*60}")
    print(f"📊 Resumen:")
    print(f"   Sin problemas: {limpios}")
    print(f"   Corregidos:    {corregidos}")
    print(f"   Errores:       {errores}")


def imprimir_diagnostico(path: Path):
    """Imprime un diagnóstico detallado sin modificar el archivo."""
    diag = diagnosticar(path)

    print(f"\n🔍 Diagnóstico: {path.name}")
    print(f"{'─'*50}")
    print(f"  Sample rate:      {diag['rate']} Hz")
    print(f"  Canales:          {diag['canales']}")
    print(f"  Duración real:    {diag['duracion_real']:.2f}s")
    print(f"  Duración guion:   {diag['duracion_util']:.2f}s")
    print()

    if diag["header_corrupto"]:
        print(f"  ⚠️  HEADER CORRUPTO — frames declarados: {FRAMES_CORRUPTO:,}")
        print(f"      Duración falsa: {diag['duracion_header']:.0f}s ({diag['duracion_header']/3600:.1f}h)")
        print(f"      Duración real:  {diag['duracion_real']:.2f}s ✓")
    else:
        print(f"  ✅ Header correcto")

    if diag["cola_espuria"]:
        print(f"  ⚠️  COLA ESPURIA — {diag['segundos_cola']:.1f}s de audio después del guion")
        print(f"      Se cortará en: {diag['duracion_util']:.2f}s + fade-out de {FADE_OUT_MS}ms")
    else:
        print(f"  ✅ Sin cola espuria")

    if not diag["header_corrupto"] and not diag["cola_espuria"]:
        print(f"\n  ✅ Archivo limpio — no requiere corrección")
    else:
        print(f"\n  → Para corregir: python audio_cleaner.py {path}")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Limpiador de WAVs de MiniMax — corrige header y cola espuria"
    )
    parser.add_argument(
        "entrada",
        help="Archivo .wav o carpeta con WAVs"
    )
    parser.add_argument(
        "--sufijo", default="",
        help="Sufijo para el archivo limpio (ej: '_clean'). "
             "Sin sufijo sobreescribe el original."
    )
    parser.add_argument(
        "--solo-diagnostico", action="store_true",
        help="Solo muestra el diagnóstico sin modificar archivos"
    )
    parser.add_argument(
        "--recursivo", action="store_true",
        help="Buscar WAVs en subcarpetas también"
    )
    args = parser.parse_args()

    entrada = Path(args.entrada)

    if not entrada.exists():
        print(f"❌ No existe: {entrada}")
        sys.exit(1)

    if entrada.is_dir():
        if args.solo_diagnostico:
            wavs = sorted(entrada.glob("**/*.wav" if args.recursivo else "*.wav"))
            for wav in wavs:
                imprimir_diagnostico(wav)
        else:
            limpiar_carpeta(entrada, args.sufijo, args.recursivo)

    elif entrada.suffix.lower() == ".wav":
        if args.solo_diagnostico:
            imprimir_diagnostico(entrada)
        else:
            limpiar_wav(entrada, args.sufijo)
    else:
        print(f"❌ El archivo debe ser .wav: {entrada}")
        sys.exit(1)
