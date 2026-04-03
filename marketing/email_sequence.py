"""
marketing/email_sequence.py — MiuraForge Marketing Toolkit
============================================================
Generador de secuencias de emails automatizados para funnel.

Soporta:
- Secuencias de bienvenida (onboarding)
- Secuencias de lanzamiento (launch)
- Secuencias de re-engancho (re-engagement)
- Secuencias de venta (sales)

Cada secuencia respeta la Doctrina Andrés:
- Sin verbos permisivos ("podrías", "quizás")
- CTAs físicos y concretos
- Tono de autoridad calmada

Uso:
    python -m marketing.email_sequence --tipo bienvenida --producto "El Hombre que Dejó de Mentirse"
    python -m marketing.email_sequence --tipo lanzamiento --duracion 7
    python -m marketing.email_sequence --exportar emails.json
"""

import sys
import argparse
from pathlib import Path
from typing import Optional
import json
import re

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from llm.factory import LLMFactory

# ---------------------------------------------------------------------------
# CONFIGURACIÓN DE SECUENCIAS
# ---------------------------------------------------------------------------

TIPOS_SECUENCIA = {
    "bienvenida": {
        "nombre": "Secuencia de Bienvenida",
        "descripcion": "Onboarding para nuevos suscriptores",
        "duracion_dias": 5,
        "objetivo": "Establecer confianza + presentar propuesta de valor",
        "dia_0": "Email inmediato de bienvenida",
        "dia_1": "Historia personal del fundador",
        "dia_3": "Contenido de valor (framework gratis)",
        "dia_5": "Soft pitch del producto principal",
        "dia_7": "Social proof + CTA final",
    },
    "lanzamiento": {
        "nombre": "Secuencia de Lanzamiento",
        "descripcion": "Secuencia para lanzar un producto nuevo",
        "duracion_dias": 7,
        "objetivo": "Generar anticipation + escasez + conversión",
        "estructura": ["anuncio", "educacion", "beneficios", "objeciones", "urgencia", "cierre"],
    },
    "reengancho": {
        "nombre": "Secuencia de Re-engancho",
        "descripcion": "Reactivar suscriptores inactivos",
        "duracion_dias": 3,
        "objetivo": "Recuperar interés + re-ofrecer valor",
    },
    "venta": {
        "nombre": "Secuencia de Venta",
        "descripcion": "Secuencia directa de conversión",
        "duracion_dias": 5,
        "objetivo": "Cierre de venta con CTAs progresivos",
    },
}

VERBOS_PROHIBIDOS = [
    "podrías",
    "quizás",
    "tal vez",
    "posiblemente",
    "quizá",
    "a lo mejor",
    "deberías",
    "tendrías que",
    "tal vez deberías",
]

VERBOS_PERMITIDOS = [
    "hacé",
    "ejecutá",
    "implementá",
    "forjá",
    "construÍ",
    "aplicá",
    "poné en práctica",
    "ejecuta ahora",
]

# ---------------------------------------------------------------------------
# PROMPTS PARA LLM
# ---------------------------------------------------------------------------

PROMPT_SECUENCIA = """Eres el Copywriter de Email Marketing de Disciplina en Acero.

Tu trabajo es crear una secuencia de emails que respeta la Doctrina Andrés:
- Tono de AUTORIDAD CALMADA (no grito, no desesperación)
- CTAs FÍSICOS y concretos (no "piensa en esto", sino "hacé X ahora")
- Prohibido: {verbos_prohibidos}
- Permitido: {verbos_permitidos}

Tipo de secuencia: {tipo_secuencia}
Producto/Servicio: {producto}
Objetivo: {objetivo}
Duración: {duracion} días

Genera la secuencia completa en JSON:

```json
{{
    "secuencia": [
        {{
            "dia": 1,
            "asunto": "Asunto del email (máx 50 chars, sin emojis)",
            "preheader": "Preview del email (máx 80 chars)",
            "cuerpo": "Cuerpo del email en texto plano. Usá párrafos cortos. Terminá con un CTA físico.",
            "cta_principal": "Texto del botón CTA",
            "objetivo_email": "Qué busca lograr este email"
        }}
    ],
    "metricas_esperadas": {{
        "open_rate_estimado": "XX%",
        "click_rate_estimado": "XX%",
        "conversion_estimada": "XX%"
    }},
    "notas_implementacion": [
        "Tips técnicos para implementar"
    ]
}}
```

Responde SOLO con el JSON."""

PROMPT_ASUNTOS = """Eres el especialista en Subject Lines de Disciplina en Acero.

Generá 5 variantes de asunto de email para:
Contexto: {contexto}
Objetivo: {objetivo}

Reglas:
- Máximo 50 caracteres
- Sin emojis
- Sin SPAM words (gratis, oferta, descuento)
- Curiosidad + beneficio
- Tono Andrés: directo, sin adornos

Devuelve un JSON:

```json
{{
    "asuntos": [
        {{
            "texto": "asunto aquí",
            "tipo": "curiosidad|beneficio|historia|pregunta",
            "score_estimado": 85
        }}
    ],
    "recomendado": "mejor asunto"
}}
```"""

# ---------------------------------------------------------------------------
# FUNCIONES AUXILIARES
# ---------------------------------------------------------------------------


def _extraer_json(texto: str) -> Optional[dict]:
    """Extrae JSON de respuesta del LLM."""
    try:
        return json.loads(texto)
    except json.JSONDecodeError:
        pass

    json_match = re.search(r"```(?:json)?\s*([\s\S]*?)```", texto)
    if json_match:
        try:
            return json.loads(json_match.group(1).strip())
        except json.JSONDecodeError:
            pass

    json_match = re.search(r"\{[\s\S]*\}", texto)
    if json_match:
        try:
            clean = re.sub(r",\s*([}\]])", r"\1", json_match.group(0))
            return json.loads(clean)
        except json.JSONDecodeError:
            pass

    return None


def _validar_doctrina(texto: str) -> list[str]:
    """Valida que el texto cumpla con la Doctrina Andrés."""
    violaciones = []
    texto_lower = texto.lower()

    for verbo in VERBOS_PROHIBIDOS:
        if verbo in texto_lower:
            violaciones.append(f"Verbo prohibido encontrado: '{verbo}'")

    return violaciones


def _get_llm():
    """Obtiene instancia del LLM."""
    return LLMFactory.get_provider()


# ---------------------------------------------------------------------------
# FUNCIONES PRINCIPALES
# ---------------------------------------------------------------------------


def generar_secuencia(
    tipo: str = "bienvenida",
    producto: str = "Disciplina en Acero",
    duracion: Optional[int] = None,
) -> dict:
    """
    Genera una secuencia de emails completa.

    Args:
        tipo: Tipo de secuencia (bienvenida, lanzamiento, reengancho, venta)
        producto: Nombre del producto/servicio
        duracion: Duración en días (opcional, usa default del tipo)

    Returns:
        Dict con la secuencia completa
    """
    if tipo not in TIPOS_SECUENCIA:
        print(f"⚠️ Tipo '{tipo}' no válido. Disponibles: {list(TIPOS_SECUENCIA.keys())}")
        return {}

    config = TIPOS_SECUENCIA[tipo]
    dias = duracion or config["duracion_dias"]
    llm = _get_llm()

    prompt = PROMPT_SECUENCIA.format(
        tipo_secuencia=config["nombre"],
        producto=producto,
        objetivo=config["objetivo"],
        duracion=dias,
        verbos_prohibidos=", ".join(VERBOS_PROHIBIDOS[:5]),
        verbos_permitidos=", ".join(VERBOS_PERMITIDOS[:5]),
    )

    print(f"📧 Generando secuencia de {config['nombre']} para: {producto}...")
    response = llm.generate(prompt)

    resultado = _extraer_json(response)
    if not resultado:
        print("⚠️ No se pudo parsear respuesta del LLM")
        return {"error": "parse_error", "raw_response": response}

    # Validar doctrina en cada email
    for email in resultado.get("secuencia", []):
        violaciones = _validar_doctrina(email.get("cuerpo", ""))
        if violaciones:
            email["validacion_doctrina"] = violaciones

    return resultado


def generar_asuntos(
    contexto: str,
    objetivo: str = "maximizar apertura",
) -> dict:
    """
    Genera variantes de asuntos de email.

    Args:
        contexto: Contexto del email
        objetivo: Objetivo del asunto

    Returns:
        Dict con asuntos y recomendado
    """
    llm = _get_llm()

    prompt = PROMPT_ASUNTOs.format(contexto=contexto, objetivo=objetivo)

    print(f"✉️ Generando asuntos para: {contexto[:50]}...")
    response = llm.generate(prompt)

    resultado = _extraer_json(response)
    if not resultado:
        return {"error": "parse_error"}

    return resultado


def exportar_secuencia(secuencia: dict, formato: str = "json") -> str:
    """
    Exporta secuencia en formato específico.

    Args:
        secuencia: Dict con la secuencia
        formato: Formato de export (json, csv, html)

    Returns:
        String con el contenido exportado
    """
    if formato == "json":
        return json.dumps(secuencia, indent=2, ensure_ascii=False)

    elif formato == "csv":
        lines = ["dia,asunto,preheader,cta_principal"]
        for email in secuencia.get("secuencia", []):
            lines.append(
                f"{email.get('dia', '')},{email.get('asunto', '')},{email.get('preheader', '')},{email.get('cta_principal', '')}"
            )
        return "\n".join(lines)

    elif formato == "html":
        html = ["<html><body><h1>Secuencia de Emails</h1>"]
        for email in secuencia.get("secuencia", []):
            html.append(f"""
<div style="border: 1px solid #333; padding: 20px; margin: 20px;">
    <h2>Día {email.get("dia", "N/A")}: {email.get("asunto", "Sin asunto")}</h2>
    <p><strong>Preheader:</strong> {email.get("preheader", "")}</p>
    <p><strong>CTA:</strong> {email.get("cta_principal", "")}</p>
    <div style="white-space: pre-wrap;">{email.get("cuerpo", "")}</div>
</div>
""")
        html.append("</body></html>")
        return "\n".join(html)

    return json.dumps(secuencia, indent=2, ensure_ascii=False)


def mostrar_preview(secuencia: dict) -> None:
    """Muestra preview de la secuencia en consola."""
    print("\n" + "=" * 60)
    print("📧 PREVIEW DE SECUENCIA DE EMAILS")
    print("=" * 60)

    for email in secuencia.get("secuencia", []):
        dia = email.get("dia", "N/A")
        asunto = email.get("asunto", "Sin asunto")
        cta = email.get("cta_principal", "Sin CTA")

        print(f"\n📅 DÍA {dia}")
        print(f"   Asunto: {asunto}")
        print(f"   CTA: {cta}")

        if "validacion_doctrina" in email:
            print(f"   ⚠️ Validación: {email['validacion_doctrina']}")

    # Métricas
    if "metricas_esperadas" in secuencia:
        print("\n📊 MÉTRICAS ESPERADAS:")
        for k, v in secuencia["metricas_esperadas"].items():
            print(f"   {k}: {v}")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main():
    parser = argparse.ArgumentParser(description="Generador de Secuencias de Email")
    parser.add_argument(
        "--tipo",
        choices=list(TIPOS_SECUENCIA.keys()),
        default="bienvenida",
        help="Tipo de secuencia",
    )
    parser.add_argument("--producto", default="Disciplina en Acero", help="Producto/servicio")
    parser.add_argument("--duracion", type=int, help="Duración en días")
    parser.add_argument(
        "--exportar",
        choices=["json", "csv", "html"],
        help="Formato de exportación",
    )
    parser.add_argument("--output", default="secuencia.json", help="Archivo de salida")

    args = parser.parse_args()

    secuencia = generar_secuencia(
        tipo=args.tipo,
        producto=args.producto,
        duracion=args.duracion,
    )

    if args.exportar:
        contenido = exportar_secuencia(secuencia, args.exportar)
        Path(args.output).write_text(contenido, encoding="utf-8")
        print(f"✅ Secuencia exportada a: {args.output}")
    else:
        mostrar_preview(secuencia)


if __name__ == "__main__":
    main()
