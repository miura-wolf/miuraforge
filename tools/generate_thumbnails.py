#!/usr/bin/env python3
"""
⚔️ GENERADOR DE THUMBNAILS - YouTube Shorts
Usa los motores de MiuraForge (NVIDIA/Nebius/Replicate)

Tamaño: 1080x1920 (9:16 vertical)
Estilo: Cinematic, industrial, Disciplina en Acero
"""

import os
import sys

sys.path.append(os.path.abspath(os.path.dirname(os.path.dirname(__file__))))

from tools.image_forge import generar_imagen_nvidia, generar_imagen_nebius, generar_imagen_replicate
from rich.console import Console

console = Console()

# Configuración
OUTPUT_DIR = "output/thumbnails"
WIDTH = 1080
HEIGHT = 1920
RATIO = "9:16"

# Prompt base estilo Disciplina en Acero
PROMPT_BASE = """Cinematic portrait, vertical composition 9:16, industrial brutalist aesthetic, 
dramatic chiaroscuro lighting from above, metallic textures and surfaces, 
Blade Runner color palette (deep blacks, steel grays, hints of burnt orange), 
close-up of a man with intense expression showing inner conflict, 
heavy shadows on face, fog and atmospheric haze, concrete brutalist architecture background,
photorealistic, 8K resolution, sharp focus, cinematic film grain, 
no text, no watermarks, professional color grading"""

# 4 thumbnails para la serie "El Diagnóstico"
THUMBNAILS = [
    {
        "id": 1,
        "titulo": "TE CONVENCISTE DE QUE ERES PRODUCTIVO",
        "tema": "Productividad",
        "adicionales": "man looking at messy desk with overwhelmed expression, procrastination theme",
    },
    {
        "id": 2,
        "titulo": "SIGUES ESPERANDO EL MOMENTO PERFECTO",
        "tema": "Parálisis",
        "adicionales": "man standing at crossroads, paralyzed by indecision, frozen in time",
    },
    {
        "id": 3,
        "titulo": "TE MIENTES CADA MAÑANA",
        "tema": "Autoengaño",
        "adicionales": "man looking at mirror with disappointed expression, self-deception theme",
    },
    {
        "id": 4,
        "titulo": "PREFIERES SOÑAR A PROBAR",
        "tema": "Fantasía",
        "adicionales": "man with eyes closed dreaming while reality crumbles around him",
    },
]


def generar_thumbnail(thumbnail_data, motor="auto"):
    """Genera un thumbnail con el motor especificado."""

    # Construir prompt completo
    prompt = f"{PROMPT_BASE}, {thumbnail_data['adicionales']}"

    # Nombre archivo
    filename = f"thumbnail_{thumbnail_data['id']:02d}_{thumbnail_data['tema'].lower()}.png"
    output_path = os.path.join(OUTPUT_DIR, filename)

    # Crear directorio
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    console.print(
        f"\n[bold cyan]🎨 Generando Thumbnail {thumbnail_data['id']}:[/] {thumbnail_data['titulo']}"
    )
    console.print(f"[dim]Motor: {motor} | Tamaño: {WIDTH}x{HEIGHT} ({RATIO})[/]")

    # Generar según motor
    if motor == "nvidia":
        resultado = generar_imagen_nvidia(prompt, output_path, WIDTH, HEIGHT)
    elif motor == "nebius":
        resultado = generar_imagen_nebius(prompt, output_path, WIDTH, HEIGHT)
    elif motor == "replicate":
        resultado = generar_imagen_replicate(prompt, output_path, WIDTH, HEIGHT)
    else:  # auto
        # Intentar NVIDIA primero (gratis), si falla ir a Nebius
        console.print("[yellow]Intentando NVIDIA (gratis)...[/]")
        resultado = generar_imagen_nvidia(prompt, output_path, WIDTH, HEIGHT)
        if not resultado:
            console.print("[yellow]NVIDIA filtró o falló. Intentando Nebius...[/]")
            resultado = generar_imagen_nebius(prompt, output_path, WIDTH, HEIGHT)
        if not resultado:
            console.print("[yellow]Nebius falló. Intentando Replicate...[/]")
            resultado = generar_imagen_replicate(prompt, output_path, WIDTH, HEIGHT)

    if resultado:
        console.print(f"[green]✅ Thumbnail generado:[/] {output_path}")
        return output_path
    else:
        console.print(f"[red]❌ Falló la generación del thumbnail {thumbnail_data['id']}[/]")
        return None


def main():
    """Genera los 4 thumbnails para FASE 2."""

    console.print("\n" + "=" * 60)
    console.print("[bold red]⚔️ MIURA THUMBNAIL FORGE[/]")
    console.print("[dim]Generando thumbnails para FASE 2 - Canal YouTube[/]")
    console.print("=" * 60)

    console.print(f"\n[bold]Configuración:[/]")
    console.print(f"  • Tamaño: {WIDTH}x{HEIGHT} ({RATIO})")
    console.print(f"  • Estilo: Cinematic Industrial")
    console.print(f"  • Motor: AUTO (NVIDIA → Nebius → Replicate)")
    console.print(f"  • Output: {OUTPUT_DIR}/")

    # Generar los 4 thumbnails
    generados = []
    for thumb in THUMBNAILS:
        path = generar_thumbnail(thumb, motor="auto")
        if path:
            generados.append(path)

    # Resumen
    console.print("\n" + "=" * 60)
    console.print(f"[bold green]✅ COMPLETADO:[/] {len(generados)}/4 thumbnails generados")
    console.print("=" * 60)

    if generados:
        console.print("\n[bold]Archivos generados:[/]")
        for path in generados:
            console.print(f"  📁 {path}")

        console.print("\n[bold yellow]⚠️ NOTA IMPORTANTE:[/]")
        console.print("Estos thumbnails NO tienen texto.")
        console.print("Debes agregar el texto 'TE CONVENCISTE...' usando un editor:")
        console.print("  • Canva (gratis): canva.com")
        console.print("  • Photoshop")
        console.print("  • GIMP (gratis)")
        console.print("\nO usar PIL/Pillow para agregar texto automáticamente.")

    return generados


if __name__ == "__main__":
    # Permitir selección de motor
    import sys

    motor = sys.argv[1] if len(sys.argv) > 1 else "auto"

    if motor not in ["auto", "nvidia", "nebius", "replicate"]:
        console.print("[red]Motor inválido. Usa: auto, nvidia, nebius, replicate[/]")
        sys.exit(1)

    main()
