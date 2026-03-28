"""
marketing/funnel_engine.py — MiuraForge Marketing Toolkit
==========================================================
Motor de Embudo de Conversión para Disciplina en Acero.

Embudo doctrinal:
  TOFU → Blog/YouTube/Shorts (dolor identificado)
  MOFU → Lead Magnet "El Fundamento" (30 días) + Email sequences
  BOFU → Libro "El Hombre que Dejó de Mentirse" + Merch

Uso:
  python -m marketing.funnel_engine --analyze     # analiza estado actual del embudo
  python -m marketing.funnel_engine --plan         # genera plan de optimización
  python -m marketing.funnel_engine --emails TYPE  # genera secuencia de email (welcome|nurture|launch)
"""

import sys
import argparse
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

from llm.factory import LLMFactory

# ---------------------------------------------------------------------------
# DEFINICIÓN DEL EMBUDO DOCTRINAL
# ---------------------------------------------------------------------------

FUNNEL_DEFINITION = """
## EMBUDO DE CONVERSIÓN — DISCIPLINA EN ACERO

### TOFU (Top of Funnel) — Consciencia y Atracción
- **Canal principal:** YouTube (Shorts + largo formato)
- **Canal secundario:** Blog (reseñas de libros SEO-optimizadas)
- **Contenido:** Los 4 dolores masculinos (Silencio, Máscara, Vacío, Proveedor Invisible)
- **Métrica clave:** Vistas, impresiones, nuevos suscriptores
- **CTA:** "Si te reconoces aquí, empieza por el Fundamento"

### MOFU (Middle of Funnel) — Consideración y Educación
- **Lead Magnet:** "El Fundamento" (protocolo de 30 días, PDF gratuito)
- **Email sequence:** 5 correos de bienvenida (Brevo)
- **Contenido:** Protocolo estructurado, diagnóstico de identidad
- **Métrica clave:** Tasa de conversión del formulario, aperturas de email
- **CTA:** "30 días. Sin motivación vacía. Solo el protocolo."

### BOFU (Bottom of Funnel) — Conversión y Decisión
- **Producto principal:** Libro "El Hombre que Dejó de Mentirse" ($9 USD)
- **Producto secundario:** Merchandise (próximamente)
- **Ingresos afiliados:** Amazon links en reseñas del blog
- **Métrica clave:** Ventas, ingresos mensuales, CLV
- **CTA:** "Forja tu identidad → Lee El Hombre que Dejó de Mentirse"
"""

PROMPT_ANALYZE = """Eres el Estratega de Embudos de Disciplina en Acero.

Analizá el estado actual del embudo de conversión basándote en esta definición:

{funnel}

ACTIVOS ACTUALES:
- YouTube: Canal activo con Shorts sobre los 4 dolores masculinos
- Blog: En construcción (Astro + Netlify), primeras reseñas en proceso
- Lead Magnet: "El Fundamento" diseñado, formulario en landing page
- Email: Brevo configurado (tier gratuito, 300/día)
- Libro: Disponible digitalmente, precio $9 USD
- Merch: En diseño (próximamente)

GENERÁ:
1. Score actual de cada etapa (0-100)
2. Gap analysis: qué falta en cada etapa
3. Quick wins: 3 acciones que se pueden hacer ESTA SEMANA
4. Proyección: impacto estimado si se ejecutan los quick wins
"""

PROMPT_EMAILS = {
    "welcome": """Generá una secuencia de 5 correos de BIENVENIDA para Disciplina en Acero.

CONTEXTO:
- El usuario acaba de descargar "El Fundamento" (protocolo de 30 días)
- Tono: Andrés (autoridad calmada, prensa hidráulica, diagnóstico directo)
- NUNCA: coaching genérico, motivación vacía, "tú puedes", "sé tu mejor versión"
- SIEMPRE: diagnóstico preciso, acciones físicas, metáforas de acero/forja

ESTRUCTURA POR EMAIL:
- Asunto (máx 50 chars, generar tensión)
- Preview text (máx 90 chars)
- Cuerpo (200-300 palabras máximo)
- CTA (acción física concreta)
- P.S. (toque personal o urgencia)

CADENCIA: Día 0, Día 2, Día 5, Día 10, Día 15

EMAIL 1 (Día 0): Entrega del Fundamento + establecer expectativas
EMAIL 2 (Día 2): Primer dolor (Silencio) + primer ejercicio del protocolo
EMAIL 3 (Día 5): Segundo dolor (Máscara) + por qué la mayoría abandona
EMAIL 4 (Día 10): Checkpoint — ¿sigues o ya te mentiste de nuevo?
EMAIL 5 (Día 15): Puente al libro — el Fundamento es el mapa, el libro es la brújula
""",
    "nurture": """Generá una secuencia de 6 correos de NURTURE para leads que descargaron El Fundamento pero NO compraron el libro.

TONO: Andrés — sin presión de venta directa, pero con diagnóstico incómodo.
CADENCIA: Semanal (Día 21, 28, 35, 42, 49, 56 después de la suscripción)

Cada email debe:
1. Diagnosticar UN patrón específico de autoengaño
2. Dar UNA acción física concreta
3. Mencionar el libro solo como herramienta, no como venta

EMAIL 1: "El hombre que completó el protocolo pero no cambió nada"
EMAIL 2: "Lo que la constancia produce que la intensidad no puede"
EMAIL 3: "Por qué el silencio no es fortaleza"
EMAIL 4: "El costo real de la máscara"
EMAIL 5: "Vacío ≠ depresión — la diferencia que nadie te explicó"
EMAIL 6: "La última mentira: 'ya estoy bien'"
""",
    "launch": """Generá una secuencia de 8 correos de LANZAMIENTO para el libro "El Hombre que Dejó de Mentirse".

CONTEXTO:
- Precio: $9 USD (digital)
- Audiencia: hombres 25-45 que ya descargaron El Fundamento
- Tono: Andrés — urgencia legítima, no escasez artificial

CADENCIA:
- Día -7: Teaser — "Algo se está forjando"
- Día -3: Revelación — qué es y por qué existe
- Día -1: Víspera — "Mañana se abre la forja"
- Día 0 (AM): Lanzamiento — "Ya está disponible"
- Día 0 (PM): Recordatorio — "24 horas"
- Día +2: Social proof — testimonios/primeros lectores
- Día +5: Último empujón — "La forja cierra"
- Día +7: Cierre + transición a nurture
"""
}}


def analizar_embudo() -> str:
    brain = LLMFactory.get_brain("deployer")
    return brain.generate(PROMPT_ANALYZE.format(funnel=FUNNEL_DEFINITION))


def generar_emails(tipo: str) -> str:
    if tipo not in PROMPT_EMAILS:
        return f"❌ Tipo de secuencia no válido: {tipo}. Opciones: welcome, nurture, launch"
    brain = LLMFactory.get_brain("architect")  # Mistral — precisión narrativa
    return brain.generate(PROMPT_EMAILS[tipo])


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Funnel Engine — MiuraForge Marketing")
    parser.add_argument("--analyze", action="store_true", help="Analizar estado del embudo")
    parser.add_argument("--emails", type=str, choices=["welcome", "nurture", "launch"],
                        help="Generar secuencia de emails")
    args = parser.parse_args()

    if args.analyze:
        print("⚔️  Analizando embudo de conversión...\n")
        print(analizar_embudo())
    elif args.emails:
        print(f"⚔️  Generando secuencia de emails: {args.emails}...\n")
        print(generar_emails(args.emails))
    else:
        print("Uso: python -m marketing.funnel_engine --analyze | --emails [welcome|nurture|launch]")
