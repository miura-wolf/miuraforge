import re

from rich.console import Console

console = Console()

# ─── UMBRAL DE CALIDAD PARA DATASET DE FINE-TUNING ───────────────────────────
# Solo guiones con Coherencia >= 8 Y ADN >= 8 se marcan como "aprobado".
# El resto queda en "revision" para revisión manual del Soberano.
UMBRAL_COHERENCIA = 8
UMBRAL_ADN = 8
# ─────────────────────────────────────────────────────────────────────────────


def safe_int(val):
    """Extrae el primer número de un string. Útil para métricas como '8/10'."""
    try:
        if not val:
            return 0
        # Extraer la PRIMERA secuencia de dígitos (ej: "8/10" → 8, "9 puntos" → 9)
        numeros = re.findall(r"\d+", str(val))
        return int(numeros[0]) if numeros else 0
    except Exception:
        return 0


def _evaluar_calidad(db, timestamp_video):
    """
    Lee las métricas del Auditor desde Sheets y determina el estado final.
    Retorna: ("aprobado", coherencia, adn) o ("revision", coherencia, adn)
    """
    try:
        resultado = db.obtener_resultados_auditoria(timestamp_video)
        coherencia = safe_int(resultado.get("coherencia"))
        adn = safe_int(resultado.get("adn_acero"))

        if coherencia >= UMBRAL_COHERENCIA and adn >= UMBRAL_ADN:
            return "aprobado", coherencia, adn
        else:
            return "revision", coherencia, adn
    except Exception as e:
        console.print(
            f"[yellow]⚠️ No se pudieron leer métricas del Auditor para {timestamp_video}: {e}[/]"
        )
        # Si no se pueden leer métricas, va a revisión por precaución
        return "revision", 0, 0
