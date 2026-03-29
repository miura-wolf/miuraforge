"""
forge_blog.py — MiuraForgeEngine / Blog Engine
================================================
Módulo MF-003-Astro: Doctrina Digital

Flujo completo:
  Google Sheets (LIBRO_ESTADO = ancla_lista)
    → Lee fila de BLOG_CONTENIDO
    → Blog Alchemist (core/blog_alchemist.py) transforma Cuerpo_Raw en Reseña de Acero
    → ANCLA_VERDAD se inserta INTACTA (jamás se parafrasea)
    → Genera archivo .md en src/content/blog/{slug}.md
    → Actualiza LIBRO_ESTADO = publicado en Sheets
    → Llama al Build Hook de Netlify al terminar

Pipeline separado de alchemist.py (guiones YouTube).
Solo procesa registros donde LIBRO_ESTADO = 'ancla_lista'.

Prerequisitos:
  pip install python-frontmatter gspread

Variables de entorno (.env de MiuraForge):
  NETLIFY_BUILD_HOOK=https://api.netlify.com/build_hooks/TU_ID

Uso:
  python forge_blog.py                    # procesa todos los ancla_lista
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
BLOG_OUTPUT_DIR = BASE_DIR.parent / "disciplinaenacero" / "src" / "content" / "blog"
NETLIFY_HOOK    = os.getenv("NETLIFY_BUILD_HOOK", "")

SHEET_NAME      = "Miura_Blog_Content"
TAB_NAME        = "BLOG_CONTENIDO"
ESTADO_PROCESAR = "ancla_lista"      # LIBRO_ESTADO: solo procesar cuando el ancla está lista
ESTADO_LISTO    = "publicado"         # LIBRO_ESTADO: estado tras publicación

# Columnas de la hoja (deben coincidir exactamente con los headers del Sheet)
COL = {
    "id":           "ID",
    "estado":       "Estado",
    "titulo":       "Título",
    "slug":         "Slug",
    "fecha":        "Fecha",
    "descripcion":  "Descripción",
    "keywords":     "Keywords",
    "categoria":    "Categoría",
    "imagen":       "Imagen_URL",
    "amazon":       "Enlace_Afiliado",
    "cuerpo":       "Cuerpo_Raw",
    "tags":         "Tags",
    "readtime":     "ReadTime_Min",
    "featured":     "Featured",
    "ancla":        "ANCLA_VERDAD",
    "libro_estado": "LIBRO_ESTADO",
}

# ---------------------------------------------------------------------------
# CONEXIÓN CON SHEETS VIA DATABASE DE MIURA
# ---------------------------------------------------------------------------

def conectar_sheets():
    try:
        sys.path.append(str(BASE_DIR))
        from core.database import Database
        db = Database()
        hoja = db.blog_contenido
        return db, hoja
    except Exception as e:
        print(f"❌ Error conectando con Sheets: {e}")
        print("   Asegúrate de ejecutar desde la raíz de MiuraForgeEngine")
        sys.exit(1)


def leer_pendientes(hoja, id_especifico: str = "") -> list[dict]:
    registros = hoja.get_all_records()
    if id_especifico:
        return [r for r in registros if str(r.get(COL["id"], "")).strip() == id_especifico]
    # Solo procesa registros donde LIBRO_ESTADO == ancla_lista
    return [r for r in registros if str(r.get(COL["libro_estado"], "")).strip().lower() == ESTADO_PROCESAR]


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


def actualizar_libro_estado(hoja, id_fila: str, nuevo_estado: str):
    """Actualiza la columna LIBRO_ESTADO para un registro específico."""
    registros = hoja.get_all_records()
    headers   = hoja.row_values(1)
    col_id    = headers.index(COL["id"]) + 1
    col_libro = headers.index(COL["libro_estado"]) + 1
    for i, r in enumerate(registros, start=2):
        if str(r.get(COL["id"], "")).strip() == str(id_fila).strip():
            hoja.update_cell(i, col_libro, nuevo_estado)
            return True
    return False


# ---------------------------------------------------------------------------
# BLOG ALCHEMIST & VISUALIZER — módulos separados
# ---------------------------------------------------------------------------

def llamar_blog_alchemist(titulo: str, cuerpo_raw: str, ancla_verdad: str = "", enlace_amazon: str = "") -> str:
    """Invoca al Blog Alchemist para generar la Reseña de Acero.

    Pipeline completamente separado de alchemist.py (guiones YouTube).
    El ANCLA_VERDAD se inserta INTACTA — jamás se parafrasea.
    """
    try:
        from core.blog_alchemist import invocar_blog_alchemist
        return invocar_blog_alchemist(
            titulo=titulo,
            cuerpo_raw=cuerpo_raw,
            ancla_verdad=ancla_verdad,
            enlace_amazon=enlace_amazon,
        )
    except Exception as e:
        print(f"  ⚠️  Error en Blog Alchemist: {e}")
        print("  Usando texto en bruto sin transformar...")
        return cuerpo_raw


def llamar_blog_visualizer(titulo: str, contenido: str, slug: str) -> str:
    """Invoca al Blog Visualizer para diseñar y forjar la imagen de portada."""
    try:
        from core.blog_visualizer import crear_visual_blog
        # El visualizer usa el resumen (primeros 500 chars) para el prompt
        return crear_visual_blog(titulo, contenido[:500], slug)
    except Exception as e:
        print(f"  ⚠️  Error en Blog Visualizer: {e}")
        return ""


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
    if not desc:
        # Fallback desc: Strip Markdown headers and markdown bold syntax, take 150 chars
        clean_content = re.sub(r'#.*?\n', '', contenido_generado)
        clean_content = re.sub(r'\*\*(.*?)\*\*', r'\1', clean_content)
        clean_content = clean_content.replace('\n', ' ').strip()
        desc = clean_content[:150] + ("..." if len(clean_content) > 150 else "")

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
        msg = f"ID {id_especifico}" if id_especifico else "LIBRO_ESTADO = ancla_lista"
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
        ancla   = str(row.get(COL["ancla"], "")).strip()
        amazon  = str(row.get(COL["amazon"], "")).strip()

        print(f"{'─'*60}")
        print(f"📝 [{id_fila}] {titulo[:55]}...")

        if not titulo:
            print(f"  ❌ Sin título — saltando")
            fallidos += 1
            continue

        if not cuerpo:
            print(f"  ⚠️  Cuerpo_Raw vacío — generando esqueleto básico")
            cuerpo = f"Reseña de {titulo}. Tema: disciplina, identidad, forja del hombre."

        if ancla:
            print(f"  🗡️  Ancla del Soberano detectada ({len(ancla)} chars)")
        else:
            print(f"  ⚠️  Sin ANCLA_VERDAD — se generará sin Voz del Soberano")

        # Transformar con el Blog Alchemist (módulo separado)
        print(f"  🔧 Blog Alchemist procesando...")
        contenido = llamar_blog_alchemist(titulo, cuerpo, ancla, amazon)

        # Generar imagen con el Blog Visualizer (módulo separado)
        slug = row.get(COL["slug"], "").strip() or generar_slug(titulo)
        print(f"  🎨 Blog Visualizer forjando estética...")
        img_rel_path = llamar_blog_visualizer(titulo, contenido, slug)

        if img_rel_path:
            # Sincronizar el path de la imagen en el row para el .md
            row[COL["imagen"]] = img_rel_path

        # Generar .md
        ruta = generar_md(row, contenido, BLOG_OUTPUT_DIR, dry_run)

        if ruta:
            generados += 1
            if not dry_run:
                # Actualizar LIBRO_ESTADO a 'publicado'
                actualizar_libro_estado(hoja, id_fila, ESTADO_LISTO)
                print(f"  📊 LIBRO_ESTADO actualizado → {ESTADO_LISTO}")
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
