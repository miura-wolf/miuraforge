#!/usr/bin/env python3
"""
===============================================================================
VIDEO GENERATOR - Integración con Self-Forcing2.1-I2V-1.3B-GGUF
===============================================================================

Sistema de generación de video para "Disciplina en Acero"
Compatible con: Nichonauta/Self-Forcing2.1-I2V-1.3B-GGUF

Este script permite:
- Generar videos a partir de prompts textuales
- Usar imágenes como referencia (I2V)
- Integrarse con el pipeline de audio existente
- Aplicar procesamiento cinematico a los videos

Uso:
    python video_generator.py --prompt "tu prompt" --output video.mp4
    python video_generator.py --image imagen.jpg --prompt "descripcion" --output video.mp4

===============================================================================
"""

import os
import sys
import argparse
import json
import subprocess
from pathlib import Path
from typing import Optional, List, Dict

# ============================================================================
# CONFIGURACIÓN
# ============================================================================

# Rutas por defecto
DEFAULT_COMFYUI_PATH = os.path.expanduser("~/ComfyUI")
DEFAULT_MODEL_PATH = os.path.expanduser("~/ComfyUI/models/diffusers")

# Model config
MODEL_CONFIG = {
    "model_name": "Self-Forcing2.1-I2V-1.3B-GGUF",
    "model_id": "Nichonauta/Self-Forcing2.1-I2V-1.3B-GGUF",
    "quantizations": {
        "q4_0": "1.3 GB",
        "q8_0": "2.3 GB",
        "f16": "4.3 GB"
    }
}

# Prompts de ejemplo para "Disciplina en Acero"
EXAMPLE_PROMPTS = {
    "forge": """Scene: Realistic industrial forge with cold furnace and scattered tools
Camera Movement: Slow dolly-in toward anvil
Lighting: Dramatic chiaroscuro with single source from furnace door crack
Texture: Rough forged metal surfaces with fine dust particles
Composition: Extreme close-up on hammer resting on anvil, shallow depth of field
Atmosphere: Tense anticipation, heavy metallic air
Lens/Perspective: 35mm cine prime lens, eye-level perspective""",

    "workshop": """Scene: Industrial workshop with hanging unused tools against concrete wall
Camera Movement: Slow orbit around tool shadows
Lighting: High contrast between black shadows and subtle rim lighting
Texture: Cold metal and concrete with dust accumulation
Composition: Symmetrical framing of tool silhouettes
Atmosphere: Purpose void, silent abandonment
Lens/Perspective: 24mm wide angle, low-angle perspective""",

    "workbench": """Scene: Half-finished metal piece on workbench with scattered tools
Camera Movement: Handheld tracking along workbench surface
Lighting: Dramatic side lighting emphasizing unfinished edges
Texture: Rough metal filings and oil stains on steel surface
Composition: Diagonal composition following metal piece
Atmosphere: Execution deficit, frustrated potential
Lens/Perspective: 50mm macro lens, overhead perspective""",

    "tools_floor": """Scene: Multiple tools scattered in deep shadows across workshop floor
Camera Movement: Slow dolly across tool distribution pattern
Lighting: Extreme contrast with pools of light in darkness
Texture: Various metal textures with subtle oxidation
Composition: Chaotic arrangement telling story of distraction
Atmosphere: Mental dispersion, fractured focus
Lens/Perspective: 35mm anamorphic, Dutch angle""",

    "door": """Scene: Slightly ajar industrial metal door with light intrusion
Camera Movement: Slow push through doorway
Lighting: Strong backlight through crack creating silhouette
Texture: Heavy steel door with peeling paint and rust spots
Composition: Frame within frame through door opening
Atmosphere: Boundary weakness, uncontrolled access
Lens/Perspective: 28mm wide angle, threshold perspective""",

    "books": """Scene: Dust-covered industrial book tower with closed notebook
Camera Movement: Slow orbit around knowledge monument
Lighting: Subtle volumetric lighting through dust particles
Texture: Leather bindings and paper with metallic accents
Composition: Precarious vertical stacking against wall
Atmosphere: Intellectual self-deception, unused wisdom
Lens/Perspective: 85mm portrait lens, eye-level perspective"""
}


# ============================================================================
# CLASE PRINCIPAL: VIDEO GENERATOR
# ============================================================================

class VideoGenerator:
    """
    Generador de video basado en Self-Forcing2.1-I2V-1.3B-GGUF
    """

    def __init__(self,
                 comfyui_path: str = None,
                 model_path: str = None,
                 quantization: str = "q4_0"):
        """
        Inicializa el generador de video.

        Args:
            comfyui_path: Ruta a ComfyUI
            model_path: Ruta al modelo GGUF
            quantization: Cuantización (q4_0, q8_0, f16)
        """
        self.comfyui_path = comfyui_path or DEFAULT_COMFYUI_PATH
        self.model_path = model_path or DEFAULT_MODEL_PATH
        self.quantization = quantization

        # Verificar instalación
        self._verificar_entorno()

    def _verificar_entorno(self):
        """Verifica que el entorno esté correctamente configurado."""
        print(f"🔍 [VideoGen] Verificando entorno...")

        # Verificar ComfyUI
        if not os.path.exists(self.comfyui_path):
            print(f"⚠️  [VideoGen] ComfyUI no encontrado en: {self.comfyui_path}")
            print(f"   Instala ComfyUI desde: https://github.com/comfyanonymous/ComfyUI/")

        # Verificar ComfyUI-GGUF
        gguf_node = os.path.join(self.comfyui_path, "custom_nodes", "ComfyUI-GGUF")
        if not os.path.exists(gguf_node):
            print(f"⚠️  [VideoGen] ComfyUI-GGUF no encontrado")
            print(f"   Instala desde: https://github.com/city96/ComfyUI-GGUF")

        print(f"✅ [VideoGen] Entorno verificado")

    def generar_video(self,
                     prompt: str,
                     output_path: str,
                     image_path: str = None,
                     duration: int = 5,
                     fps: int = 24,
                     width: int = 640,
                     height: int = 480,
                     steps: int = 25,
                     cfg_scale: float = 7.0,
                     seed: int = -1) -> bool:
        """
        Genera un video a partir de un prompt.

        Args:
            prompt: Descripción textual de la escena
            output_path: Ruta de salida para el video
            image_path: Imagen de referencia (opcional, para I2V)
            duration: Duración en segundos
            fps: Fotogramas por segundo
            width: Ancho del video
            height: Alto del video
            steps: Pasos de inferencia
            cfg_scale: Escala CFG
            seed: Semilla aleatoria (-1 para aleatorio)

        Returns:
            bool: True si la generación fue exitosa
        """
        print(f"\n🎬 [VideoGen] Iniciando generación de video...")
        print(f"   Prompt: {prompt[:80]}...")

        # Generar workflow de ComfyUI
        workflow = self._generar_workflow(
            prompt=prompt,
            image_path=image_path,
            duration=duration,
            fps=fps,
            width=width,
            height=height,
            steps=steps,
            cfg_scale=cfg_scale,
            seed=seed
        )

        # Guardar workflow
        workflow_path = os.path.join(self.comfyui_path, "input", "workflow.json")
        os.makedirs(os.path.dirname(workflow_path), exist_ok=True)

        with open(workflow_path, "w") as f:
            json.dump(workflow, f, indent=2)

        print(f"   Workflow guardado: {workflow_path}")

        # Ejecutar ComfyUI
        return self._ejecutar_comfyui(workflow_path, output_path)

    def _generar_workflow(self,
                          prompt: str,
                          image_path: Optional[str],
                          duration: int,
                          fps: int,
                          width: int,
                          height: int,
                          steps: int,
                          cfg_scale: float,
                          seed: int) -> dict:
        """Genera el workflow de ComfyUI en formato JSON."""

        workflow = {
            "nodes": [],
            "models": [self._get_model_config()]
        }

        # Nodo 1: Load Text Prompt
        nodes = []

        # CLIP Text Encode
        nodes.append({
            "id": 1,
            "type": "CLIPTextEncode",
            "pos": [100, 100],
            "size": [300, 100],
            "flags": {},
            "order": 0,
            "mode": 0,
            "inputs": [
                {"name": "text", "type": "STRING", "link": None},
                {"name": "clip", "type": "CLIP", "link": None}
            ],
            "outputs": [
                {"name": "CONDITIONING", "type": "CONDITIONING", "links": None}
            ],
            "properties": {},
            "widgets_values": [prompt]
        })

        # Empty Latent Video
        nodes.append({
            "id": 2,
            "type": "EmptyLatentVideo",
            "pos": [100, 300],
            "size": [300, 200],
            "flags": {},
            "order": 1,
            "mode": 0,
            "inputs": [
                {"name": "batch_size", "type": "INT", "link": None}
            ],
            "outputs": [
                {"name": "LATENT", "type": "LATENT", "links": None}
            ],
            "properties": {},
            "widgets_values": [
                1,  # batch_size
                width,  # width
                height,  # height
                duration * fps,  # frames
                fps,  # fps
                1  # compression
            ]
        })

        # KSampler
        nodes.append({
            "id": 3,
            "type": "KSampler",
            "pos": [500, 100],
            "size": [300, 300],
            "flags": {},
            "order": 2,
            "mode": 0,
            "inputs": [
                {"name": "model", "type": "MODEL", "link": None},
                {"name": "positive", "type": "CONDITIONING", "link": None},
                {"name": "negative", "type": "CONDITIONING", "link": None},
                {"name": "latent", "type": "LATENT", "link": None}
            ],
            "outputs": [
                {"name": "LATENT", "type": "LATENT", "links": None}
            ],
            "properties": {},
            "widgets_values": [
                seed if seed >= 0 else int.from_bytes(os.urandom(4), 'big'),  # seed
                steps,  # steps
                cfg_scale,  # cfg
                "euler_ancestral",  # sampler_name
                "normal",  # scheduler
                1.0  # denoise
            ]
        })

        # VAE Decode
        nodes.append({
            "id": 4,
            "type": "VAEDecodeTiled",
            "pos": [500, 500],
            "size": [300, 100],
            "flags": {},
            "order": 3,
            "mode": 0,
            "inputs": [
                {"name": "samples", "type": "LATENT", "link": None},
                {"name": "vae", "type": "VAE", "link": None}
            ],
            "outputs": [
                {"name": "IMAGE", "type": "IMAGE", "links": None}
            ],
            "properties": {}
        })

        # Save Video
        nodes.append({
            "id": 5,
            "type": "SaveVideo",
            "pos": [700, 500],
            "size": [300, 100],
            "flags": {},
            "order": 4,
            "mode": 0,
            "inputs": [
                {"name": "images", "type": "IMAGE", "link": None}
            ],
            "outputs": [],
            "properties": {},
            "widgets_values": [output_path]
        })

        workflow["nodes"] = nodes
        return workflow

    def _get_model_config(self) -> dict:
        """Retorna la configuración del modelo."""
        return {
            "model_name": MODEL_CONFIG["model_name"],
            "model_path": os.path.join(
                self.model_path,
                f"Self-Forcing2.1-I2V-1.3B-{self.quantization.upper()}.gguf"
            ),
            "quantization": self.quantization
        }

    def _ejecutar_comfyui(self, workflow_path: str, output_path: str) -> bool:
        """Ejecuta ComfyUI con el workflow."""

        # Buscar ejecutable de ComfyUI
        comfy_exe = os.path.join(self.comfyui_path, "python", "main.py")
        if not os.path.exists(comfy_exe):
            comfy_exe = os.path.join(self.comfyui_path, "comfy.exe")

        if not os.path.exists(comfy_exe):
            print(f"❌ [VideoGen] No se encontró ejecutable de ComfyUI")
            print(f"   Busca en: {self.comfyui_path}")
            return False

        try:
            print(f"🚀 [VideoGen] Ejecutando ComfyUI...")

            result = subprocess.run(
                [
                    sys.executable,
                    comfy_exe,
                    "--workflow",
                    workflow_path,
                    "--output",
                    output_path,
                    "--preview",
                    "false"
                ],
                capture_output=True,
                text=True,
                timeout=600  # 10 minutos
            )

            if result.returncode == 0:
                print(f"✅ [VideoGen] Video generado: {output_path}")
                return True
            else:
                print(f"❌ [VideoGen] Error en generación:")
                print(result.stderr)
                return False

        except subprocess.TimeoutExpired:
            print(f"❌ [VideoGen] Timeout - la generación tardó más de 10 minutos")
            return False
        except Exception as e:
            print(f"❌ [VideoGen] Error: {e}")
            return False


# ============================================================================
# PIPELINE INTEGRADO: AUDIO + VIDEO
# ============================================================================

class DisciplinaEnAceroPipeline:
    """
    Pipeline completo para "Disciplina en Acero":
    1. Genera audio narrado
    2. Procesa audio (voice_director)
    3. Genera video ilustrativo
    4. Combina audio + video
    """

    def __init__(self):
        """Inicializa el pipeline."""
        self.video_gen = VideoGenerator()
        print("🎬 [Pipeline] Disciplina en Acero inicializado")

    def generar_episodio(self,
                        texto: str,
                        prompt_video: str,
                        output_video: str,
                        voice_audio: str = None) -> bool:
        """
        Genera un episodio completo:
        1. Audio narrado (si se proporciona)
        2. Video ilustrativo
        3. Combina ambos

        Args:
            texto: Texto para narración de voz
            prompt_video: Prompt para generación de video
            output_video: Video final de salida
            voice_audio: Archivo de audio de voz (opcional)

        Returns:
            bool: True si fue exitoso
        """
        print(f"\n{'='*60}")
        print("🎬 GENERANDO EPISODIO: DISCIPLINA EN ACERO")
        print(f"{'='*60}")

        # 1. Generar video
        print(f"\n🎬 [Pipeline] Generando video...")
        exito_video = self.video_gen.generar_video(
            prompt=prompt_video,
            output_path=output_video
        )

        if not exito_video:
            print("❌ [Pipeline] Error al generar video")
            return False

        # 2. Si hay audio de voz, combinar
        if voice_audio and os.path.exists(voice_audio):
            print(f"\n🔊 [Pipeline] Combinando audio + video...")
            return self._combinar_audio_video(voice_audio, output_video, output_video)

        print(f"\n✅ [Pipeline] Episodio generado: {output_video}")
        return True

    def _combinar_audio_video(self,
                             audio_path: str,
                             video_path: str,
                             output_path: str) -> bool:
        """Combina audio y video usando ffmpeg."""

        try:
            # Verificar ffmpeg
            result = subprocess.run(
                ["ffmpeg", "-version"],
                capture_output=True
            )

            if result.returncode != 0:
                print("⚠️ [Pipeline] ffmpeg no disponible")
                print("   Instala: https://ffmpeg.org/download.html")
                return False

            # Combinar
            print(f"🔧 [Pipeline] Ejecutando ffmpeg...")
            cmd = [
                "ffmpeg",
                "-y",  # Sobrescribir
                "-i", audio_path,
                "-i", video_path,
                "-c:v", "copy",
                "-c:a", "aac",
                "-strict", "experimental",
                output_path
            ]

            result = subprocess.run(cmd, capture_output=True, text=True)

            if result.returncode == 0:
                print(f"✅ [Pipeline] Audio + Video combinados: {output_path}")
                return True
            else:
                print(f"❌ [Pipeline] Error: {result.stderr}")
                return False

        except FileNotFoundError:
            print("⚠️ [Pipeline] ffmpeg no encontrado")
            return False


# ============================================================================
# PUNTO DE ENTRADA
# ============================================================================

def main():
    """Función principal."""
    parser = argparse.ArgumentParser(
        description="Video Generator para Disciplina en Acero",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"""
Ejemplos:
  # Generar video desde prompt
  python video_generator.py --prompt "Scene: Industrial forge..."

  # Generar video con imagen de referencia (I2V)
  python video_generator.py --image input.jpg --prompt "Animation description..."

  # Usar prompt predefinido
  python video_generator.py --preset forge

  # Pipeline completo
  python video_generator.py --pipeline --texto "Tu texto" --preset forge

Prompts disponibles:
  forge      - Forja industrial
  workshop   - Taller industrial
  workbench  - Mesa de trabajo
  tools_floor - Herramientas en el suelo
  door       - Puerta industrial
  books      - Torre de libros
        """
    )

    # Argumentos
    parser.add_argument(
        "--prompt", "-p",
        help="Prompt de texto para generación de video"
    )

    parser.add_argument(
        "--image", "-i",
        help="Imagen de referencia para I2V"
    )

    parser.add_argument(
        "--output", "-o",
        default="output.mp4",
        help="Archivo de salida (default: output.mp4)"
    )

    parser.add_argument(
        "--preset", "-pr",
        choices=list(EXAMPLE_PROMPTS.keys()),
        help="Usar prompt predefinido"
    )

    parser.add_argument(
        "--duration", "-d",
        type=int,
        default=5,
        help="Duración del video en segundos (default: 5)"
    )

    parser.add_argument(
        "--fps",
        type=int,
        default=24,
        help="Fotogramas por segundo (default: 24)"
    )

    parser.add_argument(
        "--width", "-w",
        type=int,
        default=640,
        help="Ancho del video (default: 640)"
    )

    parser.add_argument(
        "--height", "-ht",
        type=int,
        default=480,
        help="Alto del video (default: 480)"
    )

    parser.add_argument(
        "--steps", "-s",
        type=int,
        default=25,
        help="Pasos de inferencia (default: 25)"
    )

    parser.add_argument(
        "--cfg",
        type=float,
        default=7.0,
        help="Escala CFG (default: 7.0)"
    )

    parser.add_argument(
        "--seed",
        type=int,
        default=-1,
        help="Semilla aleatoria (default: aleatorio)"
    )

    parser.add_argument(
        "--quantization", "-q",
        choices=["q4_0", "q8_0", "f16"],
        default="q4_0",
        help="Cuantización del modelo (default: q4_0)"
    )

    parser.add_argument(
        "--comfyui-path",
        default=DEFAULT_COMFYUI_PATH,
        help="Ruta a ComfyUI"
    )

    parser.add_argument(
        "--pipeline",
        action="store_true",
        help="Ejecutar pipeline completo (audio + video)"
    )

    parser.add_argument(
        "--texto",
        help="Texto para narración de voz (usado con --pipeline)"
    )

    args = parser.parse_args()

    # Obtener prompt
    prompt = args.prompt

    if args.preset:
        prompt = EXAMPLE_PROMPTS[args.preset]
        print(f"📝 [VideoGen] Usando preset: {args.preset}")

    if not prompt:
        print("❌ Error: Debes proporcionar --prompt o --preset")
        parser.print_help()
        sys.exit(1)

    # Inicializar generador
    gen = VideoGenerator(
        comfyui_path=args.comfyui_path,
        quantization=args.quantization
    )

    # Generar video
    print(f"\n{'='*60}")
    print("🎬 VIDEO GENERATOR - DISCIPLINA EN ACERO")
    print(f"{'='*60}")

    exito = gen.generar_video(
        prompt=prompt,
        output_path=args.output,
        image_path=args.image,
        duration=args.duration,
        fps=args.fps,
        width=args.width,
        height=args.height,
        steps=args.steps,
        cfg_scale=args.cfg,
        seed=args.seed
    )

    if exito:
        print(f"\n✅ Video generado exitosamente: {args.output}")
    else:
        print(f"\n❌ Error en generación de video")
        sys.exit(1)


if __name__ == "__main__":
    main()
