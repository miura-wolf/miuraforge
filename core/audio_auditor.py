#!/usr/bin/env python3
"""
===============================================================================
AUDIO AUDITOR - Sistema de Detección y Corrección de Problemas de Audio
===============================================================================

Sistema automatizado que:
- Detecta saltos de edición (jump cuts)
- Detecta repeticiones/tartamudeos
- Detecta problemas de dicción (sibilancia)
- Analiza energía y silencios
- Aplica correcciones automáticas

Uso:
    python audio_auditor.py <archivo.wav> [--corregir] [--pipeline]

Ejemplos:
    # Solo análisis
    python audio_auditor.py mi_audio.wav

    # Análisis + corrección automática
    python audio_auditor.py mi_audio.wav --corregir

    # Pipeline completo (análisis + procesamiento + corrección)
    python audio_auditor.py mi_audio.wav --pipeline
===============================================================================
"""

import os
import sys
import argparse
import numpy as np

# Dependencias
try:
    import librosa
    import soundfile as sf
    from pedalboard import (
        Pedalboard, HighpassFilter, LowpassFilter,
        Distortion, Compressor, Reverb, PeakFilter, Chorus
    )
    LIBRERIAS_DISPONIBLES = True
except ImportError:
    LIBRERIAS_DISPONIBLES = False
    print("⚠️ Advertencia: Librerías de audio no disponibles.")
    print("   Instala con: pip install librosa soundfile pedalboard numpy scipy")


# ============================================================================
# CONFIGURACIÓN
# ============================================================================

# Perfil objetivo para el pipeline cinematográfico
TARGET_PROFILE = {
    "spectral_centroid": 2000,  # voz oscura pero clara
    "rms": 0.12,                # energía controlada
    "low_energy_ratio": 0.25,   # presencia de graves
    "presence_band": 3000       # claridad en consonantes
}


# ============================================================================
# CLASE PRINCIPAL: AUDIO AUDITOR
# ============================================================================

class AudioAuditor:
    """
    Sistema de auditoría de audio que detecta y corrige problemas:
    - Saltos de edición (jump cuts)
    - Repeticiones/tartamudeos
    - Problemas de dicción (sibilancia)
    - Análisis energético
    """

    def __init__(self):
        """Inicializa el auditor."""
        self.problemas_detectados = []
        self.sugerencias = []
        self.ultimo_analisis = None

    def analizar_audio(self, audio_path: str) -> dict:
        """
        Analiza un archivo de audio y detecta problemas.
        Retorna un diccionario con el análisis completo.
        """
        if not LIBRERIAS_DISPONIBLES:
            print("⚠️ [Auditor] Librerías de análisis no disponibles")
            return {"error": "librerías no disponibles"}

        if not os.path.exists(audio_path):
            print(f"❌ [Auditor] Archivo no encontrado: {audio_path}")
            return {"error": "archivo no encontrado"}

        try:
            # Cargar audio
            y, sr = librosa.load(audio_path, sr=44100)

            print(f"🔍 [Auditor] Analizando: {audio_path}")
            print(f"   Duración: {len(y)/sr:.2f}s | Sample rate: {sr}Hz")

            # Análisis completo
            resultados = {
                "salto_edicion": self._detectar_saltos_edicion(y, sr),
                "repeticiones": self._detectar_repeticiones(y, sr),
                "sibilancia": self._detectar_sibilancia(y, sr),
                "energia": self._analizar_energia(y, sr),
                "silencios": self._analizar_silencios(y, sr),
                "calidad": self._analizar_calidad(y, sr)
            }

            self.ultimo_analisis = resultados
            return resultados

        except Exception as e:
            print(f"❌ [Auditor] Error en análisis: {e}")
            return {"error": str(e)}

    def _detectar_saltos_edicion(self, y, sr) -> dict:
        """
        Detecta saltos de edición (jump cuts) buscando
        transiciones abruptas en energía.
        """
        # Calcular energía por frames
        frame_length = int(sr * 0.05)  # 50ms frames
        hop_length = int(frame_length / 2)
        energy = np.array([
            np.sum(y[i:i+frame_length]**2)
            for i in range(0, len(y) - frame_length, hop_length)
        ])

        # Normalizar energía
        energy = energy / (np.max(energy) + 1e-9)

        # Detectar saltos abruptos
        threshold = 0.3
        min_silence = 0.05  # 50ms mínimo
        max_silence = 0.3    # 300ms máximo

        saltos = []
        in_silence = False
        silence_start = 0

        for i, e in enumerate(energy):
            if e < threshold and not in_silence:
                in_silence = True
                silence_start = i
            elif e >= threshold and in_silence:
                in_silence = False
                silence_duration = (i - silence_start) * hop_length / sr

                if min_silence < silence_duration < max_silence:
                    timestamp = silence_start * hop_length / sr
                    saltos.append({
                        "timestamp": round(timestamp, 3),
                        "duracion": round(silence_duration, 3),
                        "tipo": "salto_edicion"
                    })

        return {
            "detectado": len(saltos) > 0,
            "cantidad": len(saltos),
            "saltos": saltos
        }

    def _detectar_repeticiones(self, y, sr) -> dict:
        """
        Detecta repeticiones de palabras usando análisis de energía.
        """
        # Extraer envolvente
        frame_length = int(sr * 0.1)
        hop_length = int(frame_length / 4)
        energy = np.array([
            np.mean(y[i:i+frame_length]**2)
            for i in range(0, len(y) - frame_length, hop_length)
        ])

        # Detectar picos
        threshold = np.mean(energy) + np.std(energy)
        peaks = []

        for i in range(1, len(energy) - 1):
            if energy[i] > threshold and energy[i] > energy[i-1] and energy[i] > energy[i+1]:
                peaks.append(i)

        # Buscar patrones de repetición
        repeticiones = []
        min_distance = int(0.2 * sr / hop_length)

        for i in range(len(peaks) - 1):
            distance = peaks[i+1] - peaks[i]
            if distance < min_distance:
                timestamp = peaks[i] * hop_length / sr
                repeticiones.append({
                    "timestamp": round(timestamp, 3),
                    "distancia_picos": round(distance * hop_length / sr, 3),
                    "tipo": "posible_repeticion"
                })

        return {
            "detectado": len(repeticiones) > 0,
            "cantidad": len(repeticiones),
            "repeticiones": repeticiones
        }

    def _detectar_sibilancia(self, y, sr) -> dict:
        """
        Detecta problemas de sibilancia (sibilantes agresivas).
        Analiza las frecuencias altas (4kHz-12kHz).
        """
        fft = np.fft.rfft(y)
        freqs = np.fft.rfftfreq(len(y), 1/sr)

        # Banda de sibilancia
        sibilant_band = (freqs > 4000) & (freqs < 12000)
        sibilant_energy = np.sum(np.abs(fft[sibilant_band])**2)
        total_energy = np.sum(np.abs(fft)**2)
        sibilant_ratio = sibilant_energy / (total_energy + 1e-9)

        threshold = 0.15

        return {
            "detectado": sibilant_ratio > threshold,
            "ratio": round(sibilant_ratio, 4),
            "threshold": threshold,
            "severidad": "alta" if sibilant_ratio > 0.25 else "media" if sibilant_ratio > 0.15 else "baja"
        }

    def _analizar_energia(self, y, sr) -> dict:
        """Análisis general de energía del audio."""
        rms = np.sqrt(np.mean(y**2))
        peak = np.max(np.abs(y))

        return {
            "rms": round(rms, 4),
            "peak": round(peak, 4),
            "dinamica_db": round(20 * np.log10(peak / (rms + 1e-9)), 1)
        }

    def _analizar_silencios(self, y, sr) -> dict:
        """Análisis de silencios en el audio."""
        frame_length = int(sr * 0.05)
        energy = np.array([
            np.mean(y[i:i+frame_length]**2)
            for i in range(0, len(y) - frame_length, frame_length)
        ])

        threshold = np.mean(energy) * 0.1
        silencios = np.sum(energy < threshold)
        total_frames = len(energy)

        return {
            "silencio_ratio": round(silencios / total_frames, 3),
            "duracion_promedio": round(silencios * 0.05, 2)
        }

    def _analizar_calidad(self, y, sr) -> dict:
        """Análisis de calidad general del audio."""
        # Calcular SNR (Signal-to-Noise Ratio) aproximado
        signal_power = np.mean(y**2)
        noise_threshold = np.percentile(np.abs(y), 5)
        noise_mask = np.abs(y) < noise_threshold
        noise_power = np.mean(y[noise_mask]**2) if np.any(noise_mask) else 1e-10

        snr = 10 * np.log10(signal_power / (noise_power + 1e-10))

        # Detectar clipping
        clipping = np.sum(np.abs(y) > 0.99) / len(y)

        return {
            "snr_db": round(snr, 1),
            "clipping_ratio": round(clipping, 5),
            "calidad": "buena" if snr > 20 else "regular" if snr > 10 else "baja"
        }

    def aplicar_correcciones(self, audio_path: str, output_path: str) -> bool:
        """
        Aplica correcciones automáticas basadas en los problemas detectados.
        """
        if not LIBRERIAS_DISPONIBLES:
            return False

        try:
            analisis = self.analizar_audio(audio_path)
            print(f"🔍 [Auditor] Problemas detectados: {[k for k,v in analisis.items() if isinstance(v, dict) and v.get('detectado')]}")

            y, sr = librosa.load(audio_path, sr=44100)

            board = Pedalboard()

            # 1. Corrección de sibilancia
            if analisis.get("sibilancia", {}).get("detectado", False):
                severity = analisis["sibilancia"]["severidad"]
                if severity == "alta":
                    board.append(PeakFilter(cutoff_frequency_hz=6000, gain_db=-4, q=1.0))
                    board.append(PeakFilter(cutoff_frequency_hz=10000, gain_db=-3, q=1.0))
                    print("🔧 [Auditor] Corrección: Reducción de sibilancia (-4dB @ 6kHz)")
                elif severity == "media":
                    board.append(PeakFilter(cutoff_frequency_hz=8000, gain_db=-2, q=1.0))
                    print("🔧 [Auditor] Corrección: Reducción de sibilancia (-2dB @ 8kHz)")

            # 2. Corrección de saltos de edición
            if analisis.get("salto_edicion", {}).get("detectado", False):
                board.append(Reverb(room_size=0.15, wet_level=0.03, damping=0.8))
                print("🔧 [Auditor] Corrección: Suavizado de transiciones")

            # Aplicar
            if len(board.plugins) > 0:
                y = board(y, sr)
                print("✅ [Auditor] Correcciones aplicadas")
            else:
                print("✅ [Auditor] Sin correcciones necesarias")

            # Normalizar
            y = y / np.max(np.abs(y)) * 0.95

            sf.write(output_path, y, sr)
            print(f"💾 [Auditor] Audio corregido: {output_path}")
            return True

        except Exception as e:
            print(f"❌ [Auditor] Error: {e}")
            return False

    def aplicar_correcciones_from_array(self, audio, sr, output_path: str) -> bool:
        """Versión que trabaja con arrays numpy."""
        try:
            fft = np.fft.rfft(audio)
            freqs = np.fft.rfftfreq(len(audio), 1/sr)

            sibilant_band = (freqs > 4000) & (freqs < 12000)
            sibilant_energy = np.sum(np.abs(fft[sibilant_band])**2)
            total_energy = np.sum(np.abs(fft)**2)
            sibilant_ratio = sibilant_energy / (total_energy + 1e-9)

            board = Pedalboard()

            if sibilant_ratio > 0.15:
                board.append(PeakFilter(cutoff_frequency_hz=8000, gain_db=-2, q=1.0))
                print("🔧 [Auditor] Corrección de sibilancia aplicada")

            if len(board.plugins) > 0:
                audio = board(audio, sr)

            audio = audio / np.max(np.abs(audio)) * 0.95
            sf.write(output_path, audio, sr)
            return True

        except Exception as e:
            print(f"❌ [Auditor] Error: {e}")
            return False

    def generar_reporte(self, audio_path: str = None) -> str:
        """Genera un reporte textual del análisis."""
        if self.ultimo_analisis is None and audio_path:
            self.analizar_audio(audio_path)

        analisis = self.ultimo_analisis
        if not analisis:
            return "⚠️ No hay análisis disponible"

        reporte = []
        reporte.append("=" * 60)
        reporte.append("📋 REPORTE DE AUDITORÍA DE AUDIO")
        reporte.append("=" * 60)

        # Saltos de edición
        salto = analisis.get("salto_edicion", {})
        if salto.get("detectado"):
            reporte.append(f"\n⚠️ SALTOS DE EDICIÓN: {salto['cantidad']} detectado(s)")
            for s in salto.get("saltos", [])[:3]:
                reporte.append(f"   • Timestamp: {s['timestamp']}s | Duración: {s['duracion']}s")
        else:
            reporte.append("\n✅ Saltos de edición: No detectados")

        # Repeticiones
        rep = analisis.get("repeticiones", {})
        if rep.get("detectado"):
            reporte.append(f"\n⚠️ REPETICIONES: {rep['cantidad']} detectada(s)")
            for r in rep.get("repeticiones", [])[:3]:
                reporte.append(f"   • Timestamp: {r['timestamp']}s | Distancia: {r['distancia_picos']}s")
        else:
            reporte.append("\n✅ Repeticiones: No detectadas")

        # Sibilancia
        sib = analisis.get("sibilancia", {})
        if sib.get("detectado"):
            reporte.append(f"\n⚠️ SIBILANCIA: Severidad {sib['severidad'].upper()}")
            reporte.append(f"   Ratio: {sib['ratio']:.4f} (threshold: {sib['threshold']})")
            reporte.append(f"   → Aplicar corrección: --corregir")
        else:
            reporte.append("\n✅ Sibilancia: Dentro de parámetros normales")

        # Energía
        ene = analisis.get("energia", {})
        reporte.append(f"\n📊 ENERGÍA:")
        reporte.append(f"   RMS: {ene.get('rms', 0):.4f}")
        reporte.append(f"   Peak: {ene.get('peak', 0):.4f}")
        reporte.append(f"   Dinámica: {ene.get('dinamica_db', 0):.1f} dB")

        # Silencios
        sil = analisis.get("silencios", {})
        reporte.append(f"\n🔇 SILENCIOS:")
        reporte.append(f"   Ratio: {sil.get('silencio_ratio', 0):.1%}")

        # Calidad
        cal = analisis.get("calidad", {})
        reporte.append(f"\n🎵 CALIDAD GENERAL:")
        reporte.append(f"   SNR: {cal.get('snr_db', 0):.1f} dB")
        reporte.append(f"   Evaluación: {cal.get('calidad', 'N/A').upper()}")

        reporte.append("\n" + "=" * 60)

        return "\n".join(reporte)


# ============================================================================
# PIPELINE CINEMATOGRÁFICO
# ============================================================================

def cinematic_voice_pipeline(input_file: str, output_file: str,
                            target_profile: dict = None) -> bool:
    """
    Pipeline completo que:
    1. Analiza automáticamente
    2. Ajusta parámetros dinámicamente
    3. Procesa con Pedalboard
    4. Aplica correcciones del auditor
    5. Exporta audio final
    """
    if target_profile is None:
        target_profile = TARGET_PROFILE

    print("\n" + "=" * 60)
    print("🎬 PIPELINE CINEMATOGRÁFICO")
    print("=" * 60)

    if not LIBRERIAS_DISPONIBLES:
        print("❌ [Pipeline] Librerías no disponibles")
        return False

    try:
        # 1. Cargar audio
        print("📂 [Pipeline] Cargando audio...")
        audio, sr = librosa.load(input_file, sr=44100)

        # 2. Análisis acústico
        print("🔍 [Pipeline] Analizando perfil acústico...")
        metrics = {
            "centroid": np.mean(librosa.feature.spectral_centroid(y=audio, sr=sr)),
            "rms": np.mean(librosa.feature.rms(y=audio)),
        }

        stft = np.abs(librosa.stft(audio))
        freqs = librosa.fft_frequencies(sr=sr)
        low_band = np.sum(stft[(freqs < 200)])
        full_band = np.sum(stft)
        metrics["low_ratio"] = low_band / (full_band + 1e-9)

        print(f"   📊 Perfil detectado:")
        print(f"      • Centroid: {metrics['centroid']:.0f} Hz")
        print(f"      • RMS: {metrics['rms']:.3f}")
        print(f"      • Low ratio: {metrics['low_ratio']:.3f}")

        # 3. Ajuste dinámico
        print("\n⚙️  [Pipeline] Ajustando parámetros...")

        distortion = 12
        if metrics["centroid"] > target_profile["spectral_centroid"]:
            distortion += 2
            print("   → Distorsión aumentada (+2dB)")

        subharmonic_mix = 0.15
        if metrics["low_ratio"] < target_profile["low_energy_ratio"]:
            subharmonic_mix = 0.22
            print("   → Subarmónicos aumentados (+7%)")

        presence_boost = 0
        if metrics["centroid"] < target_profile["spectral_centroid"] * 0.8:
            presence_boost = 1.5
            print("   → Presencia aumentada (+1.5dB)")

        # 4. Procesamiento
        print("\n🎛️  [Pipeline] Procesando audio...")
        board = Pedalboard([
            HighpassFilter(cutoff_frequency_hz=70),

            # Tilt EQ
            PeakFilter(cutoff_frequency_hz=120, gain_db=2.0, q=0.7),
            PeakFilter(cutoff_frequency_hz=8000, gain_db=-2.0, q=0.7),

            # Formant shifting
            PeakFilter(cutoff_frequency_hz=500, gain_db=-2, q=2.0),
            PeakFilter(cutoff_frequency_hz=1500, gain_db=-3, q=2.0),
            PeakFilter(cutoff_frequency_hz=2500, gain_db=-2, q=2.0),

            # Presencia
            PeakFilter(cutoff_frequency_hz=3000, gain_db=3.0 + presence_boost, q=1.0),

            # Distorsión
            Distortion(drive_db=distortion),

            # Compresión
            Compressor(threshold_db=-24, ratio=5, attack_ms=8, release_ms=150),

            # Reverb
            Reverb(room_size=0.22, wet_level=0.05, damping=0.6)
        ])

        processed = board(audio, sr)

        # 5. Subarmónicos
        print("🎸 [Pipeline] Añadiendo subarmónicos...")
        dark_layer = librosa.effects.pitch_shift(processed, sr=sr, n_steps=-2.5)
        processed = processed + (dark_layer * subharmonic_mix)

        # 6. Micro-chorus
        print("🔊 [Pipeline] Aplicando micro-chorus...")
        left = processed.copy()
        right = processed.copy()

        chorus_l = Chorus(rate_hz=0.18, depth=0.07, mix=0.05)
        chorus_r = Chorus(rate_hz=0.21, depth=0.06, mix=0.05)

        left = chorus_l(left, sr)
        right = chorus_r(right, sr)

        final_audio = np.vstack([left, right]).T

        # 7. Normalizar
        final_audio = final_audio / np.max(np.abs(final_audio)) * 0.95

        # 8. Auditoría
        print("\n🔍 [Pipeline] Ejecutando auditoría final...")
        auditor = AudioAuditor()
        temp_output = output_file.replace('.wav', '_temp.wav')
        auditor.aplicar_correcciones_from_array(final_audio, sr, temp_output)

        if os.path.exists(temp_output):
            final_audio, sr = librosa.load(temp_output, sr=44100)
            os.remove(temp_output)

        # 9. Exportar
        sf.write(output_file, final_audio, sr)

        print(f"\n✅ [Pipeline] Audio generado: {output_file}")
        print("=" * 60)

        # 10. Reporte
        print(auditor.generar_reporte(output_file))

        return True

    except Exception as e:
        print(f"❌ [Pipeline] Error: {e}")
        import traceback
        traceback.print_exc()
        return False




# ============================================================================
# PUNTO DE ENTRADA
# ============================================================================

def main():
    """Función principal."""
    parser = argparse.ArgumentParser(
        description="Audio Auditor - Sistema de detección y corrección de audio",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos:
  python audio_auditor.py mi_audio.wav              # Solo análisis
  python audio_auditor.py mi_audio.wav --corregir   # Análisis + corrección
  python audio_auditor.py mi_audio.wav --pipeline   # Pipeline completo
  python audio_auditor.py *.wav --batch            # Procesar lote
        """
    )

    parser.add_argument(
        "input",
        nargs="?",
        help="Archivo de audio a procesar"
    )

    parser.add_argument(
        "--corregir", "-c",
        action="store_true",
        help="Aplicar correcciones automáticas"
    )

    parser.add_argument(
        "--pipeline", "-p",
        action="store_true",
        help="Ejecutar pipeline cinematográfico completo"
    )

    parser.add_argument(
        "--batch", "-b",
        action="store_true",
        help="Procesar todos los archivos .wav en la carpeta"
    )

    parser.add_argument(
        "--output", "-o",
        help="Archivo de salida (para pipeline)"
    )

    args = parser.parse_args()

    # Verificar librerías
    if not LIBRERIAS_DISPONIBLES:
        print("\n❌ ERROR: Librerías requeridas no instaladas")
        print("   Ejecuta: pip install librosa soundfile pedalboard numpy scipy")
        sys.exit(1)

    # Procesamiento por lotes
    if args.batch:
        import glob
        archivos = glob.glob("*.wav")
        if not archivos:
            print("❌ No se encontraron archivos .wav")
            sys.exit(1)

        print(f"\n📁 Procesando {len(archivos)} archivos...\n")
        auditor = AudioAuditor()

        for archivo in archivos:
            print(f"\n--- {archivo} ---")
            if args.pipeline:
                output = archivo.replace(".wav", "_cinematico.wav")
                cinematic_voice_pipeline(archivo, output)
            else:
                auditor.analizar_audio(archivo)
                print(auditor.generar_reporte())

                if args.corregir:
                    output = archivo.replace(".wav", "_corregido.wav")
                    auditor.aplicar_correcciones(archivo, output)

        print(f"\n✅ Lote procesado: {len(archivos)} archivos")
        return

    # Procesamiento individual
    if not args.input:
        parser.print_help()
        sys.exit(1)

    if not os.path.exists(args.input):
        print(f"❌ Archivo no encontrado: {args.input}")
        sys.exit(1)

    # Pipeline completo
    if args.pipeline:
        output = args.output or args.input.replace(".wav", "_cinematico.wav")
        cinematic_voice_pipeline(args.input, output)
        return

    # Solo análisis
    auditor = AudioAuditor()
    auditor.analizar_audio(args.input)
    print(auditor.generar_reporte())

    # Corrección si se pide
    if args.corregir:
        output = args.output or args.input.replace(".wav", "_corregido.wav")
        print(f"\n🔧 Aplicando correcciones...")
        auditor.aplicar_correcciones(args.input, output)


if __name__ == "__main__":
    main()
