"""
forge_blog.py — MiuraForgeEngine / Blog Engine
================================================
Módulo MF-003-Astro: Doctrina Digital

Flujo completo:
  Google Sheets (Estado = LISTO_PARA_FORJAR)
    → Lee fila de BLOG_CONTENIDO
    → Alchemist transforma Cuerpo_Raw en Reseña de Acero
    → Genera archivo .md en src/content/blog/{slug}.md
    → Actualiza Estado = PUBLICADO en Sheets
    → Llama al Build Hook de Netlify al terminar

Prerequisitos:
  pip install python-frontmatter gspread

Variables de entorno (.env de MiuraForge):
  NETLIFY_BUILD_HOOK=https://api.netlify.com/build_hooks/TU_ID

Uso:
  python forge_blog.py                    # procesa todos los LISTO_PARA_FORJAR
  python forge_blog.py --dry-run          # simula sin escribir archivos ni llamar Netlify
  python forge_blog.py --id 3             # procesa solo la fila con ID = 3
  python forge_blog.py --sin-netlify      # genera .md pero no dispara el build
"""

import os
import sys
import re
import argparse
import requests
import frontmatter
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# ---------------------------------------------------------------------------
# CONFIGURACIÓN
# ---------------------------------------------------------------------------

BASE_DIR        = Path(__file__).resolve().parent
BLOG_OUTPUT_DIR = BASE_DIR / "disciplinaenacero.com" / "src" / "content" / "blog"
NETLIFY_HOOK    = os.getenv("NETLIFY_BUILD_HOOK", "")

SHEET_NAME      = "Miura_Blog_Content"
TAB_NAME        = "BLOG_CONTENIDO"
ESTADO_PROCESAR = "LISTO_PARA_FORJAR"
ESTADO_LISTO    = "PUBLICADO"

# Columnas de la hoja (deben coincidir exactamente con los headers del Sheet)
COL = {
    "id":          "A: ID",
    "estado":      "B: Estado",
    "titulo":      "C: Título",
    "slug":        "D: Slug",
    "fecha":       "E: Fecha",
    "descripcion": "F: Descripción (meta)",
    "keywords":    "G: Keywords",
    "categoria":   "H: Categoría",
    "imagen":      "I: Imagen_URL",
    "amazon":      "J: Enlace_Afiliado_Amazon",
    "cuerpo":      "K: Cuerpo_Raw",
    "tags":        "L: Tags",
    "readtime":    "M: ReadTime_Min",
    "featured":    "N: Featured",
}

# ---------------------------------------------------------------------------
# CONEXIÓN CON SHEETS VIA DATABASE DE MIURA
# ---------------------------------------------------------------------------

def conectar_sheets():
    try:
        sys.path.append(str(BASE_DIR))
        from core.database import Database
        db = Database()
        hoja = db.spreadsheet.worksheet(TAB_NAME)
        return db, hoja
    except Exception as e:
        print(f"❌ Error conectando con Sheets: {e}")
        print("   Asegúrate de ejecutar desde la raíz de MiuraForgeEngine")
        sys.exit(1)


def leer_pendientes(hoja, id_especifico: str = "") -> list[dict]:
    registros = hoja.get_all_records()
    if id_especifico:
        return [r for r in registros if str(r.get(COL["id"], "")).strip() == id_especifico]
    return [r for r in registros if str(r.get(COL["estado"], "")).strip() == ESTADO_PROCESAR]


def actualizar_estado(hoja, id_fila: str, nuevo_estado: str):
    registros = hoja.get_all_records()
    headers   = hoja.row_values(1)
    col_id    = headers.index(COL["id"]) + 1
    col_est   = headers.index(COL["estado"]) + 1
    for i, r in enumerate(registros, start=2):
        if str(r.get(COL["id"], "")).strip() == str(id_fila).strip():
            hoja.update_cell(i, col_est, nuevo_estado)
            return True
    return False


# ---------------------------------------------------------------------------
# ALCHEMIST — transformación de texto a Reseña de Acero
# ---------------------------------------------------------------------------

PROMPT_ALCHEMIST = """Eres el Alchemist de Disciplina en Acero.

Tu misión: transformar el texto en bruto en una RESEÑA DE ACERO.

DOCTRINA INQUEBRANTABLE:
1. Tono: masculino, autoritario, filosófico de acción
2. NO consuelas, NO motivas con vacío, NO usas frases de coaching genérico
3. REVELAS el autoengaño, DIAGNOSTICAS el problema, ORDENAS la acción
4. El libro reseñado es el "qué". "El Hombre que Dejó de Mentirse" es el "quién" y el "cómo"
5. Metáforas permitidas: acero, forja, fragua, katana, yunque, vacío, presión, carbono
6. Verbos PROHIBIDOS: "podrías", "quizás", "tal vez", "intenta", "considera"
7. Estructura: Problema → Revelación incómoda → Acción concreta → CTA

ESTRUCTURA DEL ARTÍCULO:
- Apertura impactante (2-3 párrafos): golpe directo al problema
- H2 "El mapa sin el acero": análisis crítico del libro desde la doctrina
- H2 "La forja real": qué da el libro + qué falta sin identidad de acero
- H2 "Veredicto de acero": conclusión, 2-3 párrafos
- CTA final: párrafo que lleva al libro "El Hombre que Dejó de Mentirse"

LONGITUD: 600-900 palabras. Cada palabra debe pesar.

TÍTULO DEL ARTÍCULO: {titulo}
TEXTO EN BRUTO (transforma esto):
{cuerpo_raw}

---
Entrega SOLO el contenido del artículo en Markdown. Sin explicaciones, sin comentarios.
Comienza directamente con el primer párrafo.
"""


def llamar_alchemist(titulo: str, cuerpo_raw: str) -> str:
    """Llama al Alchemist (LLM del engine) para transformar el texto."""
    try:
        from llm.factory import LLMFactory
        brain = LLMFactory.get_brain("alchemist")
        prompt = PROMPT_ALCHEMIST.format(titulo=titulo, cuerpo_raw=cuerpo_raw)
        resultado = brain.generate(prompt)
        return resultado.strip()
    except Exception as e:
        print(f"  ⚠️  Error en Alchemist: {e}")
        print("  Usando texto en bruto sin transformar...")
        return cuerpo_raw


# ---------------------------------------------------------------------------
# GENERADOR DE MARKDOWN
# ---------------------------------------------------------------------------

def generar_slug(titulo: str) -> str:
    """Genera un slug limpio desde el título si no viene en el Sheet."""
    slug = titulo.lower()
    slug = re.sub(r'[áàäâ]', 'a', slug)
    slug = re.sub(r'[éèëê]', 'e', slug)
    slug = re.sub(r'[íìïî]', 'i', slug)
    slug = re.sub(r'[óòöô]', 'o', slug)
    slug = re.sub(r'[úùüû]', 'u', slug)
    slug = re.sub(r'[ñ]', 'n', slug)
    slug = re.sub(r'[^a-z0-9\s-]', '', slug)
    slug = re.sub(r'[\s]+', '-', slug.strip())
    slug = re.sub(r'-+', '-', slug)
    return slug[:80]


def generar_md(row: dict, contenido_generado: str, output_dir: Path, dry_run: bool = False) -> str | None:
    """
    Genera el archivo .md con frontmatter compatible con Astro Content Collections.
    Retorna la ruta del archivo generado, o None si falló.
    """
    titulo    = row.get(COL["titulo"], "").strip()
    slug      = row.get(COL["slug"], "").strip() or generar_slug(titulo)
    fecha_raw = row.get(COL["fecha"], "").strip() or datetime.now().strftime("%Y-%m-%d")
    desc      = row.get(COL["descripcion"], "").strip()
    keywords  = [k.strip() for k in row.get(COL["keywords"], "").split(",") if k.strip()]
    categoria = row.get(COL["categoria"], "Reseñas").strip()
    imagen    = row.get(COL["imagen"], "").strip()
    amazon    = row.get(COL["amazon"], "").strip()
    tags_raw  = row.get(COL["tags"], "")
    tags      = [t.strip() for t in str(tags_raw).split(",") if t.strip()]
    readtime_raw = row.get(COL["readtime"], "")
    featured_raw = row.get(COL["featured"], "FALSE")

    try:
        readtime = int(float(str(readtime_raw))) if readtime_raw else None
    except:
        readtime = None

    featured = str(featured_raw).upper() in ("TRUE", "1", "YES", "SÍ", "SI")

    # Construir frontmatter
    meta = {
        "title":       titulo,
        "slug":        slug,
        "date":        fecha_raw,
        "description": desc,
    }
    if keywords:   meta["keywords"]    = keywords
    if categoria:  meta["category"]    = categoria
    if imagen:     meta["image"]       = imagen
    if amazon:     meta["amazon_link"] = amazon
    if tags:       meta["tags"]        = tags
    if readtime:   meta["readTime"]    = readtime
    meta["featured"] = featured

    post = frontmatter.Post(contenido_generado, **meta)
    output_path = output_dir / f"{slug}.md"

    if dry_run:
        print(f"  [DRY-RUN] Se generaría: {output_path}")
        print(f"  Frontmatter: title='{titulo}', slug='{slug}', date='{fecha_raw}'")
        return str(output_path)

    output_dir.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(frontmatter.dumps(post))

    size_kb = output_path.stat().st_size / 1024
    print(f"  ✅ Generado: {output_path.name} ({size_kb:.1f} KB)")
    return str(output_path)


# ---------------------------------------------------------------------------
# TRIGGER DE NETLIFY
# ---------------------------------------------------------------------------

def disparar_netlify(dry_run: bool = False):
    if not NETLIFY_HOOK:
        print("⚠️  NETLIFY_BUILD_HOOK no configurado en .env — saltando build")
        return False

    if dry_run:
        print(f"  [DRY-RUN] Llamaría al Build Hook: {NETLIFY_HOOK[:50]}...")
        return True

    try:
        r = requests.post(NETLIFY_HOOK, timeout=15)
        if r.status_code in (200, 201):
            print(f"🚀 Netlify Build Hook disparado — sitio reconstruyéndose...")
            return True
        else:
            print(f"⚠️  Build Hook respondió {r.status_code}: {r.text[:100]}")
            return False
    except Exception as e:
        print(f"❌ Error llamando al Build Hook: {e}")
        return False


# ---------------------------------------------------------------------------
# PIPELINE PRINCIPAL
# ---------------------------------------------------------------------------

def forjar_blog(dry_run: bool = False, id_especifico: str = "", sin_netlify: bool = False):
    print("⚔️  MIURA FORGE — Blog Engine")
    print("=" * 60)

    db, hoja = conectar_sheets()
    pendientes = leer_pendientes(hoja, id_especifico)

    if not pendientes:
        msg = f"ID {id_especifico}" if id_especifico else "Estado = LISTO_PARA_FORJAR"
        print(f"✅ No hay artículos pendientes ({msg})")
        return

    print(f"📋 Artículos a procesar: {len(pendientes)}")
    if dry_run:
        print("🔍 MODO DRY-RUN — sin escritura de archivos ni llamadas a Netlify")
    print()

    generados = 0
    fallidos  = 0

    for row in pendientes:
        id_fila = str(row.get(COL["id"], "")).strip()
        titulo  = row.get(COL["titulo"], "").strip()
        cuerpo  = row.get(COL["cuerpo"], "").strip()

        print(f"{'─'*60}")
        print(f"📝 [{id_fila}] {titulo[:55]}...")

        if not titulo:
            print(f"  ❌ Sin título — saltando")
            fallidos += 1
            continue

        if not cuerpo:
            print(f"  ⚠️  Cuerpo_Raw vacío — generando esqueleto básico")
            cuerpo = f"Reseña de {titulo}. Tema: disciplina, identidad, forja del hombre."

        # Transformar con el Alchemist
        print(f"  🔧 Alchemist procesando...")
        contenido = llamar_alchemist(titulo, cuerpo)

        # Generar .md
        ruta = generar_md(row, contenido, BLOG_OUTPUT_DIR, dry_run)

        if ruta:
            generados += 1
            if not dry_run:
                actualizar_estado(hoja, id_fila, ESTADO_LISTO)
                print(f"  📊 Estado actualizado → {ESTADO_LISTO}")
        else:
            fallidos += 1

    # Disparar Netlify si hubo generaciones exitosas
    print()
    print("=" * 60)
    print(f"📊 Resumen: {generados} generados | {fallidos} fallidos")

    if generados > 0 and not sin_netlify:
        disparar_netlify(dry_run)
    elif sin_netlify:
        print("ℹ️  Build Hook omitido (--sin-netlify)")

    if generados > 0 and not dry_run:
        print(f"\n✅ Artículos disponibles en: {BLOG_OUTPUT_DIR}")
        print("   Netlify los compilará y publicará automáticamente.")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Blog Engine — MiuraForgeEngine")
    parser.add_argument("--dry-run",     action="store_true",
                        help="Simula sin escribir archivos ni llamar Netlify")
    parser.add_argument("--id",          type=str, default="",
                        help="Procesar solo la fila con este ID")
    parser.add_argument("--sin-netlify", action="store_true",
                        help="Genera .md pero no dispara el Build Hook")
    args = parser.parse_args()

    forjar_blog(
        dry_run      = args.dry_run,
        id_especifico = args.id,
        sin_netlify  = args.sin_netlify,
    )
