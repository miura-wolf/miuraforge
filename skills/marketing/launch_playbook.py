#!/usr/bin/env python3
"""
⚔️ LAUNCH PLAYBOOK - Miura Forge
Sistema de lanzamientos para ebooks y productos

Basado en: Docs/estrategia_venta.txt
"""

import os
import sys
from datetime import datetime, timedelta

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from llm.factory import LLMFactory
from core.database import Database


class LaunchPlaybook:
    """
    Gestiona lanzamientos de productos digitales.

    Estructura de lanzamiento:
    - Fase 1: Pre-launch (calentamiento)
    - Fase 2: Lanzamiento ($9 + bonus)
    - Fase 3: Estable ($17)
    - Fase 4: Bundle (Libro + Protocolo $27)
    """

    def __init__(self):
        self.brain = LLMFactory.get_brain("marketing")
        self.db = Database()

        # Precios según estrategia_venta.txt
        self.PRECIO_LANZAMIENTO = 9
        self.PRECIO_ESTABLE = 17
        self.PRECIO_PROTOCOLO = 17
        self.PRECIO_BUNDLE = 27

    def crear_launch_calendar(self, producto: str, fecha_inicio: str) -> dict:
        """
        Crea calendario de lanzamiento de 30 días.

        Args:
            producto: Nombre del producto (ej: "El Hombre que Dejó de Mentirse")
            fecha_inicio: Fecha de inicio (YYYY-MM-DD)

        Returns:
            dict con fases y acciones
        """

        inicio = datetime.strptime(fecha_inicio, "%Y-%m-%d")

        calendario = {"producto": producto, "fecha_inicio": fecha_inicio, "fases": []}

        # Fase 1: Pre-launch (Días -14 a -1)
        calendario["fases"].append(
            {
                "nombre": "Pre-launch",
                "dias": f"Día -14 a Día -1",
                "fechas": {
                    "inicio": (inicio - timedelta(days=14)).strftime("%Y-%m-%d"),
                    "fin": (inicio - timedelta(days=1)).strftime("%Y-%m-%d"),
                },
                "objetivo": "Calentar audiencia, generar expectativa",
                "acciones": [
                    "3-5 shorts teasers (sin decir qué es)",
                    "Historia personal de por qué escribiste el libro",
                    "Encuesta: '¿Te cuesta mantener disciplina?'",
                    "Conteo regresivo en stories",
                ],
                "contenido": "Misterio + curiosidad",
            }
        )

        # Fase 2: Lanzamiento (Semana 1)
        calendario["fases"].append(
            {
                "nombre": "Lanzamiento",
                "dias": "Día 1 a Día 7",
                "fechas": {
                    "inicio": fecha_inicio,
                    "fin": (inicio + timedelta(days=6)).strftime("%Y-%m-%d"),
                },
                "objetivo": "Maximizar ventas semana 1",
                "precio": f"${self.PRECIO_LANZAMIENTO} USD + bonus",
                "bonus": "Checklist '5 síntomas del hombre en el yunque'",
                "acciones": [
                    "Short de anuncio (Hook agresivo)",
                    "Email a lista (Brevo)",
                    "Stories 3x/día con CTA",
                    "Respondiendo preguntas",
                    "Testimonios tempranos",
                ],
                "contenido": "Urgencia + escasez temporal",
            }
        )

        # Fase 3: Precio estable (Después semana 1)
        calendario["fases"].append(
            {
                "nombre": "Estable",
                "dias": "Día 8 en adelante",
                "fechas": {
                    "inicio": (inicio + timedelta(days=7)).strftime("%Y-%m-%d"),
                    "fin": "Continuo",
                },
                "objetivo": "Ventas orgánicas continuas",
                "precio": f"${self.PRECIO_ESTABLE} USD",
                "bonus": "Ninguno",
                "acciones": [
                    "1-2 shorts/semana mencionando libro",
                    "Email nurture mensual",
                    "Actualizar landing con testimonios",
                    "SEO orgánico",
                ],
                "contenido": "Valor demostrado + social proof",
            }
        )

        # Fase 4: Bundle (Cuando Protocolo esté listo)
        calendario["fases"].append(
            {
                "nombre": "Bundle",
                "dias": "Cuando Protocolo 30D esté listo",
                "fechas": {"inicio": "TBD", "fin": "Continuo"},
                "objetivo": "Aumentar ticket promedio",
                "precio": f"Libro ${self.PRECIO_ESTABLE} | Protocolo ${self.PRECIO_PROTOCOLO} | Bundle ${self.PRECIO_BUNDLE}",
                "estrategia": "Bundle $27 hace que la decisión sea obvia",
                "acciones": [
                    "Anuncio bundle",
                    "Comparativa de precios",
                    "Email a compradores actuales",
                    "Upsell en thank you page",
                ],
                "contenido": "Lógica matemática del bundle",
            }
        )

        return calendario

    def generar_contenido_launch(self, fase: str, producto: str) -> dict:
        """
        Genera contenido específico para cada fase del launch.

        Args:
            fase: "pre-launch", "launch", "estable", "bundle"
            producto: Nombre del producto

        Returns:
            dict con scripts, copy, emails
        """

        if fase == "launch":
            prompt = f"""Actúa como copywriter de Disciplina en Acero.

Producto: {producto}
Precio lanzamiento: ${self.PRECIO_LANZAMIENTO} USD
Bonus: Checklist "5 síntomas del hombre en el yunque"

Genera:
1. Anuncio Short (30s) - Hook + CTA
2. Email lanzamiento (asunto + cuerpo)
3. 3 ideas de Stories
4. Copy landing page (headline + bullets)

TONO: Urgencia legítima, sin escasez falsa.
"""

            contenido = self.brain.generate(prompt)

            return {"fase": fase, "producto": producto, "contenido_generado": contenido}

        elif fase == "estable":
            # Contenido evergreen
            return {
                "fase": fase,
                "tipo": "evergreen",
                "estrategia": "Mencionar libro en shorts + CTA link",
            }

        return {"fase": fase, "status": "not implemented"}

    def calcular_metricas_launch(self, ventas_semana1: int, precio_promedio: float) -> dict:
        """
        Calcula métricas post-lanzamiento.

        Args:
            ventas_semana1: Cantidad de ventas
            precio_promedio: Precio promedio (considerando $9 y $17)

        Returns:
            dict con métricas
        """

        ingreso_total = ventas_semana1 * precio_promedio

        # Proyección mensual
        if ventas_semana1 >= 50:
            proyeccion_mensual = ventas_semana1 * 4  # Optimista
        elif ventas_semana1 >= 20:
            proyeccion_mensual = ventas_semana1 * 3
        else:
            proyeccion_mensual = ventas_semana1 * 2  # Conservador

        return {
            "ventas_semana1": ventas_semana1,
            "precio_promedio": precio_promedio,
            "ingreso_total": ingreso_total,
            "proyeccion_mensual": proyeccion_mensual,
            "ingreso_proyectado": proyeccion_mensual * precio_promedio,
            "status": "EXITOSO" if ventas_semana1 >= 20 else "NECESITA AJUSTES",
        }


if __name__ == "__main__":
    playbook = LaunchPlaybook()

    # Crear calendario para lanzamiento
    calendario = playbook.crear_launch_calendar(
        producto="El Hombre que Dejó de Mentirse", fecha_inicio="2026-04-15"
    )

    print("=" * 60)
    print("LAUNCH CALENDAR")
    print("=" * 60)
    print(f"Producto: {calendario['producto']}")
    print(f"Inicio: {calendario['fecha_inicio']}")
    print()

    for fase in calendario["fases"]:
        print(f"\n⚔️ {fase['nombre'].upper()}")
        print(f"   Periodo: {fase['dias']}")
        print(f"   Precio: {fase.get('precio', 'N/A')}")
        print(f"   Objetivo: {fase['objetivo']}")
        print(f"   Acciones: {len(fase['acciones'])} tareas")
