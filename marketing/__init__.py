"""
marketing — MiuraForge Marketing Toolkit
==========================================
Módulo de marketing adaptado del framework ai-marketing-claude.

Componentes:
- seo_auditor: Auditoría SEO de 4 pilares (técnico, on-page, contenido, doctrinal)
- copy_optimizer: Optimización de headlines, CTAs y meta descriptions (PAS/AIDA)
- funnel_engine: Análisis de embudo TOFU/MOFU/BOFU + generador de email sequences
- launch_playbook: Playbook de lanzamiento de 8 semanas + checklist
- social_calendar: Calendario de contenido 30 días (YouTube, IG, TikTok, Twitter)
- competitive_intel: Inteligencia competitiva — SWOT, gaps, tácticas robables
- landing_cro: Analizador CRO de landing pages (6 dimensiones)
- ad_creative: Generador de creativos para ads (FB, YT, IG, TT, TW)
- pdf_report: Generador de PDFs profesionales para reportes
- content_gap_analysis: Detector de gaps de contenido y oportunidades SEO
- email_sequence: Generador de secuencias de emails automatizados
- launch_timing: Calculadora de timing óptimo para lanzamientos

Stack: LLM Factory (NVIDIA Gemma 3, Mistral Large 3, DeepSeek V3.2)

NOTA: Imports lazy para evitar errores al ejecutar submódulos con `python -m`.
Usá import directo: `from marketing.social_calendar import generar_calendario`
"""

# Imports core (siempre disponibles)
from marketing.seo_auditor import auditar_post, auditar_todos
from marketing.copy_optimizer import optimizar_headline, auditar_cta, optimizar_meta
from marketing.funnel_engine import analizar_embudo, generar_emails
from marketing.launch_playbook import generar_playbook, mostrar_checklist


# Lazy imports para módulos nuevos (evita RuntimeWarning con python -m)
def __getattr__(name):
    if name in ("generar_calendario", "repurposar_guion", "exportar_sheets"):
        from marketing.social_calendar import (
            generar_calendario,
            repurposar_guion,
            exportar_sheets,
        )

        _map = {
            "generar_calendario": generar_calendario,
            "repurposar_guion": repurposar_guion,
            "exportar_sheets": exportar_sheets,
        }
        return _map[name]
    if name in ("analizar_competidores", "modo_auto"):
        from marketing.competitive_intel import analizar_competidores, modo_auto

        _map = {"analizar_competidores": analizar_competidores, "modo_auto": modo_auto}
        return _map[name]
    if name in ("analizar_landing", "generar_variantes"):
        from marketing.landing_cro import analizar_landing, generar_variantes

        _map = {"analizar_landing": analizar_landing, "generar_variantes": generar_variantes}
        return _map[name]
    if name == "generar_ad_creatives":
        from marketing.ad_creative import generar_ad_creatives

        return generar_ad_creatives
    if name in (
        "generar_pdf_seo",
        "generar_pdf_competitive",
        "generar_pdf_calendar",
        "generar_pdf_generico",
    ):
        from marketing.pdf_report import (
            generar_pdf_seo,
            generar_pdf_competitive,
            generar_pdf_calendar,
            generar_pdf_generico,
        )

        _map = {
            "generar_pdf_seo": generar_pdf_seo,
            "generar_pdf_competitive": generar_pdf_competitive,
            "generar_pdf_calendar": generar_pdf_calendar,
            "generar_pdf_generico": generar_pdf_generico,
        }
        return _map[name]
    # Content Gap Analysis
    if name in ("analizar_gaps", "analizar_competidores_gap", "generar_oportunidades"):
        from marketing.content_gap_analysis import (
            analizar_gaps,
            analizar_competidores as analizar_competidores_gap,
            generar_oportunidades,
        )

        _map = {
            "analizar_gaps": analizar_gaps,
            "analizar_competidores_gap": analizar_competidores_gap,
            "generar_oportunidades": generar_oportunidades,
        }
        return _map[name]
    # Email Sequence
    if name in ("generar_secuencia_email", "generar_asuntos_email", "exportar_secuencia_email"):
        from marketing.email_sequence import (
            generar_secuencia as generar_secuencia_email,
            generar_asuntos as generar_asuntos_email,
            exportar_secuencia as exportar_secuencia_email,
        )

        _map = {
            "generar_secuencia_email": generar_secuencia_email,
            "generar_asuntos_email": generar_asuntos_email,
            "exportar_secuencia_email": exportar_secuencia_email,
        }
        return _map[name]
    # Launch Timing
    if name in (
        "calcular_fecha_optima",
        "generar_cronograma_lanzamiento",
        "auditar_fecha_lanzamiento",
    ):
        from marketing.launch_timing import (
            calcular_fecha_optima,
            generar_cronograma as generar_cronograma_lanzamiento,
            auditar_fecha as auditar_fecha_lanzamiento,
        )

        _map = {
            "calcular_fecha_optima": calcular_fecha_optima,
            "generar_cronograma_lanzamiento": generar_cronograma_lanzamiento,
            "auditar_fecha_lanzamiento": auditar_fecha_lanzamiento,
        }
        return _map[name]
    raise AttributeError(f"module 'marketing' has no attribute '{name}'")


__all__ = [
    "auditar_post",
    "auditar_todos",
    "optimizar_headline",
    "auditar_cta",
    "optimizar_meta",
    "analizar_embudo",
    "generar_emails",
    "generar_playbook",
    "mostrar_checklist",
    "generar_calendario",
    "repurposar_guion",
    "exportar_sheets",
    "analizar_competidores",
    "modo_auto",
    "analizar_landing",
    "generar_variantes",
    "generar_ad_creatives",
    "generar_pdf_seo",
    "generar_pdf_competitive",
    "generar_pdf_calendar",
    "generar_pdf_generico",
    "analizar_gaps",
    "analizar_competidores_gap",
    "generar_oportunidades",
    "generar_secuencia_email",
    "generar_asuntos_email",
    "exportar_secuencia_email",
    "calcular_fecha_optima",
    "generar_cronograma_lanzamiento",
    "auditar_fecha_lanzamiento",
]
