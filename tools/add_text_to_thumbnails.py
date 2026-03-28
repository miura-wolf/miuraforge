#!/usr/bin/env python3
"""
⚔️ ADD TEXT TO THUMBNAILS - Agrega texto industrial a las miniaturas
Usa PIL/Pillow para editar imágenes sin Canva externo
"""

import os
import sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from rich.console import Console

console = Console()

THUMBNAILS_CONFIG = [
    {
        "id": 1,
        "linea1": "TE CONVENCISTE",
        "linea2": "DE QUE ERES",
        "linea3": "PRODUCTIVO",
        "archivo": "thumbnail_01_productividad.png",
    },
    {
        "id": 2,
        "linea1": "SIGUES ESPERANDO",
        "linea2": "EL MOMENTO",
        "linea3": "PERFECTO",
        "archivo": "thumbnail_02_paralisis.png",
    },
    {
        "id": 3,
        "linea1": "TE MIENTES",
        "linea2": "CADA",
        "linea3": "MAÑANA",
        "archivo": "thumbnail_03_autoengano.png",
    },
    {
        "id": 4,
        "linea1": "PREFIERES",
        "linea2": "SOÑAR",
        "linea3": "A PROBAR",
        "archivo": "thumbnail_04_fantasia.png",
    },
]


def get_font(size):
    """Obtiene una fuente bold grande."""
    # Intentar fuentes comunes en orden de preferencia
    font_paths = [
        "C:/Windows/Fonts/impact.ttf",  # Impact - industrial/bold
        "C:/Windows/Fonts/arialbd.ttf",  # Arial Bold
        "C:/Windows/Fonts/calibrib.ttf",  # Calibri Bold
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",  # Linux
        "/System/Library/Fonts/Helvetica.ttc",  # Mac
    ]

    for font_path in font_paths:
        if os.path.exists(font_path):
            try:
                return ImageFont.truetype(font_path, size)
            except:
                pass

    # Fallback a fuente default
    return ImageFont.load_default()


def add_text_to_thumbnail(image_path, output_path, linea1, linea2, linea3):
    """Agrega texto industrial a una miniatura."""

    # Abrir imagen
    img = Image.open(image_path)
    draw = ImageDraw.Draw(img)
    width, height = img.size

    # Configuración de texto
    font_size = 100  # Tamaño grande para impacto
    font = get_font(font_size)

    # Colores
    text_color = (255, 255, 255)  # Blanco puro
    outline_color = (0, 0, 0)  # Negro para contorno
    outline_width = 4

    # Posición Y (arriba, 15% desde el borde superior)
    y_start = int(height * 0.15)
    line_spacing = font_size + 20

    # Función para dibujar texto con contorno
    def draw_text_with_outline(text, y_pos):
        x = width // 2

        # Dibujar contorno (negro) en 8 direcciones
        for dx in range(-outline_width, outline_width + 1):
            for dy in range(-outline_width, outline_width + 1):
                if dx != 0 or dy != 0:
                    draw.text(
                        (x + dx, y_pos + dy), text, font=font, fill=outline_color, anchor="mm"
                    )

        # Dibujar texto principal (blanco)
        draw.text((x, y_pos), text, font=font, fill=text_color, anchor="mm")

    # Dibujar las 3 líneas de texto
    draw_text_with_outline(linea1.upper(), y_start)
    draw_text_with_outline(linea2.upper(), y_start + line_spacing)
    draw_text_with_outline(linea3.upper(), y_start + line_spacing * 2)

    # Agregar marca pequeña abajo (opcional)
    marca_font = get_font(30)
    marca_text = "DISCIPLINA EN ACERO"
    marca_y = height - 80

    # Contorno para marca
    for dx in range(-2, 3):
        for dy in range(-2, 3):
            if dx != 0 or dy != 0:
                draw.text(
                    (width // 2 + dx, marca_y + dy),
                    marca_text,
                    font=marca_font,
                    fill=outline_color,
                    anchor="mm",
                )

    # Marca principal
    draw.text(
        (width // 2, marca_y), marca_text, font=marca_font, fill=(192, 192, 192), anchor="mm"
    )  # Gris acero

    # Guardar
    img.save(output_path, quality=95)
    console.print(f"[green]✅ Thumbnail con texto:[/] {output_path}")

    return output_path


def main():
    """Procesa todos los thumbnails y les agrega texto."""

    input_dir = "output/thumbnails"
    output_dir = "output/thumbnails_final"

    console.print("\n" + "=" * 60)
    console.print("[bold red]⚔️ AGREGANDO TEXTO A THUMBNAILS[/]")
    console.print("=" * 60)

    # Crear directorio de salida
    os.makedirs(output_dir, exist_ok=True)

    procesados = []

    for config in THUMBNAILS_CONFIG:
        input_path = os.path.join(input_dir, config["archivo"])

        # Verificar si existe el archivo base
        if not os.path.exists(input_path):
            console.print(f"[yellow]⚠️ No encontrado:[/] {input_path}")
            console.print(
                f"[dim]   Saltando... Genera primero con:[/] python tools/generate_thumbnails.py"
            )
            continue

        # Nombre de salida
        output_filename = f"thumbnail_{config['id']:02d}_final.png"
        output_path = os.path.join(output_dir, output_filename)

        console.print(f"\n[bold cyan]📝 Procesando Thumbnail {config['id']}:[/]")
        console.print(f"[dim]   Input: {input_path}[/]")
        console.print(f"   Texto: {config['linea1']} {config['linea2']} {config['linea3']}")

        try:
            result = add_text_to_thumbnail(
                input_path, output_path, config["linea1"], config["linea2"], config["linea3"]
            )
            procesados.append(result)
        except Exception as e:
            console.print(f"[red]❌ Error:[/] {e}")

    # Resumen
    console.print("\n" + "=" * 60)
    console.print(f"[bold green]✅ COMPLETADO:[/] {len(procesados)}/4 thumbnails con texto")
    console.print("=" * 60)

    if procesados:
        console.print("\n[bold]Thumbnails listos para YouTube:[/]")
        for path in procesados:
            console.print(f"  📁 {path}")

        console.print("\n[bold yellow]⚔️ INSTRUCCIONES PARA YOUTUBE:[/]")
        console.print("1. Ve a YouTube Studio")
        console.print("2. Sube tu Short")
        console.print("3. En 'Detalles' → Click en 'Subir miniatura'")
        console.print("4. Selecciona el archivo _final.png")
        console.print("5. Guarda")

        console.print("\n[dim]Los thumbnails están optimizados para:[/]")
        console.print("  • 1080x1920 (9:16 vertical)")
        console.print("  • Texto grande legible en móvil")
        console.print("  • Estilo industrial/cinematic")
        console.print("  • Contorno negro para contraste")


if __name__ == "__main__":
    main()
