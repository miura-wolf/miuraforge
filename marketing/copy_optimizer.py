"""
marketing/copy_optimizer.py — MiuraForge Marketing Toolkit
============================================================
Optimizador de Copy para headlines, CTAs y meta descriptions.

Frameworks implementados:
  - PAS (Problema → Agitación → Solución) — alineado con doctrina Andrés
  - AIDA (Atención → Interés → Deseo → Acción)
  - Scoring de CTAs (verifica que sean acciones físicas concretas)

Uso:
  python -m marketing.copy_optimizer --headline "Tu título aquí"
  python -m marketing.copy_optimizer --cta "Tu CTA aquí"
  python -m marketing.copy_optimizer --meta "Tu meta description aquí"
"""

import sys
import argparse
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

from llm.factory import LLMFactory

# ---------------------------------------------------------------------------
# PROMPTS DOCTRINALES
# ---------------------------------------------------------------------------

PROMPT_HEADLINE = """Eres el Estratega de Copy de Disciplina en Acero.

Analizá este headline y generá 5 alternativas optimizadas.

REGLAS DOCTRINALES:
1. Tono: masculino, autoritario, filosófico de acción
2. NO uses frases de coaching genérico ("descubre tu potencial", "sé tu mejor versión")
3. Verbos PROHIBIDOS: "podrías", "quizás", "tal vez", "intenta", "considera"
4. Verbos PERMITIDOS: "revela", "diagnostica", "ordena", "forja", "destruye", "instala"
5. Cada headline debe generar TENSIÓN (no curiosidad vacía)
6. Máximo 70 caracteres para SEO

FRAMEWORKS A APLICAR:
- PAS: Problema → Agitación → Solución
- Número + Beneficio Concreto
- Pregunta provocadora que duele

HEADLINE ORIGINAL: {headline}

FORMATO DE RESPUESTA:
1. [headline alternativo] — Framework: [PAS/Número/Pregunta] — Chars: XX
2. [headline alternativo] — Framework: [PAS/Número/Pregunta] — Chars: XX
3. [headline alternativo] — Framework: [PAS/Número/Pregunta] — Chars: XX
4. [headline alternativo] — Framework: [PAS/Número/Pregunta] — Chars: XX
5. [headline alternativo] — Framework: [PAS/Número/Pregunta] — Chars: XX

RECOMENDACIÓN: [cuál es el mejor y por qué]
"""

PROMPT_CTA = """Eres el Auditor de CTAs de Disciplina en Acero.

Evaluá este CTA y generá 3 alternativas que sean ACCIONES FÍSICAS CONCRETAS.

REGLAS:
- El CTA debe comenzar con un VERBO FÍSICO (abre, escribe, bloquea, elimina, levanta)
- NUNCA: "piensa", "considera", "evalúa", "planea", "reflexiona"
- Debe generar URGENCIA sin ser spam
- Máximo 50 caracteres

CTA ORIGINAL: {cta}

FORMATO:
ANÁLISIS: [por qué funciona o no funciona el CTA original]
SCORE: XX/100

ALTERNATIVAS:
1. [CTA mejorado] — Verbo físico: [sí/no] — Urgencia: [alta/media/baja]
2. [CTA mejorado] — Verbo físico: [sí/no] — Urgencia: [alta/media/baja]
3. [CTA mejorado] — Verbo físico: [sí/no] — Urgencia: [alta/media/baja]
"""

PROMPT_META = """Eres el Optimizador de Meta Descriptions de Disciplina en Acero.

Analizá esta meta description y generá 3 alternativas optimizadas para CTR.

REGLAS:
- Entre 120-160 caracteres (Google trunca después de 160)
- Debe incluir la keyword principal
- Debe generar TENSIÓN / curiosidad genuina (no clickbait vacío)
- Tono Andrés: autoridad calmada, diagnóstico directo

META ORIGINAL: {meta}

FORMATO:
ANÁLISIS: [longitud actual, keyword presente, efectividad estimada]

ALTERNATIVAS:
1. [meta optimizada] — Chars: XX — Keyword: [presente/ausente]
2. [meta optimizada] — Chars: XX — Keyword: [presente/ausente]
3. [meta optimizada] — Chars: XX — Keyword: [presente/ausente]
"""


def optimizar_headline(headline: str) -> str:
    brain = LLMFactory.get_brain("deployer")
    return brain.generate(PROMPT_HEADLINE.format(headline=headline))


def auditar_cta(cta: str) -> str:
    brain = LLMFactory.get_brain("auditor")
    return brain.generate(PROMPT_CTA.format(cta=cta))


def optimizar_meta(meta: str) -> str:
    brain = LLMFactory.get_brain("deployer")
    return brain.generate(PROMPT_META.format(meta=meta))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Copy Optimizer — MiuraForge Marketing")
    parser.add_argument("--headline", type=str, help="Headline a optimizar")
    parser.add_argument("--cta", type=str, help="CTA a auditar")
    parser.add_argument("--meta", type=str, help="Meta description a optimizar")
    args = parser.parse_args()

    if args.headline:
        print("⚔️  Optimizando headline...\n")
        print(optimizar_headline(args.headline))
    elif args.cta:
        print("⚔️  Auditando CTA...\n")
        print(auditar_cta(args.cta))
    elif args.meta:
        print("⚔️  Optimizando meta description...\n")
        print(optimizar_meta(args.meta))
    else:
        print("Uso: python -m marketing.copy_optimizer --headline|--cta|--meta 'texto'")
