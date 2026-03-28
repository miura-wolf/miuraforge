#!/usr/bin/env python3
"""
⚔️ SEO AUDITOR - Miura Forge
Auditoría de contenido para blog y YouTube

Scoring: 0-100 en 6 dimensiones
"""

import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from llm.factory import LLMFactory
from typing import Dict, List


class SEOAuditor:
    """
    Audita contenido según scoring rubrics (0-100).
    Basado en metodología ai-marketing-claude adaptada.
    """

    # Pesos de cada dimensión
    DIMENSIONES = {
        "content_messaging": 0.25,  # 25%
        "conversion": 0.20,  # 20%
        "seo_discoverability": 0.20,  # 20%
        "competitive": 0.15,  # 15%
        "brand_trust": 0.10,  # 10%
        "growth": 0.10,  # 10%
    }

    def __init__(self):
        self.brain = LLMFactory.get_brain("marketing")

    def auditar_post_blog(self, titulo: str, contenido: str, keywords: List[str]) -> Dict:
        """
        Audita un post del blog.

        Args:
            titulo: Título del post
            contenido: Cuerpo del post
            keywords: Lista de keywords objetivo

        Returns:
            dict con scores y recomendaciones
        """

        prompt = f"""Actúa como auditor SEO especializado en contenido masculino.

Contenido a auditar:
Título: {titulo}
Keywords: {", ".join(keywords)}

Texto:
{contenido[:2000]}...

DIMENSIONES A EVALUAR (0-100 cada una):

1. Content & Messaging (25%):
   - Headline atractivo?
   - Value prop clara?
   - Copy alineado doctrina?
   - CTAs con acciones físicas?

2. Conversion Optimization (20%):
   - Lead capture visible?
   - Links afiliados presentes?
   - Social proof (testimonios)?
   - Friction mínimo?

3. SEO & Discoverability (20%):
   - Keywords en H1, H2?
   - Meta description?
   - Structure semántica?
   - Internal links?

4. Competitive Positioning (15%):
   - Diferenciación clara?
   - Propuesta única?
   - Contra quien compite?

5. Brand & Trust (10%):
   - Tono consistente?
   - Autoridad demostrada?
   - Design quality?

6. Growth & Strategy (10%):
   - Shareable content?
   - Next steps claros?
   - CTAs múltiples?

OUTPUT FORMATO:
Dimension: Score/100 - Brief explanation

Overall Score: [weighted average]

Top 3 Fixes:
1. [priority fix]
2. [priority fix]
3. [priority fix]
"""

        respuesta = self.brain.generate(prompt)

        # Parsear respuesta (simplificado)
        return {
            "titulo": titulo,
            "raw_analysis": respuesta,
            "dimensiones": self.DIMENSIONES,
            "keywords": keywords,
        }

    def generar_meta_tags(self, titulo: str, contenido: str) -> Dict:
        """Genera meta tags optimizados."""

        prompt = f"""Genera meta tags SEO para:

Título: {titulo}

Contenido:
{contenido[:500]}

OUTPUT:
Title: (max 60 chars)
Description: (max 160 chars)
Keywords: (5-7 relevantes)
"""

        respuesta = self.brain.generate(prompt)

        return {"titulo": titulo, "meta_tags": respuesta}

    def sugerir_keywords(self, tema: str) -> List[str]:
        """Sugiere keywords para un tema."""

        prompt = f"""Sugiere 10 keywords para el tema: "{tema}"

Criterios:
- Relevancia para hombres 25-45 años
- Intención de búsqueda: problemas de procrastinación, disciplina, autoengaño
- Mix: head terms (alta competencia) + long-tail (baja competencia)

OUTPUT: Lista numerada
"""

        respuesta = self.brain.generate(prompt)

        # Parsear lista
        keywords = [
            line.strip().split(". ")[1] for line in respuesta.strip().split("\n") if "." in line
        ]

        return keywords[:10]


if __name__ == "__main__":
    auditor = SEOAuditor()

    # Test
    keywords = auditor.sugerir_keywords("procrastinación masculina")
    print("Keywords sugeridas:")
    for kw in keywords:
        print(f"  - {kw}")
