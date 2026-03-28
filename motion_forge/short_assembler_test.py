"""
short_assembler.py — MiuraForgeEngine
======================================
Ensamblador premium de videos cortos (Shorts/TikTok/Reels).
Toma clips generados por Meta AI (Motion Forge), los sincroniza con voz,
añade subtítulos automáticos (Whisper), ganchos visuales y CTAs.

Mejoras:
- Faster-Whisper para transcripción ultra-rápida.
- Estilos 'Imperio de Acero' (Dorado/Amarillo/Bordes).
- Hook (0-3s) y CTA (Final) configurables.
- Centrado milimétrico y tipografía de impacto.
"""

import os
import re
import wave
import shutil
import subprocess
import argparse
from pathlib import Path
from typing import List, Dict, Optional, Tuple, Union

# --- CONFIGURACIÓN DE FFMPEG ---
def configurar_ffmpeg():
    """Busca FFmpeg en el sistema e inyecta la ruta al PATH de Windows."""
    # Intentar añadir C:\ffmpeg\bin de inmediato como prioridad absoluta
    rutas_comunes = [r"C:\ffmpeg\bin", r"C:\Program Files\ffmpeg\bin"]
    for p in rutas_comunes:
        if os.path.exists(p):
            if p not in os.environ["PATH"]:
                os.environ["PATH"] = p + os.pathsep + os.environ["PATH"]
                print(f"   🔧 Añadiendo FFmpeg al PATH: {p}")
            break

    try:
        # Verificar si ffmpeg responde
        subprocess.run(["ffmpeg", "-version"], capture_output=True, check=True)
        return True
    except (FileNotFoundError, subprocess.CalledProcessError):
        print("⚠️ FFmpeg no detectado plenamente por el sistema.")
        return False

# --- CONFIGURACIÓN DE EFECTOS ---
FPS             = 30
ZOOM_INICIO     = 1.0
ZOOM_FIN        = 1.08
FADE_DURACION   = 0.4
OUTPUT_SIZE     = (752, 1392)

# Subtítulos Estilo 'Imperio de Acero'
SUB_FONT_NAME   = "Montserrat"   # Opciones: Anton, Oswald, Montserrat...
SUB_FONT_HOOK   = "Cinzel"       # Opciones: Bebas Neue, Cinzel...
SUB_FONTSIZE    = 60
SUB_COLOR       = "white"
SUB_STROKE      = "black"
SUB_STROKE_W    = 3
SUB_POSICION    = (OUTPUT_SIZE[0] // 2, int(OUTPUT_SIZE[1] * 0.78))

ESTILO_HOOK = {"color": "#FFFF00", "size": 75, "pos": 0.25, "font": SUB_FONT_HOOK}
ESTILO_CTA  = {"color": "#FFD700", "size": 75, "pos": 0.50, "font": SUB_FONT_HOOK}

WHISPER_MODEL_SIZE = "small"
_WHISPER_MODEL = None

# --- WHISPER (FASTER-WHISPER) ---
def transcribir_audio(audio_path: Union[str, Path]):
    global _WHISPER_MODEL
    try:
        from faster_whisper import WhisperModel
        audio_str = str(audio_path)
        print(f"   🎙️  Transcribiendo con Faster-Whisper (modelo: {WHISPER_MODEL_SIZE})...")
        if _WHISPER_MODEL is None:
            _WHISPER_MODEL = WhisperModel(WHISPER_MODEL_SIZE, device="cpu", compute_type="int8")
        segments, info = _WHISPER_MODEL.transcribe(audio_str, word_timestamps=True, language="es")
        word_list = []
        for segment in segments:
            for word in segment.words:
                word_list.append({"text": word.word, "timestamp": (word.start, word.end)})
        return word_list
    except Exception as e:
        print(f"   ⚠️ Error en Faster-Whisper: {e}. Usando fallback global.")
        return None

def extraer_texto_guion(id_sesion: str) -> str:
    """Intenta extraer el texto del guion desde las fichas metadata."""
    folder = Path("forja_local") / id_sesion
    if not folder.exists(): return ""
    txts = sorted(folder.glob("clip_*_ANIMACION.txt"))
    full_text = []
    for t in txts:
        try:
            content = t.read_text(encoding="utf-8")
            match = re.search(r"GUION:\s*(.*?)(?:\n\n|\Z)", content, re.DOTALL)
            if match:
                txt = match.group(1).replace('"', '').strip()
                if txt: full_text.append(txt)
        except: continue
    return " ".join(full_text)

# --- MOTOR DE ENSAMBLE ---
def ensamblar_short(id_sesion: str, clips_mp4: list[str], wav_path: Path, output_file: Path, hook: str = "", cta: str = "", calidad_str: str = "MIDDLE", outro_path: str = r"D:\YT\MiuraForge\forja_local\Final.mp4"):
    # IMPORTANTE: Importar después de configurar_ffmpeg
    import cv2
    from movielite import VideoWriter, VideoClip, AudioClip, TextClip, ImageClip, VideoQuality, vfx
    from pictex import Canvas, Shadow, Text, CropMode

    print(f"   Cargando clips ({len(clips_mp4)})...")
    video_clips = [VideoClip(str(c)) for c in clips_mp4]
    
    # Audio de voz
    audio_voz = AudioClip(str(wav_path))
    duracion_total = audio_voz.duration

    writer = VideoWriter(str(output_file), fps=FPS, size=OUTPUT_SIZE)
    
    print("   ✂️  Dinamizando línea de tiempo (Circular Chain Engine)...")
    clips_procesados = []
    
    t_actual = 0.0
    idx_clip = 0
    
    while t_actual < duracion_total:
        ruta_mp4 = clips_mp4[idx_clip % len(clips_mp4)]
        clip = VideoClip(ruta_mp4)
        
        # Pan & Scan: Escalar proporcionalmente para llenar la pantalla y centrar
        c_w, c_h = clip.size
        escala = max(OUTPUT_SIZE[0] / c_w, OUTPUT_SIZE[1] / c_h)
        n_w = int(c_w * escala)
        n_h = int(c_h * escala)
        clip.set_size(width=n_w, height=n_h)
        px = (OUTPUT_SIZE[0] - n_w) // 2
        py = (OUTPUT_SIZE[1] - n_h) // 2
        clip.set_position((px, py))
        
        duracion_disponible = clip.duration
        tiempo_restante = duracion_total - t_actual
        
        if tiempo_restante < duracion_disponible:
            # Es el último fragmento, lo cortamos para empalmar justo con el final de voz
            clip.set_duration(tiempo_restante)
            duracion_visual = tiempo_restante
        else:
            # Superposición: Extendemos la duración para el freeze transparente del Crossfade
            duracion_visual = duracion_disponible
            clip.set_duration(duracion_disponible + FADE_DURACION)
            
        clip.set_start(t_actual)
        
        if t_actual > 0:
            clip.add_effect(vfx.FadeIn(duration=FADE_DURACION))
            
        clip.add_effect(vfx.ZoomIn(duration=clip.duration, from_scale=ZOOM_INICIO, to_scale=ZOOM_FIN))
        
        clips_procesados.append(clip)
        
        # Avanzar el puntero en el tiempo (el siguiente clip empezará encima del FadeOut natural de este)
        t_actual += duracion_visual
        idx_clip += 1

    # --- SUBTÍTULOS ---
    subs_clips = []
    transcripcion = transcribir_audio(wav_path)
    
    if not transcripcion:
        guion = extraer_texto_guion(id_sesion)
        palabras = guion.split()
        if palabras:
            ms_pal = (duracion_total * 1000) / len(palabras)
            transcripcion = [{"text": p, "timestamp": (i*ms_pal/1000, (i+1)*ms_pal/1000)} for i, p in enumerate(palabras)]

    if transcripcion:
        print(f"   🎨 Generando subtítulos Word-by-Word (Hormozi style)...")
        # Forzar tiempos contiguos estrictos para evitar overlap fantasmal
        for idx in range(len(transcripcion)):
            w = transcripcion[idx]
            t_s = w["timestamp"][0]
            t_e = transcripcion[idx+1]["timestamp"][0] if idx < len(transcripcion) - 1 else (w["timestamp"][1] or t_s + 0.5)
            transcripcion[idx]["ts"] = (t_s, t_e)
            transcripcion[idx]["clean_text"] = re.sub(r"^[\s,.\-\[\]]+", "", w["text"].strip()).upper()

        tam_bloque = 3
        for i in range(0, len(transcripcion), tam_bloque):
            grupo = transcripcion[i : i + tam_bloque]
            grupo_limpio = [w for w in grupo if w["clean_text"]]
            if not grupo_limpio: continue

            # Generar el bloque palabra por palabra (Efecto Hormozi)
            for j, word_obj in enumerate(grupo_limpio):
                t_start = word_obj["ts"][0]
                t_end = word_obj["ts"][1]

                elementos_texto = []
                for k, w in enumerate(grupo_limpio):
                    color = "#FFFF00" if k == j else SUB_COLOR  
                    texto = w["clean_text"] + " "
                    elementos_texto.append(Text(texto).color(color))
                    
                canvas = (Canvas().width(int(OUTPUT_SIZE[0]*0.88)).font_size(SUB_FONTSIZE).font_family(SUB_FONT_NAME).font_weight("bold")
                          .text_align("center").text_wrap("normal").background_color("transparent")
                          .text_shadows(Shadow(offset=(4,4), blur_radius=6, color="black")))
                
                img = canvas.render(*elementos_texto, crop_mode=CropMode.SMART)
                img_rgba = img.to_numpy(mode='RGBA')
                
                # Salvavidas: Escalar por OpenCV si la palabra es bestialmente ancha
                max_w = int(OUTPUT_SIZE[0] * 0.95)
                if img_rgba.shape[1] > max_w:
                    scale = max_w / img_rgba.shape[1]
                    img_rgba = cv2.resize(img_rgba, (int(img_rgba.shape[1] * scale), int(img_rgba.shape[0] * scale)), interpolation=cv2.INTER_AREA)

                # Convertir a ImageClip de la duración exacta de esa palabra
                dur_palabra = max(0.05, t_end - t_start)
                g_clip = ImageClip(img_rgba, start=t_start, duration=dur_palabra)
                
                px = (OUTPUT_SIZE[0] - g_clip.size[0]) // 2
                py = int(OUTPUT_SIZE[1] * 0.78) - (g_clip.size[1] // 2)
                g_clip.set_position((px, py))
                subs_clips.append(g_clip)

    # --- OUTRO EXTERNO (Final.mp4) ---
    if outro_path and os.path.exists(outro_path):
        print(f"   🎬 Reemplazando final con Outro externo: {Path(outro_path).name}")
        outro_clip = VideoClip(outro_path)
        c_w, c_h = outro_clip.size
        # Escalar para que cubra la pantalla sin deformar
        escala = max(OUTPUT_SIZE[0] / c_w, OUTPUT_SIZE[1] / c_h)
        n_w = int(c_w * escala)
        n_h = int(c_h * escala)
        outro_clip.set_size(width=n_w, height=n_h)
        px = (OUTPUT_SIZE[0] - n_w) // 2
        py = (OUTPUT_SIZE[1] - n_h) // 2
        outro_clip.set_position((px, py))
        
        # Iniciar N segundos antes de que termine el audio principal, para que el audio termine al tiempo del video
        start_time = max(0, duracion_total - outro_clip.duration)
        outro_clip.set_start(start_time)
        clips_procesados.append(outro_clip)

    # --- HOOK ---
    if hook:
        print(f"   ⚓ Hook: {hook}")
        h_canvas = (Canvas().width(int(OUTPUT_SIZE[0]*0.9)).font_size(ESTILO_HOOK["size"]).font_family(ESTILO_HOOK["font"]).font_weight("bold")
                    .color(ESTILO_HOOK["color"]).text_align("center").text_wrap("normal").background_color("transparent")
                    .text_shadows(Shadow(offset=(5,5), blur_radius=8, color="black")))
        h_clip = TextClip(hook.upper(), start=0, duration=3.0, canvas=h_canvas)
        px = (OUTPUT_SIZE[0] - h_clip.size[0]) // 2
        py = int(OUTPUT_SIZE[1] * ESTILO_HOOK["pos"]) - (h_clip.size[1] // 2)
        h_clip.set_position((px, py))
        subs_clips.append(h_clip)

    # --- SUSCRIBETE INTERMEDIO ---
    print(f"   🔔 Marca de agua: SUSCRÍBETE")
    s_canvas = (Canvas().width(int(OUTPUT_SIZE[0]*0.9)).font_size(ESTILO_CTA["size"]).font_family("Anton").font_weight("bold")
                .color("#FF0000").text_align("center").text_wrap("normal").background_color("transparent")
                .text_shadows(Shadow(offset=(5,5), blur_radius=10, color="black")))
    s_duracion = duracion_total * 0.4
    s_inicio = duracion_total * 0.3
    s_clip = TextClip("SUSCRÍBETE", start=s_inicio, duration=s_duracion, canvas=s_canvas)
    
    import math
    s_px = (OUTPUT_SIZE[0] - s_clip.size[0]) // 2
    s_base_y = int(OUTPUT_SIZE[1] * 0.15)  # Centro superior
    
    def rebote_y(t):
        # Rebote: resta un valor absoluto senoidal a la posición base Y (sube y vuelve a bajar)
        dy = abs(math.sin(t * 5)) * 20
        return (s_px, s_base_y - dy)
        
    s_clip.set_position(rebote_y)
    s_clip.add_effect(vfx.FadeIn(duration=0.5))
    s_clip.add_effect(vfx.FadeOut(duration=0.5))
    subs_clips.append(s_clip)

    # --- CTA ---
    if cta and not (outro_path and os.path.exists(outro_path)):
        print(f"   🔔 CTA: {cta}")
        c_canvas = (Canvas().width(int(OUTPUT_SIZE[0]*0.9)).font_size(ESTILO_CTA["size"]).font_family(ESTILO_CTA["font"]).font_weight("bold")
                    .color(ESTILO_CTA["color"]).text_align("center").text_wrap("normal").background_color("transparent")
                    .text_shadows(Shadow(offset=(5,5), blur_radius=10, color="black")))
        c_clip = TextClip(cta.upper(), start=max(0, duracion_total - 4.5), duration=4.5, canvas=c_canvas)
        px = (OUTPUT_SIZE[0] - c_clip.size[0]) // 2
        py = int(OUTPUT_SIZE[1] * ESTILO_CTA["pos"]) - (c_clip.size[1] // 2)
        c_clip.set_position((px, py))
        subs_clips.append(c_clip)

    # --- RENDER ---
    print(f"   ⚙️ Renderizando ({calidad_str})...")
    q_map = {"LOW": VideoQuality.LOW, "MIDDLE": VideoQuality.MIDDLE, "HIGH": VideoQuality.HIGH, "VERY_HIGH": VideoQuality.VERY_HIGH}
    calidad = q_map.get(calidad_str.upper(), VideoQuality.HIGH)
    
    writer = VideoWriter(str(output_file), fps=FPS, size=OUTPUT_SIZE)
    for c in clips_procesados: writer.add_clip(c)
    writer.add_clip(audio_voz)
    for s in subs_clips: writer.add_clip(s)
    
    writer.write(video_quality=calidad)
    print(f"   ✅ ¡Éxito! Video en: {output_file}")


def modo_masivo(target_id: str = None):
    """
    Busca IDs listos en forja_local y los ensambla.
    Si target_id se especifica, solo procesa ese ID.
    Extrae dinámicamente el Gancho y CTA de la base de datos.
    """
    configurar_ffmpeg()
    
    base_dir = Path("forja_local")
    if not base_dir.exists(): return
    
    carpetas = [base_dir / target_id] if target_id else base_dir.iterdir()
    
    db = None
    try:
        import sys
        sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
        from core.database import Database
        db = Database(spreadsheet_name="BD_MiuraForge_Engine")
    except Exception as e:
        print(f"⚠️ [Assembler] No se pudo conectar a DB para extraer Hook/CTA: {e}")
        
    for folder in carpetas:
        if not folder.is_dir(): continue
        fid = folder.name
        
        clips = sorted([str(f) for f in folder.glob("*.mp4") if "final" not in f.name])
        if not clips: continue
        
        wav = folder / f"{fid}.wav"
        if not wav.exists():
            wav = Path("output/imagenes_shorts") / fid / f"{fid}.wav"
            
        if not wav.exists():
            print(f"⚠️ [Assembler] Audio no encontrado para {fid}. Saltando.")
            continue
            
        hook_txt = ""
        cta_txt = "SUSCRÍBETE Y COMENTA"
        titulo_archivo = f"{fid}_final"
        
        if db:
            datos_yt = db.obtener_datos_despliegue(fid)
            if datos_yt:
                hook_txt = datos_yt.get("TITULO_GOLPE") or datos_yt.get("TITULO", "")
                tit_bruto = hook_txt if hook_txt else datos_yt.get("TITULO", fid)
                if tit_bruto:
                    import re, unicodedata
                    titulo_archivo = unicodedata.normalize('NFKD', str(tit_bruto)).encode('ascii', 'ignore').decode('ascii')
                    titulo_archivo = re.sub(r'[^a-zA-Z0-9\s-]', '', titulo_archivo).strip()
                    
        # Carpeta: output/shorts_finales/ID_SESSION | Archivo: TITULO.mp4
        output_folder = Path("output/shorts_finales") / fid
        output_folder.mkdir(parents=True, exist_ok=True)
        if not titulo_archivo: titulo_archivo = f"{fid}_final"
        output = output_folder / f"{titulo_archivo}.mp4"
        
        if output.exists():
            print(f"⏩ [Assembler] Video ya ensamblado: {output.name}")
            continue
                
        print(f"\n🎬 Iniciando Ensamble Automático para: {fid}")
        ensamblar_short(fid, clips, wav, output, hook=hook_txt, cta=cta_txt)
        print("-" * 50)


# --- MAIN ---
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Miura Forge Assembler")
    parser.add_argument("--id", type=str, required=False, help="ID específico. Si se omite, corre en Modo Masivo.")
    parser.add_argument("--calidad", type=str, default="MIDDLE")
    parser.add_argument("--hook", type=str, default="")
    parser.add_argument("--cta", type=str, default="")
    args = parser.parse_args()

    if not args.id:
        print("🚀 [Assembler] Ningún ID provisto. Iniciando MODO MASIVO...")
        modo_masivo()
        import sys
        sys.exit(0)
        
    configurar_ffmpeg()
    
    folder_clips = Path("forja_local") / args.id
    folder_audio = Path("output/imagenes_shorts") / args.id
    
    # Buscar clips en forja_local
    clips = sorted([str(f) for f in folder_clips.glob("*.mp4") if "final" not in f.name])
    
    # Buscar el WAV en ambas carpetas
    wav = folder_clips / f"{args.id}.wav"
    if not wav.exists():
        wav = folder_audio / f"{args.id}.wav"
    
    hook_txt = args.hook
    cta_txt = args.cta
    titulo_archivo = f"{args.id}_final"
    
    try:
        import sys
        sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
        from core.database import Database
        db = Database(spreadsheet_name="BD_MiuraForge_Engine")
        datos_yt = db.obtener_datos_despliegue(args.id)
        if datos_yt:
            titulo_db = datos_yt.get("TITULO", "")
            if not hook_txt:
                hook_txt = datos_yt.get("TITULO_GOLPE") or titulo_db
            tit_bruto = hook_txt if hook_txt else titulo_db
            if tit_bruto:
                import re, unicodedata
                titulo_archivo = unicodedata.normalize('NFKD', str(tit_bruto)).encode('ascii', 'ignore').decode('ascii')
                titulo_archivo = re.sub(r'[^a-zA-Z0-9\s-]', '', titulo_archivo).strip()
    except Exception as e:
        print(f"⚠️ [Assembler] No se pudo conectar a BD: {e}")

    # Carpeta: output/shorts_finales/ID_SESSION | Archivo: TITULO.mp4
    output_folder = Path("output/shorts_finales") / args.id
    output_folder.mkdir(parents=True, exist_ok=True)
    if not titulo_archivo: titulo_archivo = f"{args.id}_final"
    output = output_folder / f"{titulo_archivo}.mp4"

    if not clips or not wav.exists():
        print(f"❌ Error: Faltan recursos en {folder_clips} o {folder_audio}")
        if not clips: print("   - No se encontraron clips .mp4")
        if not wav.exists(): print(f"   - No se encontró el audio: {args.id}.wav")
    else:
        ensamblar_short(args.id, clips, wav, output, hook=hook_txt, cta=cta_txt, calidad_str=args.calidad)
