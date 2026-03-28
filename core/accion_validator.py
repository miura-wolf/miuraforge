"""
⚔️ VALIDADOR DE ACCIONES MIURA - Disciplina en Acero
Este módulo implementa la Directiva 2: Los CTAs deben ser acciones físicas concretas.
Cualquier verbo pasivo, terapéutico o abstracto es rechazado por el Yunque.
"""

import re

# Verbos que implican movimiento o acción física real en el mundo real
VERBOS_FISICOS = [
    "abre", "escribe", "bloquea", "elimina", 
    "calcula", "levanta", "corre", "llama",
    "mira", "apunta", "cierra", "empieza",
    "borra", "descarga", "limpia", "apaga",
    "camina", "registra", "sigue", "deja",
    "toma", "pon", "haz", "rompe", "forja"
]

# Verbos que inducen a la parálisis por análisis o languidez mental
VERBOS_PROHIBIDOS = [
    "piensa", "considera", "evalúa", "planea",
    "podrías", "quizás", "tal vez", "intenta",
    "siente", "imagina", "reflexiona", "analiza",
    "espera", "cree", "desea", "posiblemente"
]

def validar_cta(cta: str) -> tuple[bool, list[str]]:
    """
    Valida que el CTA sea físico y concreto.
    Retorna: (es_valido, lista_de_problemas)
    """
    if not cta or not isinstance(cta, str):
        return False, ["CTA vacío o inválido"]

    problemas = []
    cta_lower = cta.lower()
    
    # 1. Verificar verbos prohibidos (Acciones pasivas)
    for verbo in VERBOS_PROHIBIDOS:
        # Usamos \b para asegurar que es la palabra completa
        if re.search(rf"\b{verbo}\b", cta_lower):
            problemas.append(f"❌ Verbo prohibitivo detectado: '{verbo}' (Induce parálisis)")
    
    # 2. Verificar presencia de verbos físicos
    tiene_verbo_fisico = any(re.search(rf"\b{v}\b", cta_lower) for v in VERBOS_FISICOS)
    
    if not tiene_verbo_fisico:
        # Si no tiene un verbo físico conocido, marcamos como advertencia o fallo según rigor
        problemas.append("❌ No contiene verbos de acción física conocidos por el Yunque.")
    
    # 3. Longitud (Un CTA Miura es directo)
    palabras = cta.split()
    if len(palabras) > 15:
        problemas.append(f"⚠️ CTA demasiado largo ({len(palabras)} palabras). Debe ser un golpe seco.")

    return len(problemas) == 0, problemas

if __name__ == "__main__":
    # Test de batalla
    test_cases = [
        "Piensa en lo que podrías hacer mañana.",
        "Escribe ahora mismo tu mayor vergüenza en un papel.",
        "Elimina las aplicaciones que te drenan la dopamina.",
        "Tal vez deberías intentar correr un poco.",
        "Bloquea ese contacto ahora.",
        "Analiza tu situación y busca una solución."
    ]
    
    print("🛡️ [Prueba de Calidad Miura] Validando CTAs...")
    for cta in test_cases:
        valido, errs = validar_cta(cta)
        status = "✅ [APROBADO]" if valido else "❌ [RECHAZADO]"
        print(f"\nCTA: '{cta}'")
        print(f"Estado: {status}")
        if not valido:
            for e in errs:
                print(f"  - {e}")
