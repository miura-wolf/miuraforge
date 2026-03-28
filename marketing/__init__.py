"""
marketing — MiuraForge Marketing Toolkit
==========================================
Módulo de marketing adaptado del framework ai-marketing-claude.

Componentes:
  - seo_auditor:     Auditoría SEO de 4 pilares (técnico, on-page, contenido, doctrinal)
  - copy_optimizer:  Optimización de headlines, CTAs y meta descriptions (PAS/AIDA)
  - funnel_engine:   Análisis de embudo TOFU/MOFU/BOFU + generador de email sequences
  - launch_playbook: Playbook de lanzamiento de 8 semanas + checklist

Stack: LLM Factory (NVIDIA Gemma 3, Mistral Large 3, DeepSeek V3.2)
"""

from marketing.seo_auditor import auditar_post, auditar_todos
from marketing.copy_optimizer import optimizar_headline, auditar_cta, optimizar_meta
from marketing.funnel_engine import analizar_embudo, generar_emails
from marketing.launch_playbook import generar_playbook, mostrar_checklist

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
]
