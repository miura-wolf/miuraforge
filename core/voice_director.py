import os
import wave
import math
import subprocess
import tempfile
import numpy as np
import requests
from pathlib import Path
from dotenv import load_dotenv
from tenacity import retry, stop_after_attempt, wait_exponential

# Post-procesamiento Profesional (Pedalboard)
try:
    import librosa
    import soundfile as sf
    from pedalboard import Pedalboard, HighpassFilter, LowpassFilter, Distortion, Compressor, Reverb, PeakFilter, Chorus
    PEDALBOARD_DISPONIBLE = True
    # Importar el Auditor de Audio para el pipeline dinámico
    from core.audio_auditor import AudioAuditor, cinematic_voice_pipeline
except ImportError:
    PEDALBOARD_DISPONIBLE = False

load_dotenv()

# ---------------------------------------------------------------------------
# RUTAS BASE — todo relativo a la raíz de MiuraForgeEngine
# Resuelve la ruta absoluta en tiempo de ejecución sin importar
# dónde esté instalado el proyecto en disco.
# ---------------------------------------------------------------------------

# __file__ es modules/voice_director.py → .parent.parent = raíz del proyecto
_MIURA_ROOT = Path(__file__).resolve().parent.parent

def _ruta(env_var: str, default_relativo: str) -> Path:
    """
    Resuelve una ruta: primero busca en .env (puede ser absoluta o relativa),
    si no existe usa el default relativo a la raíz de Miura.
    """
    val = os.getenv(env_var, "")
    if val:
        p = Path(val)
        return p if p.is_absolute() else _MIURA_ROOT / p
    return _MIURA_ROOT / default_relativo


# ---------------------------------------------------------------------------
# POST-PROCESSOR — EQ graves + normalización a -14 dBFS
# Se aplica a TODO audio generado, sin importar el proveedor
# ---------------------------------------------------------------------------

def _post_procesar_wav(input_path: str, output_path: str, corte_agudos_db: float = 2.0) -> bool:
    """
    EQ boost de graves (<300Hz +3dB) + corte suave de agudos (>3kHz configurable)
    + normalización de volumen a -14 dBFS sobre segmentos activos.
    
    corte_agudos_db: dB a reducir en agudos >3kHz.
        - ElevenLabs: 2.0 dB (default)
        - Supertonic:  1.0 dB (M4 ya tiene agudos bajos de base, no apilar dos cortes)
    """
    try:
        with wave.open(input_path, 'r') as w:
            rate = w.getframerate()
            ch   = w.getnchannels()
            sw   = w.getsampwidth()
            raw  = w.readframes(w.getnframes())

        samples = np.frombuffer(raw, dtype=np.int16).astype(np.float64) / 32768.0

        # --- Compresor suave de transientes ---
        # Supertonic genera audio con peak ya en 0.98 (el runner hace clip interno).
        # Sin compresión, el EQ de graves (+3dB) lleva el peak a >1.1 y el limiter
        # recorta antes de que la normalización RMS pueda llegar al target -14dBFS.
        # Ratio 3:1 sobre umbral -6dBFS: baja transientes sin cambiar el carácter de la voz.
        umbral_comp = 10 ** (-6.0 / 20.0)   # -6 dBFS
        ratio_comp  = 3.0
        abs_samples = np.abs(samples)
        mascara_comp = abs_samples > umbral_comp
        gain_comp = np.where(
            mascara_comp,
            (umbral_comp * (abs_samples / umbral_comp) ** (1.0 / ratio_comp)) / (abs_samples + 1e-9),
            1.0
        )
        samples = samples * gain_comp

        # --- EQ en dominio de frecuencias ---
        fft   = np.fft.rfft(samples)
        freqs = np.fft.rfftfreq(len(samples), 1.0 / rate)
        mask  = np.ones(len(freqs))
        mask[freqs < 300]  = 10 ** ( 3.0 / 20.0)   # +3 dB graves
        mask[freqs > 3000] = 10 ** (-corte_agudos_db / 20.0)  # configurable por proveedor
        samples = np.fft.irfft(fft * mask)[:len(samples)]

        # --- Limiter post-EQ: controla el peak que el boost de graves puede disparar ---
        # Debe ir ANTES de la normalización RMS para no bloquearla.
        peak = np.max(np.abs(samples))
        if peak > 0.98:
            samples = samples * (0.98 / peak)

        # --- Normalización RMS a -14 dBFS (sobre segmentos activos, ignorando silencios) ---
        # Calcular RMS solo en frames donde hay señal real (>1% amplitud).
        # Evita que las pausas largas de Supertonic entre frases bajen el RMS promedio
        # y bloqueen la subida de ganancia necesaria para llegar al target.
        target_rms = 10 ** (-14.0 / 20.0)
        frame_sz   = int(rate * 0.02)  # frames de 20ms
        frames_activos = [
            samples[i:i+frame_sz]
            for i in range(0, len(samples) - frame_sz, frame_sz)
            if np.sqrt(np.mean(samples[i:i+frame_sz]**2)) > 0.01
        ]
        if frames_activos:
            activos = np.concatenate(frames_activos)
            current_rms = math.sqrt(np.mean(activos ** 2) + 1e-9)
        else:
            current_rms = math.sqrt(np.mean(samples ** 2) + 1e-9)
        samples = samples * (target_rms / current_rms)

        # --- Limiter final de seguridad anti-clipping ---
        peak = np.max(np.abs(samples))
        if peak > 0.98:
            samples = samples * (0.98 / peak)

        samples_int16 = (samples * 32768).astype(np.int16)
        with wave.open(output_path, 'w') as w_out:
            w_out.setnchannels(ch)
            w_out.setsampwidth(sw)
            w_out.setframerate(rate)
            w_out.writeframes(samples_int16.tobytes())

        return True

    except Exception as e:
        print(f"❌ [PostProcessor] Error en EQ/normalización: {e}")
        return False


# ---------------------------------------------------------------------------
def _forjar_voz_acero_v2(audio_input: str, audio_output: str):
    """
    VERSIÓN 2.0 (Dinámica) - Utiliza el AudioAuditor para un ajuste inteligente.
    """
    if not PEDALBOARD_DISPONIBLE:
        return False

    try:
        # Llamar al pipeline cinematográfico del Auditor
        return cinematic_voice_pipeline(audio_input, audio_output)
    except Exception as e:
        print(f"❌ [VoiceDirector] Error en pipeline dinámico: {e}")
        return False

# ---------------------------------------------------------------------------
def _forjar_voz_acero(audio_input: str, audio_output: str):
    """
    Aplica la cadena de efectos 'Pedalboard' para una voz cinematográfica y fría.
    Highpass -> EQ -> Saturación -> Compresión -> Reverb -> Subtono oscuro
    """
    if not PEDALBOARD_DISPONIBLE:
        return False

    try:
        # 1. Cargar audio
        y, sr = librosa.load(audio_input, sr=44100)

        # 2. Crear cadena de efectos
        board = Pedalboard([
            HighpassFilter(cutoff_frequency_hz=70),
            LowpassFilter(cutoff_frequency_hz=10000), # Mayor frialdad
            Distortion(drive_db=14), # Más metálico (armónicos impares)
            PeakFilter(cutoff_frequency_hz=3000, gain_db=3.0, q=1.0), # Presencia / Autoridad de mando
            Compressor(
                threshold_db=-24, # Menos dinámica, más presión constante
                ratio=5,
                attack_ms=8,
                release_ms=150
            ),
            # Reverb ajustada: sala de piedra, no catedral
            Reverb(
                room_size=0.22,
                damping=0.6,
                wet_level=0.07,
                dry_level=1.0
            )
        ])

        # 3. Aplicar efectos
        processed = board(y, sr)

        # 4. Crear subtono oscuro (Pitch shift -2.5 steps para autoridad)
        # Efecto psicoacústico "Fantasma Grave"
        dark_layer = librosa.effects.pitch_shift(processed, sr=sr, n_steps=-2.5)
        # Reforzando el fantasma grave al 20% (Subharmonic Reinforcement)
        final_audio = processed + (dark_layer * 0.20)

        # 5. Normalizar
        max_val = np.max(np.abs(final_audio))
        if max_val > 0:
            final_audio = (final_audio / max_val) * 0.95

        # 6. Exportar
        sf.write(audio_output, final_audio, sr)
        return True
    except Exception as e:
        print(f"❌ [Pedalboard] Error forjando voz: {e}")
        return False


# ---------------------------------------------------------------------------
# SUPERTONIC RUNNER — script interno llamado por subprocess en Python 3.11
# ---------------------------------------------------------------------------

_SUPERTONIC_RUNNER = '''
import sys
import wave
import json
import argparse
import numpy as np

def run(onnx_dir, voice_style, texto, lang, output_path):
    try:
        sys.path.insert(0, "{py_dir}")
        from helper import load_text_to_speech, Style

        tts = load_text_to_speech(onnx_dir, use_gpu=False)

        with open(voice_style, "r") as f:
            j = json.load(f)
            style = Style(
                np.array(j["style_ttl"]["data"], dtype=np.float32).reshape(j["style_ttl"]["dims"]),
                np.array(j["style_dp"]["data"], dtype=np.float32).reshape(j["style_dp"]["dims"])
            )

        result = tts(
            text=texto,
            lang=lang,
            style=style,
            total_step=16,
            speed=1.0
        )

        audio = result[0]
        samples_int16 = (audio * 32768).clip(-32768, 32767).astype("int16")

        with wave.open(output_path, "w") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(44100)
            wf.writeframes(samples_int16.tobytes())

        print(f"OK:{output_path}")

    except Exception as e:
        import traceback
        print(f"ERROR:{str(e)}")
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--onnx-dir")
    p.add_argument("--voice-style")
    p.add_argument("--text")
    p.add_argument("--lang", default="es")
    p.add_argument("--output")
    args = p.parse_args()
    run(args.onnx_dir, args.voice_style, args.text, args.lang, args.output)
'''


# ---------------------------------------------------------------------------
# VOICE DIRECTOR
# ---------------------------------------------------------------------------

class VoiceDirector:
    def __init__(self):
        # --- ElevenLabs ---
        self.api_key  = os.getenv("ELEVENLABS_API_KEY")
        self.voice_id = os.getenv("VOICE_ID")
        self.url      = f"https://api.elevenlabs.io/v1/text-to-speech/{self.voice_id}"

        if not self.api_key or not self.voice_id:
            print("⚠️ [VoiceDirector] Faltan credenciales de ElevenLabs en el .env")

        # --- Supertonic / MiuraSteel (fallback offline) ---
        # Rutas resueltas relativas a la raíz de MiuraForgeEngine/.
        # Para activar MiuraSteel solo apuntar SUPERTONIC_VOICE_STYLE al nuevo JSON.
        self.supertonic_python = str(_ruta(
            "SUPERTONIC_PYTHON",
            r"supertonic\py\.venv311\Scripts\python.exe"
        ))
        self.supertonic_onnx_dir = str(_ruta(
            "SUPERTONIC_ONNX_DIR",
            r"supertonic\assets\onnx"
        ))
        self.supertonic_voice_style = str(_ruta(
            "SUPERTONIC_VOICE_STYLE",
            r"supertonic\assets\voice_styles\M4.json"
        ))
        self.supertonic_py_dir = str(_ruta(
            "SUPERTONIC_PY_DIR",
            r"supertonic\py"
        ))

        # Verificar disponibilidad de Supertonic
        self._supertonic_disponible = Path(self.supertonic_python).exists()
        if not self._supertonic_disponible:
            print(f"⚠️ [VoiceDirector] Modo Offline no disponible — python no encontrado en:")
            print(f"   {self.supertonic_python}")
            print("   Verifica que supertonic/ esté dentro de MiuraForgeEngine/")
        else:
            perfil = Path(self.supertonic_voice_style).stem
            etiqueta = "MiuraSteel 🔥" if "MiuraSteel" in perfil or "AndresDisAcero" in perfil else f"Supertonic/{perfil}"
            print(f"🔩 [VoiceDirector] Fallback offline activo → {etiqueta}")

        print("🎙️ [Andrés] Sistema de voz inicializado. Frecuencia: 44.1kHz | Target: -14dBFS")

    # -----------------------------------------------------------------------
    # API PÚBLICA
    # -----------------------------------------------------------------------

    def _purificar_texto(self, texto: str) -> str:
        """Limpia el guion de etiquetas y aplica 'Puntuación de Acero' para evitar tartamudeos."""
        import re
        # 1. Eliminar etiquetas de fase (ej: "FASE 1 - EL GOLPE:")
        texto = re.sub(r'(?i)fase\s?\d+.*?[:\- ]+', '', texto)
        # 2. Eliminar nombres de personajes con ":" (ej: "ANDRÉS:", "PERSONAJE:")
        texto = re.sub(r'^[A-ZÁÉÍÓÚÑ]+\s?[A-ZÁÉÍÓÚÑ]*\s?:', '', texto, flags=re.M)
        # 3. Eliminar anotaciones entre paréntesis o corchetes (ej: "(susurrando)")
        texto = re.sub(r'[\(\[].*?[\)\]]', '', texto)
        # 4. Eliminar asteriscos de markdown
        texto = texto.replace('*', '')

        # --- NORMALIZACIÓN RÍTMICA (Evitar tartamudeo en Supertonic) ---
        # A. Sustituir comas por puntos suspensivos para dar respiros reales
        texto = texto.replace(',', '...')
        
        # B. Asegurar que las frases largas tengan cortes técnicos cada ~10 palabras
        # Dividimos por espacios y reconstruimos con micro-pausas si el bloque es largo
        palabras = texto.split()
        bloques = []
        for i in range(0, len(palabras), 12):
            bloques.append(" ".join(palabras[i:i+12]))
        texto = "... ".join(bloques)

        # C. Normalizar excesos de puntos suspensivos y espacios
        texto = re.sub(r'\.{3,}', '...', texto)
        texto = re.sub(r'\s+', ' ', texto).strip()
        
        # D. Forzar punto final si no tiene
        if texto and texto[-1] not in ['.', '!', '?']:
            texto += "."

        return texto

    def generar_voz(self, texto: str, nombre_archivo: str) -> bool:
        """
        Punto de entrada maestro. Purifica, sintetiza y aplica el Post-Proceso de Acero.
        Intenta ElevenLabs primero. Si falla, activa Supertonic/MiuraSteel offline.
        """
        texto_limpio = self._purificar_texto(texto)
        print(f"🎙️ [Andrés] Preparando locución: {texto_limpio[:60]}...")

        archivo_final = nombre_archivo if nombre_archivo.endswith('.wav') \
                        else nombre_archivo.replace('.mp3', '.wav')

        # Intento 1: ElevenLabs (producción principal)
        if self.api_key and self.voice_id:
            exito = self._generar_elevenlabs(texto_limpio, archivo_final)
            if exito:
                return True
            print("⚠️ [Andrés] ElevenLabs ha fallado. Activando generador de respaldo (Offline)...")

        # Intento 2: Supertonic / MiuraSteel (fallback offline ilimitado)
        if self._supertonic_disponible:
            return self._generar_supertonic(texto_limpio, archivo_final)

        print("❌ [Andrés] El búnker se ha quedado sin voz. Revisa la conexión o el saldo de ElevenLabs.")
        return False

    # -----------------------------------------------------------------------
    # PROVEEDOR 1: ElevenLabs
    # -----------------------------------------------------------------------

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def _generar_elevenlabs(self, texto: str, nombre_archivo: str) -> bool:
        """Sintetiza via ElevenLabs en formato RAW PCM y aplica el Post-Proceso."""
        api_url = f"{self.url}?output_format=pcm_44100"

        headers = {
            "Accept": "*/*",
            "Content-Type": "application/json",
            "xi-api-key": self.api_key
        }
        data = {
            "text": texto,
            "model_id": "eleven_multilingual_v2",
            "voice_settings": {
                "stability": 0.55,
                "similarity_boost": 0.8,
                "style": 0.05,
                "use_speaker_boost": True
            }
        }
        try:
            response = requests.post(api_url, json=data, headers=headers)
            if response.status_code == 200:
                pcm_bytes = response.content

                # Validar PCM antes de escribir
                if len(pcm_bytes) < 1000 or len(pcm_bytes) % 2 != 0:
                    print(f"⚠️ [ElevenLabs] PCM inválido ({len(pcm_bytes)} bytes). Reintentando...")
                    raise ValueError("PCM inválido")

                temp_wav = nombre_archivo.replace('.wav', '_tmp.wav')
                with wave.open(temp_wav, 'wb') as wf:
                    wf.setnchannels(1)
                    wf.setsampwidth(2)
                    wf.setframerate(44100)
                    wf.writeframes(pcm_bytes)

                ok = _post_procesar_wav(temp_wav, nombre_archivo, corte_agudos_db=2.0)
                if os.path.exists(temp_wav):
                    os.unlink(temp_wav)

                if ok:
                    print(f"✅ [Andrés/ElevenLabs] Voz forjada con calidad de ACERO: {nombre_archivo}")
                    return True
                return False
            else:
                print(f"⚠️ [ElevenLabs] Error {response.status_code}: {response.text}")
                response.raise_for_status()
        except Exception as e:
            print(f"❌ [ElevenLabs] Error crítico: {e}")
            raise e

    # -----------------------------------------------------------------------
    # PROVEEDOR 2: Supertonic / MiuraSteel (subprocess Python 3.11)
    # -----------------------------------------------------------------------

    def _generar_supertonic(self, texto: str, nombre_archivo: str) -> bool:
        """
        Llama a Supertonic/MiuraSteel via subprocess en Python 3.11.
        Aplica post-procesamiento EQ + normalización al WAV resultante.

        Para activar MiuraSteel en lugar de M4 base, solo cambiar en .env:
            SUPERTONIC_VOICE_STYLE=supertonic\\assets\\voice_styles\\MiuraSteel.json
        """
        try:
            runner_code = _SUPERTONIC_RUNNER.replace(
                "{py_dir}", self.supertonic_py_dir.replace("\\", "\\\\")
            )
            with tempfile.NamedTemporaryFile(
                mode='w', suffix='.py', delete=False, encoding='utf-8'
            ) as tmp:
                tmp.write(runner_code)
                runner_path = tmp.name

            raw_wav = nombre_archivo.replace('.wav', '_raw.wav')

            cmd = [
                self.supertonic_python,
                runner_path,
                "--onnx-dir",    self.supertonic_onnx_dir,
                "--voice-style", self.supertonic_voice_style,
                "--text",        texto,
                "--lang",        "es",
                "--output",      raw_wav
            ]

            perfil = Path(self.supertonic_voice_style).stem
            print(f"🔩 [MiuraSteel/{perfil}] Generando audio offline...")

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
            os.unlink(runner_path)

            if result.returncode != 0 or not os.path.exists(raw_wav):
                print(f"❌ [MiuraSteel] Error en subprocess:\n{result.stderr}")
                return False

            # --- POST-PROCESAMIENTO ---
            # Si Pedalboard está disponible y es MiuraSteel, usamos la forja profesional
            if PEDALBOARD_DISPONIBLE and ("MiuraSteel" in self.supertonic_voice_style or "AndresDisAcero" in self.supertonic_voice_style):
                print("⚒️  [Andrés] Aplicando Forja de Voz Profesional (Pedalboard)...")

                # Preferir V2 (con formant shifting, tilt EQ, micro-chorus)
                # Si falla, caer a V1 (original)
                if hasattr(_forjar_voz_acero_v2, '__call__'):
                    ok = _forjar_voz_acero_v2(raw_wav, nombre_archivo)
                    if not ok:
                        print("⚠️  [Andrés] V2 falló, intentando V1...")
                        ok = _forjar_voz_acero(raw_wav, nombre_archivo)
                else:
                    ok = _forjar_voz_acero(raw_wav, nombre_archivo)
            else:
                ok = _post_procesar_wav(raw_wav, nombre_archivo, corte_agudos_db=1.0)
                
            os.unlink(raw_wav)

            if ok:
                print(f"✅ [Andrés/MiuraSteel] Archivo forjado en acero: {nombre_archivo}")
                return True
            return False

        except subprocess.TimeoutExpired:
            print("❌ [MiuraSteel] Timeout — el proceso tardó más de 120s")
            return False
        except Exception as e:
            print(f"❌ [MiuraSteel] Fallo inesperado: {e}")
            return False
