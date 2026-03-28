"""
⚔️ FORJA VISUAL MASIVA — Sistema Dual (Imagen + Animación)
Genera prompts de imagen y directivas de animación para cada fragmento de guion.
Salida: output/masivo_grok_prompts.md + Google Sheets actualizado.
"""

import os
import sys
import time
from dotenv import load_dotenv

sys.path.append(os.path.abspath(os.path.dirname(os.path.dirname(__file__))))
from core.database import Database
from core.visual_director import VisualDirector
from rich.console import Console
from rich.progress import track

load_dotenv()
console = Console()


def mass_visual_forge(target_id=None):
    console.print(
        "\n[bold cyan]⚔️ FORJA VISUAL MASIVA — MODO DUAL (Imagen + Animación) ⚔️[/]"
    )
    db = Database()
    director_v = VisualDirector(db_manager=db)

    # Obtener registros
    try:
        rows = db.produccion.get_all_values()
    except Exception as e:
        console.print(f"[red]Error al leer la base de datos: {e}[/]")
        return

    if len(rows) <= 1:
        console.print("[red]No hay suficientes datos en la tabla PRODUCCION.[/]")
        return

    headers = rows[0]

    # Búsqueda segura de índices
    try:
        idx_id = headers.index("ID_Sesion")
        idx_fase = headers.index("Fase")
        idx_guion = headers.index("Guion")
        idx_visual = headers.index("Prompt_Visual")
    except ValueError as e:
        console.print(f"[red]Falta una columna crítica en PRODUCCION: {e}.[/]")
        return

    # Filtrar scripts MASTER pendientes de forja visual dual
    pendientes = []

    for i, r in enumerate(rows[1:], start=2):
        fase = str(r[idx_fase]).strip().upper() if len(r) > idx_fase else ""
        guion = str(r[idx_guion]).strip() if len(r) > idx_guion else ""
        visual = str(r[idx_visual]).strip() if len(r) > idx_visual else ""

        # Pendiente si: vacío, dice PENDIENTE, o NO tiene el formato dual (---CLIP)
        is_pendiente = (
            visual == "" or visual.upper() == "N/A" or "PENDIENTE" in visual.upper()
        )
        is_formato_viejo = "---CLIP" not in visual

        id_sesion = str(r[idx_id]).strip() if len(r) > idx_id else f"Fila_{i}"

        if target_id:
            if id_sesion == target_id:
                pendientes.append((i, id_sesion, guion))
                break  # Solo procesamos el ID solicitado
        elif fase == "MASTER" and (is_pendiente or is_formato_viejo):
            pendientes.append((i, id_sesion, guion))

    if not pendientes:
        console.print(
            "[green]Todos los guiones MASTER ya cuentan con visuales en formato dual.[/]"
        )
        return

    console.print(
        f"[yellow]Se encontraron {len(pendientes)} guiones pendientes de Forja Visual Dual.[/]"
    )

    doctrina_base = director_v.leer_doctrina()
    os.makedirs(
        os.path.join(os.path.dirname(os.path.dirname(__file__)), "output"),
        exist_ok=True,
    )
    out_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)), "output", "masivo_grok_prompts.md"
    )
    console.print(f"[cyan]Escribiendo resultados en: {out_path}[/]")

    with open(out_path, "w", encoding="utf-8") as f:
        f.write("# 🎥 Forja Visual Dual — Imagen + Animación\n\n")
        f.write(
            "> *Cada clip tiene: fragmento de guion, prompt de imagen (para NVIDIA Flux) y directiva de animación (para Grok/Qwen).*\n\n"
        )

    for fila_sheet, id_sesion, guion_texto in track(
        pendientes, description="Forjando Prompts Duales..."
    ):
        duracion = director_v.estimar_duracion_segundos(guion_texto)
        num_clips = max(1, round(duracion / 5))

        instruccion = f"""
        Misión:
        1. Toma el siguiente guion y divídelo lógicamente en EXACTAMENTE {num_clips} fragmentos secuenciales.
        2. Para cada fragmento, genera el bloque dual: [IMAGEN] + [ANIMACIÓN].
        3. La variable NUM_CLIPS es {num_clips}.
        4. Usa el formato de salida definido en tu doctrina (---CLIP X---).
        
        --- GUION A PROCESAR ---
        {guion_texto}
        """

        prompt_llm = f"{doctrina_base}\n\n{instruccion}"

        try:
            respuesta = director_v.brain.generate(prompt_llm).strip()

            with open(out_path, "a", encoding="utf-8") as f:
                f.write(
                    f"## ID: {id_sesion} (Fila: {fila_sheet} | {duracion}s | {num_clips} Clips)\n\n"
                )
                f.write(f"{respuesta}\n\n")
                f.write("---\n\n")

            # Sincronización con Sheets (Con reintentos)
            exito_update = False
            for intento in range(3):
                try:
                    db.produccion.update_cell(fila_sheet, idx_visual + 1, respuesta)
                    exito_update = True
                    break
                except Exception as e:
                    console.print(
                        f"   [yellow]⚠️ Intento {intento + 1} de actualización falló: {e}[/]"
                    )
                    time.sleep(2)

            if exito_update:
                console.print(f"   [green]✅ Sheets actualizado para {id_sesion}[/]")
            else:
                console.print(
                    f"   [red]❌ NO se pudo actualizar Sheets para {id_sesion}. No se saltará la próxima vez.[/]"
                )

        except Exception as e:
            console.print(f"[red]Error procesando {id_sesion}: {e}[/]")

    console.print("\n[bold green]✅ Forja Visual Dual completada exitosamente.[/]")
    console.print(f"Revisa el archivo [yellow]output/masivo_grok_prompts.md[/]")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Forja Visual Masiva")
    parser.add_argument(
        "--id", type=str, help="Forzar generación para un ID específico", default=None
    )

    args = parser.parse_args()
    mass_visual_forge(target_id=args.id)
