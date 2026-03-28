#!/usr/bin/env python3
"""
===============================================================================
VIDEO GENERATOR T2V - Self-Forcing2.1-T2V-1.3B-GGUF
===============================================================================

Sistema de generación de video a partir de texto (Text-to-Video)
Compatible con: Nichonauta/Self-Forcing2.1-T2V-1.3B-GGUF

Este script permite:
- Generar videos a partir de prompts textuales
- Usar parámetros cinematográficos avanzados
- Integrarse con el pipeline de audio existente

Uso:
    python video_generator_T2V.py --prompt "tu prompt" --output video.mp4
    python video_generator_T2V.py --preset forge --output video.mp4

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

# Config del modelo T2V
MODEL_CONFIG = {
    "model_name": "Self-Forcing2.1-T2V-1.3B-GGUF",
    "model_id": "Nichonauta/Self-Forcing2.1-T2V-1.3B-GGUF",
    "quantizations": {
        "q4_0": "803 MB",
        "q8_0": "1.51 GB",
        "f16": "2.84 GB"
    }
}

# Prompts de ejemplo para "Disciplina en Acero" (T2V - texto a video)
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
# CLASE PRINCIPAL: VIDEO GENERATOR T2V
# ============================================================================

class VideoGeneratorT2V:
    """
    Generador de video basado en Self-Forcing2.1-T2V-1.3B-GGUF
    Text-to-Video: Genera video directamente desde texto
    """

    def __init__(self,
                 comfyui_path: str = None,
                 model_path: str = None,
                 quantization: str = "q4_0"):
        """
        Inicializa el generador de video T2V.

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
        print(f"🔍 [VideoGen T2V] Verificando entorno...")

        # Verificar ComfyUI
        if not os.path.exists(self.comfyui_path):
            print(f"⚠️  [VideoGen T2V] ComfyUI no encontrado en: {self.comfyui_path}")
            print(f"   Instala ComfyUI desde: https://github.com/comfyanonymous/ComfyUI/")

        # Verificar ComfyUI-GGUF
        gguf_node = os.path.join(self.comfyui_path, "custom_nodes", "ComfyUI-GGUF")
        if not os.path.exists(gguf_node):
            print(f"⚠️  [VideoGen T2V] ComfyUI-GGUF no encontrado")
            print(f"   Instala desde: https://github.com/city96/ComfyUI-GGUF")

        print(f"✅ [VideoGen T2V] Entorno verificado")

    def generar_video(self,
                     prompt: str,
                     output_path: str,
                     duration: int = 5,
                     fps: int = 24,
                     width: int = 640,
                     height: int = 480,
                     steps: int = 25,
                     cfg_scale: float = 7.0,
                     seed: int = -1,
                     negative_prompt: str = None) -> bool:
        """
        Genera un video a partir de un prompt de texto.

        Args:
            prompt: Descripción textual de la escena
            output_path: Ruta de salida para el video
            duration: Duración en segundos
            fps: Fotogramas por segundo
            width: Ancho del video
            height: Alto del video
            steps: Pasos de inferencia
            cfg_scale: Escala CFG
            seed: Semilla aleatoria (-1 para aleatorio)
            negative_prompt: Prompt negativo (opcional)

        Returns:
            bool: True si la generación fue exitosa
        """
        print(f"\n🎬 [VideoGen T2V] Iniciando generación de video...")
        print(f"   Prompt: {prompt[:80]}...")

        # Generar workflow de ComfyUI
        workflow = self._generar_workflow(
            prompt=prompt,
            negative_prompt=negative_prompt,
            duration=duration,
            fps=fps,
            width=width,
            height=height,
            steps=steps,
            cfg_scale=cfg_scale,
            seed=seed
        )

        # Guardar workflow
        workflow_path = os.path.join(self.comfyui_path, "input", "workflow_t2v.json")
        os.makedirs(os.path.dirname(workflow_path), exist_ok=True)

        with open(workflow_path, "w") as f:
            json.dump(workflow, f, indent=2)

        print(f"   Workflow guardado: {workflow_path}")

        # Ejecutar ComfyUI
        return self._ejecutar_comfyui(workflow_path, output_path)

    def _generar_workflow(self,
                          prompt: str,
                          negative_prompt: Optional[str],
                          duration: int,
                          fps: int,
                          width: int,
                          height: int,
                          steps: int,
                          cfg_scale: float,
                          seed: int) -> dict:
        """Genera el workflow de ComfyUI para T2V."""

        # Semilla
        if seed < 0:
            seed = int.from_bytes(os.urandom(4), 'big')

        # Workflow básico para T2V
        workflow = {
            "nodes": [
                # Nodo 1: Text Prompt (Positive)
                {
                    "id": 1,
                    "type": "TextPrompt",
                    "pos": [100, 100],
                    "size": [300, 100],
                    "widgets_values": [prompt]
                },
                # Nodo 2: Text Prompt (Negative)
                {
                    "id": 2,
                    "type": "TextPrompt",
                    "pos": [100, 250],
                    "size": [300, 100],
                    "widgets_values": [negative_prompt or "blurry, low quality, distorted, deformed"]
                },
                # Nodo 3: CLIPTextEncode (Positive)
                {
                    "id": 3,
                    "type": "CLIPTextEncode",
                    "pos": [400, 100],
                    "inputs": [
                        {"name": "text", "type": "STRING", "link": 1},
                        {"name": "clip", "type": "CLIP", "link": None}
                    ]
                },
                # Nodo 4: CLIPTextEncode (Negative)
                {
                    "id": 4,
                    "type": "CLIPTextEncode",
                    "pos": [400, 250],
                    "inputs": [
                        {"name": "text", "type": "STRING", "link": 2},
                        {"name": "clip", "type": "CLIP", "link": None}
                    ]
                },
                # Nodo 5: Empty Latent Video
                {
                    "id": 5,
                    "type": "EmptyLatentVideo",
                    "pos": [400, 400],
                    "widgets_values": [
                        1,  # batch_size
                        width,
                        height,
                        duration * fps,
                        fps,
                        1  # compression
                    ]
                },
                # Nodo 6: Load Model GGUF
                {
                    "id": 6,
                    "type": "LoadModelGGUF",
                    "pos": [700, 100],
                    "widgets_values": [self._get_model_filename()]
                },
                # Nodo 7: KSampler
                {
                    "id": 7,
                    "type": "KSampler",
                    "pos": [700, 300],
                    "widgets_values": [
                        seed,
                        steps,
                        cfg_scale,
                        "euler_ancestral",
                        "normal",
                        1.0
                    ]
                },
                # Nodo 8: VAE Decode
                {
                    "id": 8,
                    "type": "VAEDecodeTiled",
                    "pos": [1000, 300]
                },
                # Nodo 9: Save Video
                {
                    "id": 9,
                    "type": "SaveVideo",
                    "pos": [1200, 300],
                    "widgets_values": [output_path]
                }
            ],
            "models": [self._get_model_config()]
        }

        return workflow

    def _get_model_filename(self) -> str:
        """Retorna el nombre del archivo del modelo."""
        return f"Self-Forcing2.1-T2V-1.3B-{self.quantization.upper()}.gguf"

    def _get_model_config(self) -> dict:
        """Retorna la configuración del modelo."""
        return {
            "model_name": MODEL_CONFIG["model_name"],
            "model_path": os.path.join(
                self.model_path,
                self._get_model_filename()
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
            print(f"❌ [VideoGen T2V] No se encontró ejecutable de ComfyUI")
            return False

        try:
            print(f"🚀 [VideoGen T2V] Ejecutando ComfyUI...")

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
                print(f"✅ [VideoGen T2V] Video generado: {output_path}")
                return True
            else:
                print(f"❌ [VideoGen T2V] Error en generación:")
                print(result.stderr)
                return False

        except subprocess.TimeoutExpired:
            print(f"❌ [VideoGen T2V] Timeout - la generación tardó más de 10 minutos")
            return False
        except Exception as e:
            print(f"❌ [VideoGen T2V] Error: {e}")
            return False


# ============================================================================
# PIPELINE INTEGRADO: AUDIO + VIDEO T2V
# ============================================================================

class DisciplinaEnAceroPipelineT2V:
    """
    Pipeline completo para "Disciplina en Acero" usando T2V:
    1. Genera audio narrado
    2. Procesa audio (voice_director)
    3. Genera video desde texto (T2V)
    4. Combina audio + video
    """

    def __init__(self):
        """Inicializa el pipeline."""
        self.video_gen = VideoGeneratorT2V()
        print("🎬 [Pipeline T2V] Disciplina en Acero inicializado")

    def generar_episodio(self,
                        texto: str,
                        prompt_video: str,
                        output_video: str,
                        voice_audio: str = None) -> bool:
        """
        Genera un episodio completo.

        Args:
            texto: Texto para narración de voz
            prompt_video: Prompt para generación de video
            output_video: Video final de salida
            voice_audio: Archivo de audio de voz (opcional)

        Returns:
            bool: True si fue exitoso
        """
        print(f"\n{'='*60}")
        print("🎬 GENERANDO EPISODIO: DISCIPLINA EN ACERO (T2V)")
        print(f"{'='*60}")

        # 1. Generar video
        print(f"\n🎬 [Pipeline T2V] Generando video...")
        exito_video = self.video_gen.generar_video(
            prompt=prompt_video,
            output_path=output_video
        )

        if not exito_video:
            print("❌ [Pipeline T2V] Error al generar video")
            return False

        # 2. Si hay audio de voz, combinar
        if voice_audio and os.path.exists(voice_audio):
            print(f"\n🔊 [Pipeline T2V] Combinando audio + video...")
            return self._combinar_audio_video(voice_audio, output_video, output_video)

        print(f"\n✅ [Pipeline T2V] Episodio generado: {output_video}")
        return True

    def _combinar_audio_video(self,
                             audio_path: str,
                             video_path: str,
                             output_path: str) -> bool:
        """Combina audio y video usando ffmpeg."""

        try:
            result = subprocess.run(
                ["ffmpeg", "-version"],
                capture_output=True
            )

            if result.returncode != 0:
                print("⚠️ [Pipeline T2V] ffmpeg no disponible")
                return False

            cmd = [
                "ffmpeg",
                "-y",
                "-i", audio_path,
                "-i", video_path,
                "-c:v", "copy",
                "-c:a", "aac",
                "-strict", "experimental",
                output_path
            ]

            result = subprocess.run(cmd, capture_output=True, text=True)

            if result.returncode == 0:
                print(f"✅ [Pipeline T2V] Audio + Video combinados: {output_path}")
                return True
            else:
                print(f"❌ [Pipeline T2V] Error: {result.stderr}")
                return False

        except FileNotFoundError:
            print("⚠️ [Pipeline T2V] ffmpeg no encontrado")
            return False


# ============================================================================
# PUNTO DE ENTRADA
# ============================================================================

def main():
    """Función principal."""
    parser = argparse.ArgumentParser(
        description="Video Generator T2V - Text to Video",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"""
Ejemplos:
  # Generar video desde prompt de texto
  python video_generator_T2V.py --prompt "Scene: Industrial forge..."

  # Usar prompt predefinido
  python video_generator_T2V.py --preset forge

  # Pipeline completo
  python video_generator_T2V.py --pipeline --texto "Tu texto" --preset forge

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
        "--negative",
        help="Prompt negativo (opcional)"
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
        print(f"📝 [VideoGen T2V] Usando preset: {args.preset}")

    if not prompt:
        print("❌ Error: Debes proporcionar --prompt o --preset")
        parser.print_help()
        sys.exit(1)

    # Inicializar generador
    gen = VideoGeneratorT2V(
        comfyui_path=args.comfyui_path,
        quantization=args.quantization
    )

    # Generar video
    print(f"\n{'='*60}")
    print("🎬 VIDEO GENERATOR T2V - DISCIPLINA EN ACERO")
    print(f"{'='*60}")

    exito = gen.generar_video(
        prompt=prompt,
        output_path=args.output,
        duration=args.duration,
        fps=args.fps,
        width=args.width,
        height=args.height,
        steps=args.steps,
        cfg_scale=args.cfg,
        seed=args.seed,
        negative_prompt=args.negative
    )

    if exito:
        print(f"\n✅ Video generado exitosamente: {args.output}")
    else:
        print(f"\n❌ Error en generación de video")
        sys.exit(1)


if __name__ == "__main__":
    main()
