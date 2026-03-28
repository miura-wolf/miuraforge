"""
marketing/seo_auditor.py — MiuraForge Marketing Toolkit
=========================================================
Auditor SEO para posts del blog de Disciplina en Acero.

Evalúa cada artículo en 4 pilares (100 puntos):
  - SEO Técnico (25%): meta tags, slug, estructura URLs
  - SEO On-Page (30%): títulos, headings, keywords, imágenes
  - Estrategia de Contenido (25%): calidad, longitud, intención de búsqueda
  - Engagement Doctrinal (20%): tono Andrés, CTAs físicos, coherencia de marca

Uso:
  python -m marketing.seo_auditor --file path/to/post.md
  python -m marketing.seo_auditor --all   # audita todos los posts del blog
"""

import sys
import os
import re
import argparse
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

from llm.factory import LLMFactory

BLOG_DIR = Path(__file__).resolve().parent.parent / "disciplinaenacero" / "src" / "content" / "blog"

# ---------------------------------------------------------------------------
# PROMPT DEL AUDITOR SEO
# ---------------------------------------------------------------------------

PROMPT_SEO = """Eres el Auditor SEO de Disciplina en Acero.

Evaluá este artículo de blog usando el marco de puntuación de 4 pilares.
Puntuá cada categoría de 0 a 100 y calculá el promedio ponderado.

## PILARES DE EVALUACIÓN

### 1. SEO Técnico (25%)
- ¿Tiene frontmatter completo? (title, slug, date, description, keywords)
- ¿El slug es limpio y descriptivo?
- ¿La meta description tiene entre 120-160 caracteres?
- ¿Tiene keywords relevantes?

### 2. SEO On-Page (30%)
- ¿Hay un solo H1 implícito (el título)?
- ¿Los H2/H3 contienen keywords o variaciones?
- ¿La densidad de keywords es natural (1-3%)?
- ¿Hay alt text en imágenes (si las hay)?
- ¿El primer párrafo contiene la keyword principal?

### 3. Estrategia de Contenido (25%)
- ¿El contenido responde a una intención de búsqueda clara?
- ¿La longitud es adecuada (>600 palabras)?
- ¿Hay estructura lógica (problema → análisis → solución → CTA)?
- ¿El contenido es original y no genérico?

### 4. Engagement Doctrinal (20%)
- ¿Mantiene el tono Andrés (autoridad calmada, prensa hidráulica)?
- ¿Los CTAs son acciones físicas concretas (no "piensa" ni "considera")?
- ¿Conecta el libro reseñado con "El Hombre que Dejó de Mentirse"?
- ¿Usa metáforas del universo de marca (acero, forja, fragua, yunque)?

## FORMATO DE RESPUESTA

```
PUNTUACIÓN SEO — [TÍTULO DEL POST]
═══════════════════════════════════
SEO Técnico:        XX/100  [breve justificación]
SEO On-Page:        XX/100  [breve justificación]
Estrategia:         XX/100  [breve justificación]
Engagement:         XX/100  [breve justificación]
───────────────────────────────────
SCORE TOTAL:        XX/100
NIVEL:              [Excelente|Bueno|Promedio|Pobre]

ACCIONES PRIORITARIAS:
1. [acción concreta más urgente]
2. [segunda acción]
3. [tercera acción]
```

---

ARTÍCULO A AUDITAR:

{contenido}
"""


def auditar_post(filepath: Path) -> str:
    """Audita un post individual del blog."""
    contenido = filepath.read_text(encoding="utf-8")
    brain = LLMFactory.get_brain("deployer")  # Gemma 3 — SEO specialist
    prompt = PROMPT_SEO.format(contenido=contenido)
    return brain.generate(prompt)


def auditar_todos() -> dict:
    """Audita todos los posts del directorio de blog."""
    resultados = {}
    posts = list(BLOG_DIR.glob("*.md")) + list(BLOG_DIR.glob("*.mdx"))

    if not posts:
        print("⚠️  No hay posts en el directorio del blog.")
        return resultados

    for post in posts:
        print(f"🔍 Auditando: {post.name}...")
        try:
            resultado = auditar_post(post)
            resultados[post.name] = resultado
            print(resultado)
            print()
        except Exception as e:
            print(f"  ❌ Error auditando {post.name}: {e}")
            resultados[post.name] = f"ERROR: {e}"

    return resultados


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Auditor SEO — MiuraForge Marketing")
    parser.add_argument("--file", type=str, help="Ruta al archivo .md a auditar")
    parser.add_argument("--all", action="store_true", help="Auditar todos los posts del blog")
    args = parser.parse_args()

    if args.file:
        p = Path(args.file)
        if not p.exists():
            print(f"❌ Archivo no encontrado: {p}")
            sys.exit(1)
        print(f"🔍 Auditando: {p.name}")
        print(auditar_post(p))
    elif args.all:
        auditar_todos()
    else:
        print("Uso: python -m marketing.seo_auditor --file post.md | --all")
