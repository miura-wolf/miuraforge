"""
core/blog_alchemist.py — MiuraForgeEngine / Blog Alchemist
=============================================================
Módulo SEPARADO del Alchemist de guiones (core/alchemist.py).
Pipeline exclusivo para reseñas del blog de disciplinaenacero.com.

Basado en el Veredicto Global:
  - Cerebro: DeepSeek-V3.2 (profundidad analítica + puentes de conversión)
  - Estructura Híbrida: análisis DeepSeek + ritmo Mistral + dato concreto
  - Voz del Soberano: ANCLA_VERDAD insertada INTACTA (jamás parafrasear)
  - Blindaje de Funnel: cierre obligatorio con Amazon + transición + libro

NO comparte prompt ni lógica con alchemist.py (guiones de YouTube).
"""

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

from llm.factory import LLMFactory

# ---------------------------------------------------------------------------
# PROMPT: BLOG ALCHEMIST — Reseñas de Acero
# ---------------------------------------------------------------------------

PROMPT_BLOG_ALCHEMIST = """Eres el Blog Alchemist de Disciplina en Acero.

Tu misión: transformar el texto en bruto en una RESEÑA DE ACERO para el blog.
Esta reseña no es motivación. Es un DIAGNÓSTICO que lleva al lector
desde el libro reseñado hasta "El Hombre que Dejó de Mentirse".

══════════════════════════════════════════
DOCTRINA INQUEBRANTABLE
══════════════════════════════════════════

1. Tono: masculino, autoritario, filosófico de acción — AUTORIDAD CALMADA
2. NO consuelas, NO motivas con vacío, NO usas frases de coaching genérico
3. REVELAS el autoengaño, DIAGNOSTICAS el problema, ORDENAS la acción
4. El libro reseñado es el "sistema" (el qué). Tu libro es la "identidad" (el quién)
5. JAMÁS sugieras que el libro reseñado "complementa" o "se necesita junto" con tu libro
   → El libro reseñado es el MAPA. Tu libro es la BRÚJULA. Uno viene después del otro.
6. Metáforas: acero, forja, fragua, katana, yunque, vacío, presión, carbono, prensa hidráulica
7. Verbos PROHIBIDOS: "podrías", "quizás", "tal vez", "intenta", "considera", "reflexiona"
8. Verbos PERMITIDOS: "revela", "diagnostica", "ordena", "forja", "destruye", "instala", "desmonta"

══════════════════════════════════════════
BLINDAJE DE EMBUDO (NO NEGOCIABLE)
══════════════════════════════════════════

NUNCA invertir el embudo. El flujo es:
  Libro reseñado (sistema/herramienta) → Tu libro (identidad/transformación)

Si el lector concluye que necesita ambos libros "en paralelo", FALLASTE.
El lector debe concluir: "El sistema solo no alcanza. Necesito leer El Hombre que Dejó de Mentirse."

══════════════════════════════════════════
ESTRUCTURA OBLIGATORIA DEL ARTÍCULO
══════════════════════════════════════════

### APERTURA (2-3 párrafos)
- Primer párrafo: DATO CONCRETO (ventas, estadística, hecho verificable)
  que genere tensión inmediata. NO declaración filosófica abstracta.
  Ejemplo: "Atomic Habits vendió 15 millones de copias. Si el método
  funcionara por sí solo, habría 15 millones de hombres transformados."
- Segundo párrafo: el DIAGNÓSTICO — por qué ese dato revela un problema

### H2: "Lo que {titulo} te da — y lo que no"
- Estructura de DOS COLUMNAS mentales:
  Columna 1: Lo que el libro reseñado SÍ resuelve (reconocer mérito real)
  Columna 2: El punto ciego que el libro NO puede tocar (identidad, vacío)
- Incluir TRES PREGUNTAS RÍTMICAS en cursiva que diagnostiquen al lector:
  Ejemplo: *¿Cuántas veces instalaste un hábito que se desmoronó
  a los 21 días? ¿Cuántos sistemas perfectos abandonaste cuando
  dejó de ser novedad? ¿Cuántas mañanas a las 5 AM terminaron
  en el mismo vacío de las 11 PM?*

### H2: "El punto ciego del sistema"
- Análisis de la IDENTIDAD CORRUPTA como el agujero que ningún
  sistema tapa — esto es lo más original que debes escribir
- Metáforas del carbono-verdad: el hierro (hábito) necesita carbono
  (verdad) para convertirse en acero (identidad).
- En "El punto ciego del sistema", usa "forjado al quién" en lugar de "matado al quién" (SEO-Safe).

### H2: "Veredicto de acero"
- 2-3 párrafos de cierre contundente
- LA FRASE PUENTE (obligatoria): conectar ambos libros en una sola
  imagen. Ejemplo: "Este libro te da el hábito de levantarte a las
  5 AM — El Hombre que Dejó de Mentirse te da la razón inquebrantable
  para hacerlo."

{bloque_ancla}

### CTA FINAL (ESTRUCTURA RÍGIDA — NO MODIFICAR ORDEN)
1. **Enlace Amazon:** "Si aún no has leído {titulo}, empieza por ahí → [enlace]"
2. **Transición doctrinal:** Una línea que conecte: "Pero si ya lo leíste
   y el vacío sigue ahí, el sistema no era el problema."
3. **Enlace tu libro:** "Lee El Hombre que Dejó de Mentirse → [enlace]"

══════════════════════════════════════════
REGLAS FINALES
══════════════════════════════════════════
- LONGITUD: 700-1000 palabras. Cada palabra debe pesar.
- NO uses bullet points en el cuerpo (solo en la sección de columnas).
- Entrega SOLO el contenido en Markdown. Sin explicaciones ni comentarios.
- Comienza directamente con el primer párrafo (el dato concreto).

══════════════════════════════════════════
DATOS DEL ARTÍCULO
══════════════════════════════════════════

TÍTULO: {titulo}
ENLACE AMAZON DEL LIBRO RESEÑADO: {enlace_amazon}

TEXTO EN BRUTO (transforma esto):
{cuerpo_raw}
"""

# ---------------------------------------------------------------------------
# BLOQUE ANCLA — Voz del Soberano (se inserta INTACTO)
# ---------------------------------------------------------------------------

BLOQUE_ANCLA_TEMPLATE = """
### Voz del Soberano

> {ancla_verdad}

"""

BLOQUE_ANCLA_VACIO = ""  # Si no hay ancla, no se inserta nada


# ---------------------------------------------------------------------------
# FUNCIÓN PRINCIPAL
# ---------------------------------------------------------------------------

def invocar_blog_alchemist(
    titulo: str,
    cuerpo_raw: str,
    ancla_verdad: str = "",
    enlace_amazon: str = "",
) -> str:
    """
    Invoca al Blog Alchemist para generar una reseña de acero.

    Args:
        titulo:        Título del artículo/libro
        cuerpo_raw:    Texto en bruto a transformar
        ancla_verdad:  Frase del Soberano — se inserta INTACTA, sin parafrasear
        enlace_amazon: Enlace de afiliado de Amazon para el libro reseñado

    Returns:
        Contenido Markdown de la reseña generada
    """
    # Construir bloque ancla (intacto o vacío)
    if ancla_verdad and ancla_verdad.strip():
        bloque = BLOQUE_ANCLA_TEMPLATE.format(ancla_verdad=ancla_verdad.strip())
    else:
        bloque = BLOQUE_ANCLA_VACIO

    # Ensamblar prompt
    prompt = PROMPT_BLOG_ALCHEMIST.format(
        titulo=titulo,
        cuerpo_raw=cuerpo_raw,
        enlace_amazon=enlace_amazon or "[enlace pendiente]",
        bloque_ancla=bloque,
    )

    try:
        # DeepSeek V3.2 — el cerebro analítico (ganador del Veredicto Global)
        brain = LLMFactory.get_brain("research")
        resultado = brain.generate(prompt)

        # Post-procesado: verificar que el ANCLA se insertó intacta
        if ancla_verdad and ancla_verdad.strip():
            if ancla_verdad.strip() not in resultado:
                # El modelo no insertó el ancla — la inyectamos manualmente
                # antes del "Veredicto de acero"
                marcador = "### Veredicto de acero"
                if marcador in resultado:
                    resultado = resultado.replace(
                        marcador,
                        f"### Voz del Soberano\n\n> {ancla_verdad.strip()}\n\n{marcador}",
                    )
                else:
                    # Fallback: insertar al final antes del CTA
                    resultado += f"\n\n### Voz del Soberano\n\n> {ancla_verdad.strip()}\n"

        return resultado.strip()
    except Exception as e:
        print(f"  ⚠️  Error en Blog Alchemist: {e}")
        print("  Resiliencia actvada: Devolviendo cuerpo original.")
        return cuerpo_raw.strip()


# ---------------------------------------------------------------------------
# TEST DIRECTO
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("⚔️  Blog Alchemist — Test de humo")
    print("=" * 50)

    test_titulo = "Hábitos Atómicos: Prueba de Alchemist"
    test_cuerpo = (
        "Atomic Habits de James Clear habla de mejoras del 1% diario. "
        "Es un buen sistema pero no responde la pregunta de identidad."
    )
    test_ancla = (
        "Leí Atomic Habits en el peor momento de mi vida y apliqué "
        "cada sistema al pie de la letra. Los hábitos funcionaron. "
        "El vacío no desapareció."
    )

    resultado = invocar_blog_alchemist(
        titulo=test_titulo,
        cuerpo_raw=test_cuerpo,
        ancla_verdad=test_ancla,
        enlace_amazon="https://amazon.com/dp/EXAMPLE",
    )

    print(resultado)
