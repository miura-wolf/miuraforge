"""
marketing/launch_playbook.py — MiuraForge Marketing Toolkit
=============================================================
Generador de Playbooks de Lanzamiento para productos de Disciplina en Acero.

Timeline de 8 semanas:
  Semana -8: Estrategia y métricas
  Semana -4: Creación de contenido y preparación técnica
  Semana -1: Calentamiento de audiencia
  Día 0:     Ejecución táctica
  Post:      Retención y análisis

Uso:
  python -m marketing.launch_playbook --product "El Hombre que Dejó de Mentirse"
  python -m marketing.launch_playbook --checklist
"""

import sys
import argparse
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

from llm.factory import LLMFactory

PROMPT_PLAYBOOK = """Eres el Director de Lanzamientos de Disciplina en Acero.

Creá un playbook de lanzamiento detallado para: {producto}

CONTEXTO DE MARCA:
- Marca: Disciplina en Acero
- Audiencia: Hombres 25-45, hispanohablantes
- Tono: Andrés (autoridad calmada, prensa hidráulica)
- Canales activos: YouTube, Blog (Astro/Netlify), Email (Brevo), Instagram
- Presupuesto: $0 (orgánico primero)

ESTRUCTURA DEL PLAYBOOK (8 semanas):

## FASE 1: Estrategia (Semana -8 a -5)
- Definir objetivos SMART (ventas, leads, engagement)
- Identificar los 3 mensajes clave del lanzamiento
- Crear buyer persona específica para este producto
- Definir KPIs y umbrales de éxito/fracaso

## FASE 2: Preparación (Semana -4 a -2)
- Landing page optimizada (Astro)
- Secuencia de emails pre-lanzamiento (8 correos)
- 10 posts de calentamiento para redes
- 3 videos teaser para YouTube/Shorts
- Blog posts de soporte SEO

## FASE 3: Calentamiento (Semana -1)
- Calendario diario de publicaciones
- Email teaser a la lista existente
- Activación de embajadores/lectores tempranos
- Preparación de respuestas para objeciones comunes

## FASE 4: Lanzamiento (Día 0)
- Timeline hora por hora
- Secuencia de publicaciones en todas las plataformas
- Email de lanzamiento
- Monitoreo en tiempo real

## FASE 5: Post-Lanzamiento (Semana +1 a +2)
- Recolección de testimonios
- Análisis de KPIs vs metas
- Ajustes de copy basados en datos
- Plan de retención y siguiente producto

Entregá el playbook completo en formato Markdown con fechas relativas.
"""

LAUNCH_CHECKLIST = """
# ✅ CHECKLIST DE LANZAMIENTO — DISCIPLINA EN ACERO

## 8 Semanas Antes
- [ ] Definir objetivos de ingresos (meta, mínimo, stretch)
- [ ] Crear buyer persona del producto
- [ ] Definir los 3 mensajes clave
- [ ] Establecer KPIs y dashboard de seguimiento

## 4 Semanas Antes
- [ ] Landing page construida y publicada
- [ ] Secuencia de emails escrita (8 correos en Brevo)
- [ ] 10 posts de calentamiento programados
- [ ] 3 videos teaser grabados/generados
- [ ] 2 blog posts de soporte SEO publicados
- [ ] Links de afiliados configurados (Amazon)

## 1 Semana Antes
- [ ] Email teaser enviado a la lista
- [ ] Posts diarios programados para la semana
- [ ] FAQ de objeciones preparada
- [ ] Página de pago testeada (PayPal/Stripe)
- [ ] Build hook de Netlify verificado

## Día del Lanzamiento
- [ ] Email de lanzamiento enviado (AM)
- [ ] Post en YouTube publicado
- [ ] Stories/Reels publicados
- [ ] Blog post de lanzamiento publicado
- [ ] Recordatorio email (PM)
- [ ] Monitoreo de métricas cada 2 horas

## Post-Lanzamiento (+7 días)
- [ ] Recopilar 5+ testimonios
- [ ] Análisis de KPIs vs metas
- [ ] Email de seguimiento a no-compradores
- [ ] Planear retención (contenido exclusivo)
- [ ] Documentar aprendizajes para próximo lanzamiento
"""


def generar_playbook(producto: str) -> str:
    brain = LLMFactory.get_brain("architect")
    return brain.generate(PROMPT_PLAYBOOK.format(producto=producto))


def mostrar_checklist():
    print(LAUNCH_CHECKLIST)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Launch Playbook — MiuraForge Marketing")
    parser.add_argument("--product", type=str, help="Producto para generar el playbook")
    parser.add_argument("--checklist", action="store_true", help="Mostrar checklist de lanzamiento")
    args = parser.parse_args()

    if args.product:
        print(f"⚔️  Generando playbook de lanzamiento para: {args.product}\n")
        print(generar_playbook(args.product))
    elif args.checklist:
        mostrar_checklist()
    else:
        print("Uso: python -m marketing.launch_playbook --product 'Nombre' | --checklist")
