"""
marketing/launch_timing.py — MiuraForge Marketing Toolkit
===========================================================
Calculadora de timing óptimo para lanzamientos.

Analiza:
- Fechas óptimas basadas en audiencia
- Evitar holidays y competencias
- Ventanas de atención del nicho
- Cronograma de preparación pre-lanzamiento

Uso:
    python -m marketing.launch_timing --calcular --tipo producto
    python -m marketing.launch_timing --cronograma --semanas 8
    python -m marketing.launch_timing --auditoria "2026-05-15"
"""

import sys
import argparse
from pathlib import Path
from typing import Optional
from datetime import datetime, timedelta
import json
import re

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from llm.factory import LLMFactory

# ---------------------------------------------------------------------------
# CONFIGURACIÓN DE TIMING
# ---------------------------------------------------------------------------

FERIADOS_ARGENTINA_2026 = [
    "2026-01-01",  # Año Nuevo
    "2026-03-24",  # Memoria
    "2026-04-02",  # Malvinas
    "2026-05-01",  # Trabajador
    "2026-05-25",  # Revolución
    "2026-06-20",  # Belgrano
    "2026-07-09",  # Independencia
    "2026-08-17",  # San Martín
    "2026-10-12",  # Raza
    "2026-12-08",  # Inmaculada
    "2026-12-25",  # Navidad
]

EVENTOS_DEPORTIVOS_2026 = [
    {"fecha": "2026-06-11", "evento": "Mundial Fútbol inicio", "impacto": "alto"},
    {"fecha": "2026-07-11", "evento": "Mundial Fútbol final", "impacto": "alto"},
]

COMPETENCIAS_DIGITALES = [
    {"periodo": "noviembre", "evento": "Black Friday / Cyber Monday", "impacto": "alto"},
    {"periodo": "enero", "evento": "Resoluciones de Año Nuevo", "impacto": "medio"},
]

TIPOS_LANZAMIENTO = {
    "producto": {
        "nombre": "Producto Digital",
        "lead_time_semanas": 4,
        "fases": ["awareness", "interés", "decisión", "cierre"],
        "evitar_feriados": True,
    },
    "servicio": {
        "nombre": "Servicio/Servicio",
        "lead_time_semanas": 6,
        "fases": ["autoridad", "prueba", "oferta", "cierre"],
        "evitar_feriados": True,
    },
    "contenido": {
        "nombre": "Contenido Major",
        "lead_time_semanas": 2,
        "fases": ["anticipación", "lanzamiento", "amplificación"],
        "evitar_feriados": False,
    },
    "evento": {
        "nombre": "Evento/Live",
        "lead_time_semanas": 3,
        "fases": ["registro", "reminder", "ejecución", "seguimiento"],
        "evitar_feriados": True,
    },
}

# ---------------------------------------------------------------------------
# PROMPTS PARA LLM
# ---------------------------------------------------------------------------

PROMPT_TIMING = """Eres el Estratega de Launch Timing de Disciplina en Acero.

Tu trabajo es recomendar la fecha óptima de lanzamiento basándote en:
1. Evitar conflictos con holidays/eventos
2. Maximizar atención de la audiencia
3. Considerar comportamiento del nicho masculino

Tipo de lanzamiento: {tipo_lanzamiento}
Lead time necesario: {lead_time} semanas
Restricciones: {restricciones}
Feriados a evitar: {feriados}
Eventos deportivos: {eventos}

Analiza y devuelve:

```json
{{
    "fecha_recomendada": "YYYY-MM-DD",
    "razon": "por qué esta fecha es óptima",
    "ventana_optima": {{
        "inicio": "YYYY-MM-DD",
        "fin": "YYYY-MM-DD"
    }},
    "fechas_evitar": [
        {{
            "fecha": "YYYY-MM-DD",
            "motivo": "razón"
        }}
    ],
    "factor_nicho": {{
        "consideracion": "comportamiento típico del nicho en esta época",
        "riesgo": "bajo|medio|alto"
    }},
    "alternativas": [
        {{
            "fecha": "YYYY-MM-DD",
            "pros": "ventajas",
            "contras": "desventajas"
        }}
    ]
}}
```

Responde SOLO con el JSON."""

PROMPT_CRONOGRAMA = """Eres el Planificador de Cronogramas de Disciplina en Acero.

Generá un cronograma detallado de {semanas} semanas para lanzamiento tipo {tipo}.

Fases: {fases}

Devuelve:

```json
{{
    "cronograma": [
        {{
            "semana": 1,
            "fase": "nombre de fase",
            "objetivo": "qué lograr",
            "acciones": [
                "acción 1",
                "acción 2"
            ],
            "kpis": [
                "métrica a medir"
            ],
            "deliverables": [
                "entregable concreto"
            ]
        }}
    ],
    "hitos_criticos": [
        {{
            "semana": X,
            "hito": "descripción",
            "dependencias": "qué debe estar listo antes"
        }}
    ],
    "contingencias": [
        {{
            "riesgo": "posible problema",
            "mitigacion": "cómo prevenir"
        }}
    ]
}}
```

Responde SOLO con el JSON."""

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


def _es_feriado(fecha: datetime) -> bool:
    """Verifica si una fecha es feriado en Argentina."""
    fecha_str = fecha.strftime("%Y-%m-%d")
    return fecha_str in FERIADOS_ARGENTINA_2026


def _get_llm():
    """Obtiene instancia del LLM."""
    return LLMFactory.get_provider()


# ---------------------------------------------------------------------------
# FUNCIONES PRINCIPALES
# ---------------------------------------------------------------------------


def calcular_fecha_optima(
    tipo: str = "producto",
    semanas_lead: Optional[int] = None,
    evitar_feriados: bool = True,
) -> dict:
    """
    Calcula la fecha óptima de lanzamiento.

    Args:
        tipo: Tipo de lanzamiento
        semanas_lead: Semanas de preparación (opcional)
        evitar_feriados: Si hay que evitar feriados

    Returns:
        Dict con fecha recomendada y análisis
    """
    if tipo not in TIPOS_LANZAMIENTO:
        print(f"⚠️ Tipo '{tipo}' no válido. Disponibles: {list(TIPOS_LANZAMIENTO.keys())}")
        return {}

    config = TIPOS_LANZAMIENTO[tipo]
    lead = semanas_lead or config["lead_time_semanas"]
    llm = _get_llm()

    # Preparar contexto
    feriados_cercanos = [
        f for f in FERIADOS_ARGENTINA_2026 if datetime.strptime(f, "%Y-%m-%d") > datetime.now()
    ][:5]

    eventos = [e["evento"] for e in EVENTOS_DEPORTIVOS_2026]

    prompt = PROMPT_TIMING.format(
        tipo_lanzamiento=config["nombre"],
        lead_time=lead,
        restricciones="Evitar feriados" if evitar_feriados else "Sin restricción de feriados",
        feriados=", ".join(feriados_cercanos),
        eventos=", ".join(eventos),
    )

    print(f"📅 Calculando fecha óptima para: {config['nombre']}...")
    response = llm.generate(prompt)

    resultado = _extraer_json(response)
    if not resultado:
        print("⚠️ No se pudo parsear respuesta del LLM")
        return {"error": "parse_error", "raw_response": response}

    return resultado


def generar_cronograma(
    tipo: str = "producto",
    semanas: Optional[int] = None,
) -> dict:
    """
    Genera cronograma detallado de lanzamiento.

    Args:
        tipo: Tipo de lanzamiento
        semanas: Duración en semanas (opcional)

    Returns:
        Dict con cronograma completo
    """
    if tipo not in TIPOS_LANZAMIENTO:
        print(f"⚠️ Tipo '{tipo}' no válido")
        return {}

    config = TIPOS_LANZAMIENTO[tipo]
    duracion = semanas or config["lead_time_semanas"]
    llm = _get_llm()

    prompt = PROMPT_CRONOGRAMA.format(
        semanas=duracion,
        tipo=config["nombre"],
        fases=", ".join(config["fases"]),
    )

    print(f"📋 Generando cronograma de {duracion} semanas...")
    response = llm.generate(prompt)

    resultado = _extraer_json(response)
    if not resultado:
        return {"error": "parse_error"}

    return resultado


def auditar_fecha(
    fecha_str: str,
    tipo: str = "producto",
) -> dict:
    """
    Audita una fecha propuesta de lanzamiento.

    Args:
        fecha_str: Fecha propuesta (YYYY-MM-DD)
        tipo: Tipo de lanzamiento

    Returns:
        Dict con auditoría de la fecha
    """
    try:
        fecha = datetime.strptime(fecha_str, "%Y-%m-%d")
    except ValueError:
        return {"error": "Formato de fecha inválido. Usá YYYY-MM-DD"}

    problemas = []
    advertencias = []
    beneficios = []

    # Verificar feriados
    if _es_feriado(fecha):
        problemas.append(f"⚠️ {fecha_str} es feriado en Argentina")

    # Verificar día de la semana
    if fecha.weekday() == 6:  # Domingo
        advertencias.append("Domingo: menor engagement típico")
    elif fecha.weekday() == 5:  # Sábado
        advertencias.append("Sábado: engagement variable")

    # Verificar cercanía a feriados
    for feriado in FERIADOS_ARGENTINA_2026:
        f_date = datetime.strptime(feriado, "%Y-%m-%d")
        delta = abs((fecha - f_date).days)
        if 0 < delta <= 3:
            advertencias.append(f"Feriado cercano: {feriado} ({delta} días)")

    # Verificar eventos deportivos
    for evento in EVENTOS_DEPORTIVOS_2026:
        e_date = datetime.strptime(evento["fecha"], "%Y-%m-%d")
        delta = abs((fecha - e_date).days)
        if delta <= 7:
            problemas.append(
                f"⚽ {evento['evento']} cercano ({delta} días) - impacto {evento['impacto']}"
            )

    # Evaluar día óptimo
    if fecha.weekday() in [1, 2, 3]:  # Martes, Miércoles, Jueves
        beneficios.append("✅ Día óptimo para lanzamientos (martes-jueves)")

    # Evaluar mes
    mes = fecha.month
    if mes in [1, 2]:  # Enero-Febrero
        advertencias.append("Enero-Febrero: tracción inicial lenta (vacaciones)")
    elif mes == 11:  # Noviembre
        advertencias.append("Noviembre: Black Friday compite por atención")
    elif mes in [3, 4, 9, 10]:
        beneficios.append("✅ Mes con buena recepción para el nicho")

    score = 100 - (len(problemas) * 20) - (len(advertencias) * 10) + (len(beneficios) * 5)
    score = max(0, min(100, score))

    return {
        "fecha": fecha_str,
        "dia_semana": fecha.strftime("%A"),
        "score": score,
        "veredicto": "APROBADO"
        if score >= 70
        else "CON RESERVAS"
        if score >= 50
        else "NO RECOMENDADO",
        "problemas": problemas,
        "advertencias": advertencias,
        "beneficios": beneficios,
    }


def mostrar_cronograma(cronograma: dict) -> None:
    """Muestra cronograma formateado en consola."""
    print("\n" + "=" * 70)
    print("📅 CRONOGRAMA DE LANZAMIENTO")
    print("=" * 70)

    for semana in cronograma.get("cronograma", []):
        num = semana.get("semana", "N/A")
        fase = semana.get("fase", "Sin fase")
        objetivo = semana.get("objetivo", "")

        print(f"\n📆 SEMANA {num} — {fase.upper()}")
        print(f"   Objetivo: {objetivo}")

        acciones = semana.get("acciones", [])
        if acciones:
            print("   Acciones:")
            for acc in acciones[:3]:
                print(f"      • {acc}")

        kpis = semana.get("kpis", [])
        if kpis:
            print(f"   KPIs: {', '.join(kpis[:3])}")

    # Hitos
    if "hitos_criticos" in cronograma:
        print("\n🎯 HITOS CRÍTICOS:")
        for hito in cronograma["hitos_criticos"]:
            print(f"   Semana {hito.get('semana', 'N/A')}: {hito.get('hito', '')}")

    # Contingencias
    if "contingencias" in cronograma:
        print("\n⚠️ CONTINGENCIAS:")
        for cont in cronograma["contingencias"]:
            print(f"   Riesgo: {cont.get('riesgo', '')}")
            print(f"   Mitigación: {cont.get('mitigacion', '')}")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main():
    parser = argparse.ArgumentParser(description="Calculadora de Launch Timing")
    parser.add_argument(
        "--calcular",
        action="store_true",
        help="Calcular fecha óptima de lanzamiento",
    )
    parser.add_argument(
        "--cronograma",
        action="store_true",
        help="Generar cronograma de lanzamiento",
    )
    parser.add_argument(
        "--auditoria",
        type=str,
        help="Auditar fecha específica (YYYY-MM-DD)",
    )
    parser.add_argument(
        "--tipo",
        choices=list(TIPOS_LANZAMIENTO.keys()),
        default="producto",
        help="Tipo de lanzamiento",
    )
    parser.add_argument("--semanas", type=int, help="Duración en semanas")
    parser.add_argument("--no-evitar-feriados", action="store_true", help="No evitar feriados")

    args = parser.parse_args()

    if args.calcular:
        resultado = calcular_fecha_optima(
            tipo=args.tipo,
            semanas_lead=args.semanas,
            evitar_feriados=not args.no_evitar_feriados,
        )
        print(json.dumps(resultado, indent=2, ensure_ascii=False))

    elif args.cronograma:
        resultado = generar_cronograma(tipo=args.tipo, semanas=args.semanas)
        mostrar_cronograma(resultado)

    elif args.auditoria:
        resultado = auditar_fecha(args.auditoria, args.tipo)
        print(json.dumps(resultado, indent=2, ensure_ascii=False))

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
