import os
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

from llm.factory import LLMFactory
from core.forge_blog import PROMPT_ALCHEMIST

# El texto a usar como base
CUERPO_RAW = """El libro Hábitos Atómicos de James Clear es un clásico sobre productividad. Habla de que las pequeñas mejoras del 1% diario se acumulan con el tiempo para crear grandes cambios. Se enfoca en los sistemas más que en las metas. Muestra cómo hacer que los hábitos sean obvios, atractivos, sencillos y satisfactorios. Habla sobre la motivación y cómo el ambiente importa más que la fuerza de voluntad. Sin embargo, desde la perspectiva de Disciplina en Acero, este libro falla si no hay un cambio de identidad primero. De nada sirve un buen sistema temporal si el hombre sigue sintiéndose insuficiente por dentro y huyendo de la realidad."""

TITULO = "Hábitos Atómicos: Por qué el 1% diario te mantiene mediocre sin identidad de acero"

# Mapeamos los modelos que queremos probar a las tareas del factory
MODELOS_A_PROBAR = {
    "Gemma-3 (SEO/Ganchos)": "deployer",
    "Mistral-Large-3 (Arquitecto)": "architect",
    "DeepSeek-V3.2 (Analista)": "research"
}

def correr_comparativa():
    print("⚔️ INICIANDO PRUEBA COMPARATIVA DE MODELOS PARA BLOG ⚔️\n")
    
    docs_dir = BASE_DIR / "Docs" / "Comparativa_Blog"
    docs_dir.mkdir(parents=True, exist_ok=True)
    
    for nombre, rol in MODELOS_A_PROBAR.items():
        print(f"👉 Probando: {nombre} (Rol: {rol})")
        
        try:
            brain = LLMFactory.get_brain(rol)
            prompt = PROMPT_ALCHEMIST.format(titulo=TITULO, cuerpo_raw=CUERPO_RAW)
            
            print(f"   Generando reseña...")
            resultado = brain.generate(prompt)
            
            archivo_salida = docs_dir / f"Habitos_Atomicos_{rol}.md"
            with open(archivo_salida, "w", encoding="utf-8") as f:
                f.write(f"# Modelo: {nombre}\n\n{resultado}")
            
            print(f"   ✅ Guardado en: {archivo_salida.name}\n")
        
        except Exception as e:
            print(f"   ❌ Error con {nombre}: {e}\n")

if __name__ == "__main__":
    correr_comparativa()
