#!/usr/bin/env python3
"""
⚔️ EMAIL SEQUENCES - Miura Forge
Secuencias de email para funnel de ventas

Funnel: Lead → Diagnóstico Gratis → Ebook ($9/$17) → Protocolo 30D ($17) → Bundle ($27)
"""

import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from datetime import datetime, timedelta
from llm.factory import LLMFactory
from core.database import Database


class EmailSequences:
    """
    Genera secuencias de email para el funnel de ventas.
    Integrado con LLMFactory (NVIDIA + Gemini) y Google Sheets.
    """

    def __init__(self):
        self.brain = LLMFactory.get_brain("emissary")
        self.db = Database()

        # Configuración según estrategia_venta.txt
        self.PRECIO_LANZAMIENTO = 9
        self.PRECIO_ESTABLE = 17
        self.PRECIO_PROTOCOLO = 17
        self.PRECIO_BUNDLE = 27

    def generar_secuencia_welcome(self, lead_email: str, nombre: str = "") -> dict:
        """
        Día 0: Email de bienvenida + entrega diagnóstico gratuito.

        Args:
            lead_email: Email del lead
            nombre: Nombre del lead (opcional)

        Returns:
            dict con asunto, cuerpo, metadata
        """

        prompt = f"""Actúa como Andrés, autoridad de Disciplina en Acero.

Contexto: Email de bienvenida a nuevo lead.

Datos:
- Nombre: {nombre if nombre else "Hombre"}
- Lead magnet: Diagnóstico gratuito "Los 5 síntomas del autoengaño"
- Oferta: Ebook "El Hombre que Dejó de Mentirse" a ${self.PRECIO_LANZAMIENTO}

ESTRUCTURA:
1. Asunto corto y provocador (máx 50 caracteres)
2. Saludo directo
3. Entrega del diagnóstico con link
4. Advertencia: "esto va a doler"
5. CTA a ebook pagado
6. Firma "Andrés"

TONO: Autoridad, sin motivación vacía. Revela, diagnostica, ordena.

OUTPUT: Solo el email completo, sin explicaciones.
"""

        contenido = self.brain.generate(prompt)

        # Parsear asunto y cuerpo
        lineas = contenido.strip().split("\n")
        asunto = lineas[0].replace("Asunto:", "").strip()
        cuerpo = "\n".join(lineas[1:]).strip()

        return {
            "tipo": "welcome",
            "asunto": asunto,
            "cuerpo": cuerpo,
            "destinatario": lead_email,
            "fecha_envio": datetime.now(),
            "precio_mencionado": self.PRECIO_LANZAMIENTO,
        }

    def generar_secuencia_nurture(self, lead_email: str) -> list[dict]:
        """
        Días 1-6: Secuencia de nurture para convertir lead en comprador.

        Returns:
            list de 6 emails (uno por día)
        """

        emails = []

        # Definir los 6 emails según DOCTRINA_MARKETING.md
        temas = [
            {
                "dia": 1,
                "tema": "El problema no es la falta de tiempo",
                "cta": "Leer diagnóstico",
                "objetivo": "engagement",
            },
            {
                "dia": 2,
                "tema": "Por qué la motivación te está matando",
                "cta": "Ver video",
                "objetivo": "educar",
            },
            {
                "dia": 3,
                "tema": "Caso: De 0 a 100 en 30 días",
                "cta": f"Comprar ebook (${self.PRECIO_LANZAMIENTO})",
                "objetivo": "vender",
            },
            {
                "dia": 4,
                "tema": "La mentira del 'cuando esté listo'",
                "cta": "Leer capítulo gratis",
                "objetivo": "probar",
            },
            {
                "dia": 5,
                "tema": "Ejercicio: 2 minutos de verdad",
                "cta": "Descargar worksheet",
                "objetivo": "ejercicio",
            },
            {
                "dia": 6,
                "tema": "¿Por qué fallaste antes? (y cómo evitarlo)",
                "cta": f"Comprar ebook (${self.PRECIO_LANZAMIENTO})",
                "objetivo": "vender_urgencia",
            },
        ]

        for i, config in enumerate(temas, 1):
            prompt = f"""Actúa como Andrés, autoridad de Disciplina en Acero.

Contexto: Email {i} de secuencia nurture (día {config["dia"]}).

Tema: {config["tema"]}
CTA: {config["cta"]}
Objetivo: {config["objetivo"]}

ESTRUCTURA:
1. Asunto que genere curiosidad (máx 60 caracteres)
2. 2-3 párrafos de contenido
3. CTA claro al final
4. Firma "Andrés"

TONO: Revelar el mecanismo del autoengaño. Sin motivación.

OUTPUT: Solo el email, sin explicaciones.
"""

            contenido = self.brain.generate(prompt)
            lineas = contenido.strip().split("\n")
            asunto = lineas[0].replace("Asunto:", "").strip()
            cuerpo = "\n".join(lineas[1:]).strip()

            email = {
                "tipo": f"nurture_dia_{config['dia']}",
                "asunto": asunto,
                "cuerpo": cuerpo,
                "destinatario": lead_email,
                "fecha_envio": datetime.now() + timedelta(days=config["dia"]),
                "objetivo": config["objetivo"],
            }

            emails.append(email)

        return emails

    def generar_secuencia_post_compra(self, comprador_email: str, nombre: str = "") -> list[dict]:
        """
        Post-compra: Entrega ebook + upsell Protocolo 30D.

        Funnel: Ebook ($9) → Protocolo 30D ($17) → Bundle ($27)

        Returns:
            list de 3 emails (inmediato, día 3, día 7)
        """

        emails = []

        # Email 1: Inmediato (entrega + upsell Protocolo)
        prompt_1 = f"""Actúa como Andrés, autoridad de Disciplina en Acero.

Contexto: Email inmediato post-compra del ebook.

Datos:
- Producto comprado: Ebook "El Hombre que Dejó de Mentirse" (${self.PRECIO_LANZAMIENTO})
- Upsell: Protocolo 30D (${self.PRECIO_PROTOCOLO})
- Bundle: Libro + Protocolo (${self.PRECIO_BUNDLE})

ESTRUCTURA:
1. Asunto: "Acá está tu libro. Y una pregunta incómoda."
2. Link de descarga del ebook
3. Instrucción: "Lee el capítulo 3 primero"
4. Pregta incómoda sobre ejecución
5. Oferta del Protocolo 30D (${self.PRECIO_PROTOCOLO})
6. Opción Bundle (${self.PRECIO_BUNDLE})
7. Firma "Andrés"

TONO: Autoridad, confrontación quirúrgica. Sin disculpas.

OUTPUT: Solo el email completo.
"""

        contenido_1 = self.brain.generate(prompt_1)
        lineas = contenido_1.strip().split("\n")
        asunto_1 = lineas[0].replace("Asunto:", "").strip()
        cuerpo_1 = "\n".join(lineas[1:]).strip()

        emails.append(
            {
                "tipo": "post_compra_inmediato",
                "asunto": asunto_1,
                "cuerpo": cuerpo_1,
                "destinatario": comprador_email,
                "fecha_envio": datetime.now(),
                "upsell": f"Protocolo 30D ${self.PRECIO_PROTOCOLO}",
            }
        )

        # Email 2: Día 3 (recordatorio Protocolo)
        prompt_2 = f"""Actúa como Andrés.

Contexto: Email día 3 post-compra.

Datos:
- Ya compró ebook
- No ha comprado Protocolo 30D aún
- Precio Protocolo: ${self.PRECIO_PROTOCOLO}

ESTRUCTURA:
1. Asunto provocador sobre acción
2. Recordatorio del Protocolo
3. Caso breve de quien ejecutó vs quien no
4. CTA al Protocolo
5. Firma "Andrés"

TONO: Sin presión, pero sin disculpas.

OUTPUT: Solo el email.
"""

        contenido_2 = self.brain.generate(prompt_2)
        lineas_2 = contenido_2.strip().split("\n")
        asunto_2 = lineas_2[0].replace("Asunto:", "").strip()
        cuerpo_2 = "\n".join(lineas_2[1:]).strip()

        emails.append(
            {
                "tipo": "post_compra_dia_3",
                "asunto": asunto_2,
                "cuerpo": cuerpo_2,
                "destinatario": comprador_email,
                "fecha_envio": datetime.now() + timedelta(days=3),
                "upsell": f"Protocolo 30D ${self.PRECIO_PROTOCOLO}",
            }
        )

        # Email 3: Día 7 (último intento Protocolo)
        prompt_3 = f"""Actúa como Andrés.

Contexto: Email día 7 post-compra (último intento upsell).

Datos:
- No compró Protocolo aún
- Precio sube mañana a ${self.PRECIO_ESTABLE}
- Urgencia real

ESTRUCTURA:
1. Asunto con urgencia
2. "Mañana el precio sube"
3. Última oportunidad Protocolo
4. CTA claro
5. Firma "Andrés"

TONO: Urgencia legítima, no escasez falsa.

OUTPUT: Solo el email.
"""

        contenido_3 = self.brain.generate(prompt_3)
        lineas_3 = contenido_3.strip().split("\n")
        asunto_3 = lineas_3[0].replace("Asunto:", "").strip()
        cuerpo_3 = "\n".join(lineas_3[1:]).strip()

        emails.append(
            {
                "tipo": "post_compra_dia_7",
                "asunto": asunto_3,
                "cuerpo": cuerpo_3,
                "destinatario": comprador_email,
                "fecha_envio": datetime.now() + timedelta(days=7),
                "upsell": f"Protocolo 30D ${self.PRECIO_PROTOCOLO} (último día)",
            }
        )

        return emails

    def guardar_email_sheets(self, email_data: dict) -> bool:
        """
        Guarda email generado en Google Sheets para tracking.

        Args:
            email_data: dict con datos del email

        Returns:
            bool: Éxito de la operación
        """
        try:
            # Crear pestaña EMAILS si no existe
            # Por ahora solo imprimir
            print(f"📧 [EmailSequences] Guardado: {email_data['asunto']}")
            return True
        except Exception as e:
            print(f"❌ [EmailSequences] Error guardando: {e}")
            return False

    def generar_funnel_completo(self, lead_email: str, nombre: str = "") -> dict:
        """
        Genera funnel completo de emails para un lead.

        Args:
            lead_email: Email del lead
            nombre: Nombre del lead

        Returns:
            dict con todas las secuencias
        """

        print(f"⚔️ Generando funnel completo para: {lead_email}")

        # Secuencia Welcome (Día 0)
        welcome = self.generar_secuencia_welcome(lead_email, nombre)

        # Secuencia Nurture (Días 1-6)
        nurture = self.generar_secuencia_nurture(lead_email)

        # Guardar en Sheets
        self.guardar_email_sheets(welcome)
        for email in nurture:
            self.guardar_email_sheets(email)

        print(f"✅ Funnel generado: 1 welcome + {len(nurture)} nurture emails")

        return {"welcome": welcome, "nurture": nurture, "total_emails": 1 + len(nurture)}


# Ejemplo de uso
if __name__ == "__main__":
    es = EmailSequences()

    # Generar funnel para lead de prueba
    funnel = es.generar_funnel_completo(lead_email="test@example.com", nombre="Hombre")

    print("\n" + "=" * 60)
    print("FUNNEL GENERADO")
    print("=" * 60)
    print(f"Welcome: {funnel['welcome']['asunto']}")
    for email in funnel["nurture"]:
        print(f"Nurture: {email['asunto']}")
