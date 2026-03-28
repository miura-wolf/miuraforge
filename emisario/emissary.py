"""
emissary.py — El Emisario de Disciplina en Acero
==================================================
Módulo de automatización de correos que opera sobre la tabla LEADS
de Google Sheets. Tres secuencias activas:

  1. BIENVENIDA    — 3 correos post-descarga del Fundamento (Días 1, 3, 7)
  2. ALERTA_VIDEO  — Disparo cuando un video se marca PUBLICADO en Sheets
  3. LANZAMIENTO   — Secuencia de conversión del libro $9 (Lunes, Jueves, Domingo)

Uso:
  python emissary.py --secuencia bienvenida
  python emissary.py --secuencia alerta_video
  python emissary.py --secuencia lanzamiento
  python emissary.py --test --email tu@correo.com   ← Prueba sin tocar LEADS

Variables de entorno requeridas (.env):
  BREVO_API_KEY           → API key de Brevo (sendinblue.com)
  GOOGLE_SHEETS_ID        → ID del spreadsheet del motor Miura
  GOOGLE_CREDENTIALS_PATH → ruta al JSON de credenciales service account
  GEMINI_API_KEY          → para personalización con Andrés (opcional)
  YOUTUBE_CHANNEL_URL     → URL base del canal (para links en alertas)
"""

import os
import sys
import json
import time
import datetime
import argparse
import requests
import gspread
from google.oauth2.service_account import Credentials
from dotenv import load_dotenv
from pathlib import Path

# Importar configuración centralizada
try:
    sys.path.append(str(Path(__file__).resolve().parent.parent))
    from core.config import CREDENTIALS_PATH as DEFAULT_CREDS_PATH
except ImportError:
    DEFAULT_CREDS_PATH = Path("credentials.json")

# ── Opcional: personalización con Gemini ──────────────────────────────
try:
    from google import genai as genai_client

    GEMINI_DISPONIBLE = True
except ImportError:
    GEMINI_DISPONIBLE = False

# ── Opcional: fallback con Nvidia NIM (OpenAI compatible) ─────────────
try:
    from openai import OpenAI as OpenAIClient

    NVIDIA_DISPONIBLE = True
except ImportError:
    NVIDIA_DISPONIBLE = False

load_dotenv()

# ─── CONFIGURACIÓN GLOBAL ─────────────────────────────────────────────
BREVO_API_KEY = os.getenv("BREVO_API_KEY", "")
SHEETS_ID = os.getenv("GOOGLE_SHEET_ID", os.getenv("GOOGLE_SHEETS_ID", ""))
# Prioridad: variable de entorno > configuración centralizada > fallback legacy
CREDS_PATH = os.getenv(
    "GOOGLE_JSON_CREDENTIALS", os.getenv("GOOGLE_CREDENTIALS_PATH", str(DEFAULT_CREDS_PATH))
)
GEMINI_KEY = os.getenv("GEMINI_API_KEY", "")
NVIDIA_KEY = os.getenv("OPENAI_API_KEY", "")
NVIDIA_BASE_URL = os.getenv("OPENAI_BASE_URL", "https://integrate.api.nvidia.com/v1")
NVIDIA_MODEL = os.getenv("OPENAI_MODEL", "deepseek-ai/deepseek-v3.1")  # Usar variable de entorno
YOUTUBE_URL = os.getenv("YOUTUBE_CHANNEL_URL", "https://youtube.com/@disciplinaenacero")
REMITENTE_NOMBRE = "Andrés — Disciplina en Acero"
REMITENTE_EMAIL = "contacto@disciplinaenacero.com"

# Límite diario de envíos (calentamiento de dominio)
# Semana 1-2: 30 | Semana 3-4: 100 | Después: 300 (límite Brevo gratuito)
LIMITE_DIARIO = int(os.getenv("LIMITE_DIARIO_EMAILS", "30"))

# Días entre correos de bienvenida
DIAS_BIENVENIDA = [0, 2, 6]  # Día 1, Día 3, Día 7 (índice desde fecha ingreso)

SCOPES = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]


# ─── CONEXIÓN SHEETS ──────────────────────────────────────────────────
def conectar_sheets():
    creds = Credentials.from_service_account_file(CREDS_PATH, scopes=SCOPES)
    client = gspread.authorize(creds)
    return client.open_by_key(SHEETS_ID)


def obtener_leads(ss, estados=None):
    """
    Retorna lista de dicts con los leads de la tabla LEADS.
    estados: lista de valores de ESTADO a filtrar. None = todos.
    """
    try:
        hoja = ss.worksheet("LEADS")
        datos = hoja.get_all_records()
        if estados:
            datos = [r for r in datos if r.get("ESTADO", "") in estados]
        return datos, hoja
    except gspread.exceptions.WorksheetNotFound:
        print("❌ [Emisario] Tabla LEADS no encontrada en Sheets.")
        return [], None


def actualizar_estado(hoja, email, nuevo_estado):
    """Actualiza la columna ESTADO del lead por email."""
    todos = hoja.get_all_values()
    for i, row in enumerate(todos):
        if len(row) > 2 and row[2].lower().strip() == email.lower().strip():
            hoja.update_cell(i + 1, 6, nuevo_estado)
            return True
    return False


def obtener_video_reciente(ss):
    """
    Busca en la tabla CONTENIDO_PUBLICADO el video más reciente
    con estado PUBLICADO que no haya sido notificado aún.
    Retorna dict con titulo, url, descripcion o None.
    """
    try:
        hoja = ss.worksheet("CONTENIDO_PUBLICADO")
        datos = hoja.get_all_records()
        # Buscar el más reciente sin notificar
        for i, row in enumerate(reversed(datos)):
            if str(row.get("ESTADO", "")).upper() == "PUBLICADO":
                if str(row.get("EMAIL_ENVIADO", "")).upper() != "SI":
                    return {
                        "titulo": row.get("TITULO", ""),
                        "url": row.get("URL_YOUTUBE", YOUTUBE_URL),
                        "descripcion": row.get("DESCRIPCION", ""),
                        "fila": len(datos) - i,  # número de fila real
                    }, hoja
        return None, hoja
    except gspread.exceptions.WorksheetNotFound:
        print("⚠️ [Emisario] Tabla CONTENIDO_PUBLICADO no encontrada.")
        print(
            "   Crea la tabla con columnas: TITULO | URL_YOUTUBE | DESCRIPCION | ESTADO | EMAIL_ENVIADO"
        )
        return None, None


def marcar_video_notificado(hoja_contenido, fila_num):
    """Marca EMAIL_ENVIADO = SI en la tabla CONTENIDO_PUBLICADO."""
    # Columna EMAIL_ENVIADO = columna 5
    hoja_contenido.update_cell(fila_num, 5, "SI")


# ─── BREVO API ────────────────────────────────────────────────────────
def enviar_brevo(destinatario_email, destinatario_nombre, asunto, cuerpo_html, cuerpo_texto):
    """
    Envía un correo vía Brevo API.
    Retorna True si fue exitoso, False si falló.
    """
    if not BREVO_API_KEY:
        print("❌ [Brevo] BREVO_API_KEY no configurada en .env")
        return False

    url = "https://api.brevo.com/v3/smtp/email"
    headers = {
        "accept": "application/json",
        "api-key": BREVO_API_KEY,
        "content-type": "application/json",
    }
    payload = {
        "sender": {"name": REMITENTE_NOMBRE, "email": REMITENTE_EMAIL},
        "to": [{"email": destinatario_email, "name": destinatario_nombre or "Recluta"}],
        "subject": asunto,
        "htmlContent": cuerpo_html,
        "textContent": cuerpo_texto,
    }

    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=15)
        if resp.status_code in (200, 201):
            return True
        else:
            print(f"❌ [Brevo] Error {resp.status_code}: {resp.text[:200]}")
            return False
    except Exception as e:
        print(f"❌ [Brevo] Excepción: {e}")
        return False


# ─── PERSONALIZACIÓN CON IA (GEMINI → FALLBACK NVIDIA) ────────────────
PROMPT_PERSONALIZACION = """Eres Andrés, la voz de Disciplina en Acero.
Escribe UNA sola frase (máximo 20 palabras) que conecte directamente con esta motivación del lead:
"{motivacion}"

La frase debe sonar como Andrés: directa, industrial, sin consuelo vacío.
No uses palabras como: sentir, inspiración, camino, potencial.
Solo la frase. Sin comillas. Sin explicación."""


def _personalizar_con_factory(motivacion):
    """Genera frase personalizada usando el cerebro de Emisario de la Factory."""
    from llm.factory import LLMFactory

    try:
        brain = LLMFactory.get_brain("emissary")
        content = brain.generate(
            PROMPT_PERSONALIZACION.format(motivacion=motivacion), temperature=0.85, max_tokens=60
        )
        return content.strip() if content else None
    except Exception as e:
        print(f"⚠️ [Emisario] Error en Factory: {e}")
        return None


def generar_frase_personalizada(nombre, motivacion):
    """
    Genera una sola frase basada en la motivación del lead.
    Prioridad: Nvidia NIM (120b), Fallback: Gemini.
    """
    if not motivacion:
        return None

    # ── Intento 1: LLM Factory (Prioridad) ─────────────────────────────
    frase = _personalizar_con_factory(motivacion)
    if frase:
        print(f"✅ [Factory] Frase generada para: {nombre[:20]}")
        return frase

    # ── Intento 2: Gemini (Fallback) ──────────────────────────────────
    if GEMINI_DISPONIBLE and GEMINI_KEY:
        model_gemini = os.getenv("ACTIVE_MODEL", "gemini-1.5-flash")
        try:
            api_key = GEMINI_KEY.split("#")[0].strip()
            client = genai_client.Client(api_key=api_key)
            respuesta = client.models.generate_content(
                model=model_gemini, contents=PROMPT_PERSONALIZACION.format(motivacion=motivacion)
            )
            frase = respuesta.text.strip()
            print(f"✅ [Gemini] Frase generada para: {nombre[:20]}")
            return frase
        except Exception as e:
            print(f"⚠️ [Gemini] Falló: {str(e)[:50]}")

    return None


# ─── PLANTILLAS DE CORREO ─────────────────────────────────────────────


def _base_html(contenido_inner):
    """Wrapper HTML con estética Disciplina en Acero."""
    contenido_inner = contenido_inner.replace("[[PUNTO_DE_DOLOR]]", "")
    return f"""
<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<style>
  body {{ margin:0; padding:0; background:#0A0A0A; font-family: Georgia, serif; }}
  .wrapper {{ max-width:600px; margin:0 auto; background:#111111; }}
  .header {{ background:#0A0A0A; padding:32px 40px; border-bottom:1px solid #2A2A2A; }}
  .header-logo {{ font-family: 'Courier New', monospace; font-size:13px; letter-spacing:0.25em; color:#C8A96E; text-transform:uppercase; text-decoration:none; }}
  .body {{ padding:40px; }}
  .saludo {{ font-family:'Courier New',monospace; font-size:11px; letter-spacing:0.2em; color:#C8A96E; text-transform:uppercase; margin-bottom:24px; }}
  p {{ font-size:16px; line-height:1.7; color:#CCCCCC; margin:0 0 20px; }}
  .frase-acero {{ border-left:2px solid #C8A96E; padding:16px 20px; margin:28px 0; font-style:italic; color:#E8E3DA; font-size:15px; line-height:1.6; }}
  .cta-btn {{ display:inline-block; background:#C8A96E; color:#0A0A0A; font-family:'Courier New',monospace; font-size:12px; letter-spacing:0.2em; text-transform:uppercase; padding:14px 32px; text-decoration:none; margin:8px 0; }}
  .separador {{ border:none; border-top:1px solid #2A2A2A; margin:32px 0; }}
  .footer {{ padding:24px 40px; border-top:1px solid #2A2A2A; }}
  .footer p {{ font-size:11px; color:#555555; line-height:1.6; margin:0; }}
  .footer a {{ color:#555555; }}
</style>
</head>
<body>
<div class="wrapper">
  <div class="header">
    <a href="https://disciplinaenacero.com" class="header-logo">⚔ Disciplina en Acero</a>
  </div>
  <div class="body">
    {contenido_inner}
  </div>
  <div class="footer">
    <p>
      Este correo llega porque solicitaste acceso al Fundamento en
      <a href="https://disciplinaenacero.com">disciplinaenacero.com</a><br>
      <a href="{{{{unsubscribe}}}}">Darse de baja</a>
    </p>
  </div>
</div>
</body>
</html>
"""


# ── Secuencia BIENVENIDA ──────────────────────────────────────────────

BIENVENIDA = [
    # Correo 0 — Día 1: Entrega del Fundamento
    {
        "dia": 0,
        "asunto": "{nombre}, aquí está el Fundamento.",
        "texto": """
{nombre},

Lo pediste. Aquí está.

El Fundamento no es motivación. Es el protocolo de base que nadie te va a dar en un video de 10 minutos.

30 días. Sin ruido. Sin atajos.

Descarga el PDF aquí: https://disciplinaenacero.com/pages/fundamento

Una advertencia: el Capítulo V tiene una tabla de tres columnas. No la saltes. Esa tabla es donde la mayoría abandona — y donde empieza la diferencia.

[[PUNTO_DE_DOLOR]]

El acero no se oxida con orgullo. Se templa con trabajo implacable.

Andrés
Disciplina en Acero
""",
        "html_inner": """
<p class="saludo">{nombre} — Acceso concedido</p>
<p>Lo pediste. Aquí está.</p>
<p>El Fundamento no es motivación. Es el protocolo de base que nadie te va a dar en un video de 10 minutos.</p>
<div class="frase-acero">30 días. Sin ruido. Sin atajos.</div>
<p style="text-align:center; margin:32px 0;">
  <a href="https://disciplinaenacero.com/pages/fundamento" class="cta-btn">Descargar el Fundamento →</a>
</p>
<hr class="separador">
<p>Una advertencia: el <strong style="color:#E8E3DA;">Capítulo V</strong> tiene una tabla de tres columnas. No la saltes. Esa tabla es donde la mayoría abandona — y donde empieza la diferencia.</p>
<p>[[PUNTO_DE_DOLOR]]</p>
<p style="color:#888; font-size:14px;">El acero no se oxida con orgullo. Se templa con trabajo implacable.</p>
<p style="color:#C8A96E; font-size:14px; font-family:'Courier New',monospace;">— Andrés</p>
""",
    },
    # Correo 1 — Día 3: Verificación de temperatura
    {
        "dia": 2,
        "asunto": "{nombre}, ¿ya desactivaste la notificación?",
        "texto": """
{nombre},

Hace dos días llegó el Fundamento a tu bandeja.

Una pregunta directa: ¿ya bloqueaste las notificaciones que discutimos en el Capítulo V?

Si la respuesta es no — el acero se está enfriando.

No porque seas débil. Sino porque el sistema está diseñado para que no lo hagas.
Cada notificación que llega mientras trabajas es un micro-robo de atención.
Multiplicado por 40 al día. Por 30 días. Eso no es distracción. Es demolición.

La tabla de las tres columnas requiere bloques de tiempo reales.
Sin eso, es solo más papel.

[[PUNTO_DE_DOLOR]]

Andrés
Disciplina en Acero
""",
        "html_inner": """
<p class="saludo">{nombre} — Verificación de temperatura</p>
<p>Hace dos días llegó el Fundamento a tu bandeja.</p>
<p>Una pregunta directa: <strong style="color:#E8E3DA;">¿ya bloqueaste las notificaciones que discutimos en el Capítulo V?</strong></p>
<div class="frase-acero">Si la respuesta es no — el acero se está enfriando.</div>
<p>No porque seas débil. Sino porque el sistema está diseñado para que no lo hagas.</p>
<p>Cada notificación que llega mientras trabajas es un micro-robo de atención. Multiplicado por 40 al día. Por 30 días. Eso no es distracción. Es demolición.</p>
<p>La tabla de las tres columnas requiere bloques de tiempo reales. Sin eso, es solo más papel.</p>
<p>[[PUNTO_DE_DOLOR]]</p>
<p style="color:#C8A96E; font-size:14px; font-family:'Courier New',monospace;">— Andrés</p>
""",
    },
    # Correo 2 — Día 7: El diagnóstico completo
    {
        "dia": 6,
        "asunto": "{nombre}, el diagnóstico completo existe.",
        "texto": """
{nombre},

Una semana desde el Fundamento.

El protocolo es el suelo. Pero el suelo sin arquitectura encima es solo tierra.

Hay un diagnóstico completo de lo que te tiene paralizado.
No un capítulo. No un video. Un análisis quirúrgico de los cuatro mecanismos exactos que operan en el hombre que lleva tiempo sintiéndose desorientado.

Se llama: El Hombre que Dejó de Mentirse.

Cuando esté disponible, los primeros acceden a precio de lanzamiento.
Deja que te avise cuando abra: https://disciplinaenacero.com/pages/ebook

[[PUNTO_DE_DOLOR]]

La identidad sigue a la ejecución. No al revés.

Andrés
Disciplina en Acero
""",
        "html_inner": """
<p class="saludo">{nombre} — Una semana en la forja</p>
<p>El protocolo es el suelo. Pero el suelo sin arquitectura encima es solo tierra.</p>
<p>Hay un diagnóstico completo de lo que te tiene paralizado. No un capítulo. No un video. Un análisis quirúrgico de los cuatro mecanismos exactos que operan en el hombre que lleva tiempo sintiéndose desorientado.</p>
<div class="frase-acero">"La identidad sigue a la ejecución. No al revés."</div>
<p>Se llama: <strong style="color:#E8E3DA;">El Hombre que Dejó de Mentirse.</strong></p>
<p>Cuando esté disponible, los primeros acceden a precio de lanzamiento.</p>
<p style="text-align:center; margin:32px 0;">
  <a href="https://disciplinaenacero.com/pages/ebook" class="cta-btn">Quiero ser notificado →</a>
</p>
<p>[[PUNTO_DE_DOLOR]]</p>
<p style="color:#C8A96E; font-size:14px; font-family:'Courier New',monospace;">— Andrés</p>
""",
    },
]

# ── Secuencia LANZAMIENTO ─────────────────────────────────────────────

LANZAMIENTO = [
    # Email 1 — Lunes: Revelación
    {
        "estado_trigger": "lead_lanzamiento_1",
        "asunto": "{nombre}, el diagnóstico está disponible. Precio real: $9.",
        "texto": """
{nombre},

Sin precio original tachado. Sin cuenta regresiva falsa.

El Hombre que Dejó de Mentirse está disponible ahora.

101 páginas. Cinco capítulos. Cuatro mecanismos exactos que mantienen al hombre paralizado — y la secuencia que los interrumpe.

Precio de lanzamiento para los primeros: $9 USD.
La semana que viene sube a $17. Sin excepción.

Accede aquí: https://disciplinaenacero.com/pages/ebook

No es un ebook de autoayuda. Es el diagnóstico que ningún video de 60 segundos puede darte.

Andrés
Disciplina en Acero
""",
        "html_inner": """
<p class="saludo">{nombre} — El diagnóstico está listo</p>
<p>Sin precio original tachado. Sin cuenta regresiva falsa.</p>
<p><strong style="color:#E8E3DA;">El Hombre que Dejó de Mentirse</strong> está disponible ahora.</p>
<p>101 páginas. Cinco capítulos. Cuatro mecanismos exactos que mantienen al hombre paralizado — y la secuencia que los interrumpe.</p>
<div class="frase-acero">Precio de lanzamiento: $9 USD — sube a $17 la próxima semana. Sin excepción.</div>
<p style="text-align:center; margin:32px 0;">
  <a href="https://disciplinaenacero.com/pages/ebook" class="cta-btn">Acceder al diagnóstico — $9 →</a>
</p>
<p style="color:#C8A96E; font-size:14px; font-family:'Courier New',monospace;">— Andrés</p>
""",
    },
    # Email 2 — Jueves: Presión
    {
        "estado_trigger": "lead_lanzamiento_2",
        "asunto": "{nombre}, el precio de $9 es una cortesía. El lunes termina.",
        "texto": """
{nombre},

El lunes el precio sube a $17 por ley de disciplina.

No es urgencia artificial. Es consecuencia real.
El que actúa rápido paga menos. Eso es doctrina.

Lo que contiene el diagnóstico que todavía no tienes:

— Por qué el silencio no es fortaleza. Es deuda diferida.
— El mecanismo exacto que secuestra tu sistema de recompensa.
— La diferencia entre la máscara que construiste y la identidad que decides.
— Por qué la responsabilidad como condena te está destruyendo.

$9 hasta el domingo: https://disciplinaenacero.com/pages/ebook

Andrés
Disciplina en Acero
""",
        "html_inner": """
<p class="saludo">{nombre} — El lunes el precio cambia</p>
<p>No es urgencia artificial. Es consecuencia real. El que actúa rápido paga menos. Eso es doctrina.</p>
<p>Lo que contiene el diagnóstico que todavía no tienes:</p>
<div class="frase-acero">
  — Por qué el silencio no es fortaleza. Es deuda diferida.<br>
  — El mecanismo que secuestra tu sistema de recompensa.<br>
  — La diferencia entre la máscara que construiste y la identidad que decides.<br>
  — Por qué la responsabilidad como condena te está destruyendo.
</div>
<p style="text-align:center; margin:32px 0;">
  <a href="https://disciplinaenacero.com/pages/ebook" class="cta-btn">$9 hasta el domingo →</a>
</p>
<p style="color:#C8A96E; font-size:14px; font-family:'Courier New',monospace;">— Andrés</p>
""",
    },
    # Email 3 — Domingo: Última llamada
    {
        "estado_trigger": "lead_lanzamiento_3",
        "asunto": "{nombre}, última llamada. Hoy a medianoche.",
        "texto": """
{nombre},

Hoy a medianoche el precio sube a $17.

Sin recordatorios adicionales. Sin segunda oportunidad al precio de lanzamiento.

El que llega tarde paga el precio de su lentitud.
Eso también es doctrina.

https://disciplinaenacero.com/pages/ebook

Andrés
Disciplina en Acero
""",
        "html_inner": """
<p class="saludo">{nombre} — Última llamada</p>
<p>Hoy a medianoche el precio sube a $17.</p>
<div class="frase-acero">El que llega tarde paga el precio de su lentitud. Eso también es doctrina.</div>
<p style="text-align:center; margin:32px 0;">
  <a href="https://disciplinaenacero.com/pages/ebook" class="cta-btn">Último acceso a $9 →</a>
</p>
<p style="color:#888; font-size:13px;">Sin recordatorios adicionales. Sin segunda oportunidad al precio de lanzamiento.</p>
<p style="color:#C8A96E; font-size:14px; font-family:'Courier New',monospace;">— Andrés</p>
""",
    },
]

# ─── MOTOR DE SECUENCIAS ──────────────────────────────────────────────


def ejecutar_bienvenida(modo_test=False, email_test=None):
    """
    Procesa la secuencia de bienvenida.
    Lee LEADS, detecta qué correo corresponde según días transcurridos,
    envía y actualiza estado.
    """
    print("⚔️  [Emisario] Iniciando secuencia BIENVENIDA...")
    ss = conectar_sheets()
    leads, hoja = obtener_leads(ss, estados=["nuevo", "bienvenida_1", "bienvenida_2"])
    enviados_sesion = 0

    if not leads and not modo_test:
        print(
            "ℹ️  [Emisario] No se encontraron leads en estados 'nuevo', 'bienvenida_1' o 'bienvenida_2'."
        )
        print("   Revisa la columna ESTADO en tu hoja de Google Sheets.")

    if modo_test:
        leads = [
            {
                "NOMBRE": "Test",
                "EMAIL": email_test,
                "MOTIVACION": "Disciplinar mi mente",
                "ESTADO": "nuevo",
                "FECHA": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
            }
        ]
        hoja = None
        print(f"🧪 [Test] Enviando a: {email_test}")

    for lead in leads:
        if enviados_sesion >= LIMITE_DIARIO:
            print(f"⚠️  [Emisario] Límite diario alcanzado ({LIMITE_DIARIO}). Reanuda mañana.")
            break

        nombre = str(lead.get("NOMBRE", "")).strip() or "Recluta"
        email = str(lead.get("EMAIL", "")).strip()
        # Buscar el dolor en MOTIVACION o DOLOR
        motivacion = str(lead.get("MOTIVACION", lead.get("DOLOR", ""))).strip()
        estado = str(lead.get("ESTADO", "nuevo")).strip()
        fecha_str = str(lead.get("FECHA", "")).strip()

        if not email:
            continue

        # Calcular días transcurridos
        try:
            fecha_ingreso = datetime.datetime.strptime(fecha_str[:16], "%Y-%m-%d %H:%M")
            dias = (datetime.datetime.now() - fecha_ingreso).days
        except:
            dias = 0

        # Determinar qué correo enviar
        correo_idx = None
        if estado == "nuevo" and dias >= DIAS_BIENVENIDA[0]:
            correo_idx = 0
            nuevo_estado = "bienvenida_1"
        elif estado == "bienvenida_1" and dias >= DIAS_BIENVENIDA[1]:
            correo_idx = 1
            nuevo_estado = "bienvenida_2"
        elif estado == "bienvenida_2" and dias >= DIAS_BIENVENIDA[2]:
            correo_idx = 2
            nuevo_estado = "bienvenida_completa"
        else:
            # LOG DE DIAGNÓSTICO
            idx_esperado = 0
            if estado == "bienvenida_1":
                idx_esperado = 1
            elif estado == "bienvenida_2":
                idx_esperado = 2

            umbral = DIAS_BIENVENIDA[idx_esperado]
            print(
                f"ℹ️  Lead {nombre[:15]} en estado '{estado}': lleva {dias} días (faltan {umbral - dias} para el próximo correo)"
            )
            continue

        plantilla = BIENVENIDA[correo_idx]
        asunto = plantilla["asunto"].format(nombre=nombre)
        html_body = plantilla["html_inner"].format(nombre=nombre)
        txt_body = plantilla["texto"].format(nombre=nombre)

        # Personalización (UNA SOLA LLAMADA)
        frase = generar_frase_personalizada(nombre, motivacion)
        linea_p = frase if frase else ""

        html_body = html_body.replace("[[PUNTO_DE_DOLOR]]", linea_p)
        txt_body = txt_body.replace("[[PUNTO_DE_DOLOR]]", linea_p)

        html_final = _base_html(html_body)

        ok = enviar_brevo(email, nombre, asunto, html_final, txt_body)

        if ok:
            enviados_sesion += 1
            print(f"✅ [{correo_idx + 1}/3] Enviado a: {nombre} <{email}> — Estado: {nuevo_estado}")
            if hoja and not modo_test:
                actualizar_estado(hoja, email, nuevo_estado)
                time.sleep(0.5)  # Pausa cortés con la API de Sheets
        else:
            print(f"❌ Error enviando a: {email}")

    print(f"\n📊 [Emisario] Bienvenida completada. Enviados: {enviados_sesion}")


def ejecutar_alerta_video(modo_test=False, email_test=None):
    """
    Detecta el video más reciente publicado en CONTENIDO_PUBLICADO,
    redacta el correo de alerta y lo envía a toda la lista activa.
    """
    print("⚔️  [Emisario] Iniciando secuencia ALERTA DE VIDEO...")
    ss = conectar_sheets()

    video, hoja_contenido = obtener_video_reciente(ss)
    if not video:
        print("ℹ️  [Emisario] No hay videos nuevos para notificar.")
        return

    print(f"🎬 Video detectado: {video['titulo']}")
    print(f"   URL: {video['url']}")

    # Obtener todos los leads activos (no compradores, no dados de baja)
    estados_activos = [
        "nuevo",
        "bienvenida_1",
        "bienvenida_2",
        "bienvenida_completa",
        "lead_lanzamiento_1",
        "lead_lanzamiento_2",
        "lead_lanzamiento_3",
    ]
    leads, hoja_leads = obtener_leads(ss, estados=estados_activos)

    if modo_test:
        leads = [{"NOMBRE": "Test", "EMAIL": email_test, "MOTIVACION": ""}]

    titulo = video["titulo"]
    url_video = video["url"]
    enviados = 0

    for lead in leads:
        if enviados >= LIMITE_DIARIO:
            print(f"⚠️  Límite diario alcanzado ({LIMITE_DIARIO}).")
            break

        nombre = str(lead.get("NOMBRE", "")).strip() or "Recluta"
        email = str(lead.get("EMAIL", "")).strip()
        if not email:
            continue

        asunto = f"{nombre}, el ruido está ganando. Mira el diagnóstico de hoy."

        html_inner = f"""
<p class="saludo">{nombre} — Nueva pieza de artillería</p>
<p>No es entretenimiento.</p>
<p>Es un análisis sobre <strong style="color:#E8E3DA;">{titulo}</strong> — y cómo opera sobre el hombre que todavía no lo ha nombrado.</p>
<div class="frase-acero">El conocimiento sin ejecución es solo más ruido.</div>
<p style="text-align:center; margin:32px 0;">
  <a href="{url_video}" class="cta-btn">Ver el diagnóstico →</a>
</p>
<hr class="separador">
<p>Después de verlo, vuelve a la tabla de las tres columnas de tu protocolo. Lo que acabas de aprender requiere una acción concreta antes de que el día termine.</p>
<p style="color:#C8A96E; font-size:14px; font-family:'Courier New',monospace;">— Andrés</p>
"""
        txt = f"""
{nombre},

No es entretenimiento.

Es un análisis sobre "{titulo}" — y cómo opera sobre el hombre que todavía no lo ha nombrado.

Míralo aquí: {url_video}

Después de verlo, vuelve a la tabla de las tres columnas de tu protocolo.
El conocimiento sin ejecución es solo más ruido.

Andrés
Disciplina en Acero
"""
        html_final = _base_html(html_inner)
        ok = enviar_brevo(email, nombre, asunto, html_final, txt)

        if ok:
            enviados += 1
            print(f"✅ Alerta enviada: {nombre} <{email}>")
            time.sleep(0.3)
        else:
            print(f"❌ Error: {email}")

    # Marcar video como notificado
    if not modo_test and hoja_contenido and enviados > 0:
        marcar_video_notificado(hoja_contenido, video["fila"])
        print(f"✅ Video marcado como EMAIL_ENVIADO en Sheets.")

    print(f"\n📊 [Emisario] Alerta completada. Enviados: {enviados}")


def ejecutar_lanzamiento(fase=1, modo_test=False, email_test=None):
    """
    Ejecuta una fase específica de la secuencia de lanzamiento del libro.
    fase: 1 (Lunes revelación), 2 (Jueves presión), 3 (Domingo última llamada)
    """
    print(f"⚔️  [Emisario] Iniciando LANZAMIENTO — Fase {fase}...")
    ss = conectar_sheets()

    # En lanzamiento, enviamos a todos los que completaron bienvenida
    # y no han comprado todavía
    estados_objetivo = ["bienvenida_completa", "bienvenida_1", "bienvenida_2"]
    leads, hoja = obtener_leads(ss, estados=estados_objetivo)

    if modo_test:
        leads = [{"NOMBRE": "Test", "EMAIL": email_test, "MOTIVACION": ""}]
        hoja = None

    plantilla = LANZAMIENTO[fase - 1]
    nuevo_estado = plantilla["estado_trigger"]
    enviados = 0

    for lead in leads:
        if enviados >= LIMITE_DIARIO:
            print(f"⚠️  Límite diario alcanzado ({LIMITE_DIARIO}).")
            break

        nombre = str(lead.get("NOMBRE", "")).strip() or "Recluta"
        email = str(lead.get("EMAIL", "")).strip()
        if not email:
            continue

        asunto = plantilla["asunto"].format(nombre=nombre)
        html_inner = plantilla["html_inner"].format(nombre=nombre)
        txt = plantilla["texto"].format(nombre=nombre)
        html_final = _base_html(html_inner)

        ok = enviar_brevo(email, nombre, asunto, html_final, txt)

        if ok:
            enviados += 1
            print(f"✅ Lanzamiento F{fase}: {nombre} <{email}>")
            if hoja and not modo_test:
                actualizar_estado(hoja, email, nuevo_estado)
                time.sleep(0.5)
        else:
            print(f"❌ Error: {email}")

    print(f"\n📊 [Emisario] Lanzamiento F{fase} completado. Enviados: {enviados}")


# ─── VERIFICAR CONFIGURACIÓN ──────────────────────────────────────────
def verificar_config():
    print("\n🔍 [Emisario] Verificando configuración...")
    errores = []

    if not BREVO_API_KEY:
        errores.append("❌ BREVO_API_KEY no configurada en .env")
    else:
        # Test conexión Brevo
        resp = requests.get(
            "https://api.brevo.com/v3/account", headers={"api-key": BREVO_API_KEY}, timeout=10
        )
        if resp.status_code == 200:
            data = resp.json()
            print(f"✅ Brevo conectado: {data.get('email', 'OK')}")
            print(
                f"   Plan: {data.get('plan', [{}])[0].get('type', 'N/A') if data.get('plan') else 'N/A'}"
            )
        else:
            errores.append(f"❌ Brevo API error: {resp.status_code}")

    if not SHEETS_ID:
        errores.append("❌ GOOGLE_SHEETS_ID no configurado")
    else:
        try:
            ss = conectar_sheets()
            leads, _ = obtener_leads(ss)
            print(f"✅ Sheets conectado. Leads en tabla: {len(leads)}")
        except Exception as e:
            errores.append(f"❌ Sheets error: {e}")

    # Test LLMs
    print("\n🤖 [IA] Verificando modelos...")
    if not GEMINI_KEY:
        print("⚠️  GEMINI_API_KEY no detectada.")
    else:
        print(f"✅ Gemini Key detectada (comienza por {GEMINI_KEY[:5]}...)")

    if not NVIDIA_KEY:
        print("⚠️  OPENAI_API_KEY (Nvidia) no detectada.")
    else:
        print(f"✅ Nvidia Key detectada (comienza por {NVIDIA_KEY[:8]}...)")
        print(f"   Modelo Nvidia: {NVIDIA_MODEL}")

    if errores:
        print("\n".join(errores))
        return False

    print("✅ Todo en orden. El Emisario está listo para operar.\n")
    return True


# ─── CLI ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="⚔️  Emissary — Disciplina en Acero",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument(
        "--secuencia",
        choices=["bienvenida", "alerta_video", "lanzamiento"],
        help="Secuencia a ejecutar",
    )
    parser.add_argument(
        "--fase",
        type=int,
        choices=[1, 2, 3],
        default=1,
        help="Fase del lanzamiento (1=Lunes, 2=Jueves, 3=Domingo)",
    )
    parser.add_argument(
        "--test",
        action="store_true",
        help="Modo test: envía solo al --email indicado sin tocar LEADS",
    )
    parser.add_argument("--email", type=str, help="Email destino en modo test")
    parser.add_argument(
        "--verificar", action="store_true", help="Verifica conexión con Brevo y Sheets"
    )

    args = parser.parse_args()

    if args.verificar:
        verificar_config()
        sys.exit(0)

    if args.test and not args.email:
        print("❌ --test requiere --email")
        sys.exit(1)

    if not args.secuencia:
        parser.print_help()
        sys.exit(0)

    if args.secuencia == "bienvenida":
        ejecutar_bienvenida(modo_test=args.test, email_test=args.email)

    elif args.secuencia == "alerta_video":
        ejecutar_alerta_video(modo_test=args.test, email_test=args.email)

    elif args.secuencia == "lanzamiento":
        ejecutar_lanzamiento(fase=args.fase, modo_test=args.test, email_test=args.email)
