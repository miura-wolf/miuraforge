"""
common.py — Funciones compartidas entre módulos de tools.
Evita duplicación de lógica común.
"""

import os
import re
from rich.console import Console

console = Console()


def parsear_guiones_apertura(md_path):
    """
    Parsea Guiones_Apertura_Canal.md y extrae ID, Guion y Prompts de referencia.

    Returns:
        list[dict]: Cada dict tiene keys: id_sesion, guion, prompts_referencia
    """
    if not os.path.exists(md_path):
        console.print(f"[red]No se encontró: {md_path}[/]")
        return []

    with open(md_path, "r", encoding="utf-8") as f:
        contenido = f.read()

    secciones = re.split(r"(?=^## 🎬)", contenido, flags=re.MULTILINE)
    resultado = []

    for seccion in secciones:
        seccion = seccion.strip()
        if not seccion.startswith("## 🎬"):
            continue

        m_id = re.search(r"\*\*ID:\*\*\s*`([^`]+)`", seccion)
        if not m_id:
            continue
        id_sesion = m_id.group(1).strip()

        # Extraer Guion (después de Objetivo: hasta separador)
        match_guion = re.search(
            r"Objetivo:.*?\n\s*\n(.*?)(?=\n\n🎬|\n\nCopiar y pegar|\n\n---)",
            seccion,
            re.DOTALL,
        )
        if match_guion:
            guion_texto = match_guion.group(1).strip()
            guion_texto = re.sub(r"^>\s*", "", guion_texto, flags=re.MULTILINE)
        else:
            guion_texto = ""

        # Extraer Prompts de Referencia
        prompts_ref = re.findall(
            r"Cinematic 9:16 vertical video\..*?(?=\n\n|\n---|\Z)",
            seccion,
            re.DOTALL,
        )
        prompts_text = "\n".join([p.strip() for p in prompts_ref])

        resultado.append(
            {
                "id_sesion": id_sesion,
                "guion": guion_texto,
                "prompts_referencia": prompts_text,
            }
        )

    return resultado


def leer_doctrina_youtube():
    """Lee el archivo de doctrina para YouTube (prompts/youtube_forge.txt)."""
    ruta = os.path.join(os.path.dirname(os.path.dirname(__file__)), "prompts", "youtube_forge.txt")
    if not os.path.exists(ruta):
        console.print(f"[red]No se encontró la doctrina: {ruta}[/]")
        return ""
    with open(ruta, "r", encoding="utf-8") as f:
        return f.read()
