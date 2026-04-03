"""
marketing/content_gap_analysis.py — MiuraForge Marketing Toolkit
==================================================================
Analizador de gaps de contenido para identificar oportunidades SEO.

Detecta:
- Keywords objetivo sin contenido asociado
- Temas del nicho no cubiertos
- Competidores rankeando donde nosotros no
- Oportunidades de contenido basadas en dolores de audiencia

Uso:
    python -m marketing.content_gap_analysis --analizar
    python -m marketing.content_gap_analysis --competidores "Hamza,1STMAN"
    python -m marketing.content_gap_analysis --oportunidades
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
# CONFIGURACIÓN DE NICHOS Y TEMAS
# ---------------------------------------------------------------------------

NICHOS_CONFIG = {
    "disciplina_masculina": {
        "nombre": "Disciplina Masculina",
        "temas_base": [
            "disciplina diaria",
            "rutinas de hombre",
            "productividad masculina",
            "mindset de acero",
            "autocontrol",
            "hábitos estoicos",
            "objetivos hombres",
            "fuerza mental",
            "resiliencia",
            "propósito de vida hombre",
        ],
        "competidores_referencia": [
            "Hamza Ahmed",
            "1STMAN",
            "FarFromWeak",
            "Improvement Pill",
        ],
        "dolores_comunes": [
            "procrastinación crónica",
            "falta de motivación",
            "adicción a distracciones",
            "vida sin propósito",
            "miedo al fracaso",
            "comparación con otros",
        ],
    },
    "fitness_masculino": {
        "nombre": "Fitness Masculino",
        "temas_base": [
            "entrenamiento hombres",
            "ganar músculo",
            "fuerza funcional",
            "dieta hombres",
            "suplementación",
            "testosterona natural",
            "estética masculina",
        ],
        "competidores_referencia": [
            "Jeff Nippard",
            "Athlean-X",
            "Jeff Cavalier",
        ],
        "dolores_comunes": [
            "estancamiento en gimnasio",
            "falta de energía",
            "complexo físico",
            "no ver resultados",
        ],
    },
}

# ---------------------------------------------------------------------------
# PROMPTS PARA LLM
# ---------------------------------------------------------------------------

PROMPT_ANALISIS_GAP = """Eres el Analista de Content Gaps de Disciplina en Acero.

Tu trabajo es identificar oportunidades de contenido basándote en:
1. Los temas base del nicho
2. Los dolores comunes de la audiencia
3. Lo que los competidores están cubriendo

Nicho: {nicho}
Temas base: {temas_base}
Dolores comunes: {dolores}

Analiza y devuelve un JSON con la siguiente estructura:

```json
{{
    "gaps_criticos": [
        {{
            "tema": "nombre del tema",
            "motivo": "por qué es un gap crítico",
            "oportunidad_seo": "potencial SEO (alto/medio/bajo)",
            "dolor_atendido": "qué dolor de audiencia atiende"
        }}
    ],
    "oportunidades_quick_wins": [
        {{
            "keyword": "keyword específica",
            "dificultad": "fácil/medio/difícil",
            "volumen_estimado": "alto/medio/bajo",
            "formato_sugerido": "blog/video/carrusel"
        }}
    ],
    "temas_oversaturated": [
        "temas ya muy cubiertos por competencia"
    ],
    "recomendacion_prioritaria": "tema #1 a atacar primero"
}}
```

Responde SOLO con el JSON, sin texto adicional."""

PROMPT_COMPETIDORES_GAP = """Eres el Analista de Competencia de Disciplina en Acero.

Analiza qué contenido están creando estos competidores y dónde tenemos gaps:

Competidores: {competidores}
Nicho: {nicho}

Devuelve un JSON con:

```json
{{
    "contenido_competidores": [
        {{
            "competidor": "nombre",
            "temas_fuertes": ["tema1", "tema2"],
            "formatos_usados": ["video", "blog", "shorts"],
            "gap_identificado": "qué NO están cubriendo"
        }}
    ],
    "oportunidades_robadas": [
        {{
            "tema": "tema que podemos capitalizar",
            "diferenciacion": "cómo lo hacemos mejor/distinto"
        }}
    ],
    "keywords_sin_atender": [
        "keywords que nadie está atacando"
    ]
}}
```

Responde SOLO con el JSON."""

# ---------------------------------------------------------------------------
# FUNCIONES AUXILIARES
# ---------------------------------------------------------------------------


def _extraer_json(texto: str) -> Optional[dict]:
    """Extrae JSON de respuesta del LLM (maneja markdown y texto extra)."""
    # Intentar parsear directo
    try:
        return json.loads(texto)
    except json.JSONDecodeError:
        pass

    # Buscar JSON en bloques de código
    json_match = re.search(r"```(?:json)?\s*([\s\S]*?)```", texto)
    if json_match:
        try:
            return json.loads(json_match.group(1).strip())
        except json.JSONDecodeError:
            pass

    # Buscar JSON sin bloques (objetos entre llaves)
    json_match = re.search(r"\{[\s\S]*\}", texto)
    if json_match:
        try:
            # Fix trailing commas
            clean = re.sub(r",\s*([}\]])", r"\1", json_match.group(0))
            return json.loads(clean)
        except json.JSONDecodeError:
            pass

    return None


def _get_llm():
    """Obtiene instancia del LLM."""
    return LLMFactory.get_provider()


# ---------------------------------------------------------------------------
# FUNCIONES PRINCIPALES
# ---------------------------------------------------------------------------


def analizar_gaps(nicho: str = "disciplina_masculina") -> dict:
    """
    Analiza gaps de contenido para un nicho específico.

    Args:
        nicho: Clave del nicho en NICHOS_CONFIG

    Returns:
        Dict con gaps_críticos, oportunidades_quick_wins, etc.
    """
    if nicho not in NICHOS_CONFIG:
        print(f"⚠️ Nicho '{nicho}' no encontrado. Disponibles: {list(NICHOS_CONFIG.keys())}")
        return {}

    config = NICHOS_CONFIG[nicho]
    llm = _get_llm()

    prompt = PROMPT_ANALISIS_GAP.format(
        nicho=config["nombre"],
        temas_base=", ".join(config["temas_base"]),
        dolores=", ".join(config["dolores_comunes"]),
    )

    print(f"🔍 Analizando gaps para: {config['nombre']}...")
    response = llm.generate(prompt)

    resultado = _extraer_json(response)
    if not resultado:
        print("⚠️ No se pudo parsear respuesta del LLM")
        return {"error": "parse_error", "raw_response": response}

    return resultado


def analizar_competidores(nicho: str = "disciplina_masculina") -> dict:
    """
    Analiza contenido de competidores para identificar gaps.

    Args:
        nicho: Clave del nicho en NICHOS_CONFIG

    Returns:
        Dict con contenido_competidores, oportunidades_robadas, etc.
    """
    if nicho not in NICHOS_CONFIG:
        print(f"⚠️ Nicho '{nicho}' no encontrado")
        return {}

    config = NICHOS_CONFIG[nicho]
    llm = _get_llm()

    competidores = ", ".join(config["competidores_referencia"])
    prompt = PROMPT_COMPETIDORES_GAP.format(
        competidores=competidores,
        nicho=config["nombre"],
    )

    print(f"🕵️ Analizando competidores: {competidores}...")
    response = llm.generate(prompt)

    resultado = _extraer_json(response)
    if not resultado:
        print("⚠️ No se pudo parsear respuesta del LLM")
        return {"error": "parse_error", "raw_response": response}

    return resultado


def generar_oportunidades(nicho: str = "disciplina_masculina") -> list[dict]:
    """
    Genera lista priorizada de oportunidades de contenido.

    Args:
        nicho: Clave del nicho

    Returns:
        Lista de oportunidades ordenadas por prioridad
    """
    # Analizar gaps propios
    gaps = analizar_gaps(nicho)
    # Analizar competencia
    comp = analizar_competidores(nicho)

    oportunidades = []

    # Agregar gaps críticos
    if "gaps_criticos" in gaps:
        for gap in gaps["gaps_criticos"]:
            oportunidades.append(
                {
                    "tema": gap.get("tema", ""),
                    "tipo": "gap_critico",
                    "prioridad": "ALTA",
                    "oportunidad_seo": gap.get("oportunidad_seo", "medio"),
                    "dolor": gap.get("dolor_atendido", ""),
                }
            )

    # Agregar quick wins
    if "oportunidades_quick_wins" in gaps:
        for qw in gaps["oportunidades_quick_wins"]:
            oportunidades.append(
                {
                    "tema": qw.get("keyword", ""),
                    "tipo": "quick_win",
                    "prioridad": "MEDIA" if qw.get("dificultad") == "medio" else "ALTA",
                    "formato": qw.get("formato_sugerido", "blog"),
                    "volumen": qw.get("volumen_estimado", "medio"),
                }
            )

    # Agregar oportunidades de competencia
    if "oportunidades_robadas" in comp:
        for opp in comp["oportunidades_robadas"]:
            oportunidades.append(
                {
                    "tema": opp.get("tema", ""),
                    "tipo": "competencia_gap",
                    "prioridad": "ALTA",
                    "diferenciacion": opp.get("diferenciacion", ""),
                }
            )

    # Ordenar por prioridad
    prioridad_orden = {"ALTA": 0, "MEDIA": 1, "BAJA": 2}
    oportunidades.sort(key=lambda x: prioridad_orden.get(x.get("prioridad", "BAJA"), 2))

    return oportunidades


def mostrar_reporte(oportunidades: list[dict]) -> None:
    """Muestra reporte formateado de oportunidades."""
    print("\n" + "=" * 60)
    print("📊 REPORTE DE OPORTUNIDADES DE CONTENIDO")
    print("=" * 60)

    if not oportunidades:
        print("⚠️ No se encontraron oportunidades")
        return

    # Agrupar por tipo
    por_tipo = {}
    for opp in oportunidades:
        tipo = opp.get("tipo", "otros")
        if tipo not in por_tipo:
            por_tipo[tipo] = []
        por_tipo[tipo].append(opp)

    for tipo, items in por_tipo.items():
        print(f"\n🎯 {tipo.upper().replace('_', ' ')} ({len(items)})")
        print("-" * 40)
        for i, item in enumerate(items[:5], 1):  # Mostrar top 5 por tipo
            tema = item.get("tema", "Sin tema")
            prioridad = item.get("prioridad", "N/A")
            emoji = "🔴" if prioridad == "ALTA" else "🟡" if prioridad == "MEDIA" else "🟢"
            print(f"  {i}. {emoji} {tema}")
            if "dolor" in item and item["dolor"]:
                print(f"     💔 Dolor: {item['dolor']}")
            if "diferenciacion" in item and item["diferenciacion"]:
                print(f"     ✨ Diferenciación: {item['diferenciacion']}")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main():
    parser = argparse.ArgumentParser(description="Analizador de Content Gaps para MiuraForge")
    parser.add_argument(
        "--analizar",
        action="store_true",
        help="Analizar gaps de contenido",
    )
    parser.add_argument(
        "--competidores",
        action="store_true",
        help="Analizar contenido de competidores",
    )
    parser.add_argument(
        "--oportunidades",
        action="store_true",
        help="Generar lista de oportunidades priorizadas",
    )
    parser.add_argument(
        "--nicho",
        default="disciplina_masculina",
        choices=list(NICHOS_CONFIG.keys()),
        help="Nicho a analizar",
    )

    args = parser.parse_args()

    if args.analizar:
        resultado = analizar_gaps(args.nicho)
        print(json.dumps(resultado, indent=2, ensure_ascii=False))

    elif args.competidores:
        resultado = analizar_competidores(args.nicho)
        print(json.dumps(resultado, indent=2, ensure_ascii=False))

    elif args.oportunidades:
        oportunidades = generar_oportunidades(args.nicho)
        mostrar_reporte(oportunidades)

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
