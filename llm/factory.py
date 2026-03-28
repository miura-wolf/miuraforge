import os
import sys

# Permitir ejecución directa desde la carpeta llm/ (Ajuste Táctico)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from llm.providers import GeminiProvider, NvidiaProvider, GroqProvider, ResilientProvider

class LLMFactory:
    @staticmethod
    def get_brain(task_name):
        """
        Asigna el cerebro perfecto para cada misión, alineado con la estrategia NVIDIA 2026.
        """
        # 1. El Explorador (OSINT y Psicología)
        # CAPA 1: Detección de tendencias (DeepSeek-V3.2 / V3.1)
        if task_name == "research_trends":
            return ResilientProvider(tiers=[
                NvidiaProvider(model_name="deepseek-ai/deepseek-v3.2"),
                GeminiProvider()
            ])
        
        # CAPA 2: Clasificación Batch (GLM 5 - Alta eficiencia)
        elif task_name == "research_batch":
            return ResilientProvider(tiers=[
                NvidiaProvider(model_name="z-ai/glm5"), 
                GeminiProvider(),
                GroqProvider()
            ])

        elif task_name == "research":
            return ResilientProvider(tiers=[
                NvidiaProvider(model_name="deepseek-ai/deepseek-v3.2"),
                GeminiProvider(),
                GroqProvider()
            ])
        
        # 2. Lectura de PDFs y Documentación (Gemini)
        elif task_name == "pdf_reader":
            return GeminiProvider()
        
        # 3. El Arquitecto (Redacción de Guiones)
        # Mistral Large 3: Precisión narrativa y frialdad industrial.
        elif task_name == "architect":
            return NvidiaProvider(model_name="mistralai/mistral-large-3-675b-instruct-2512")
        
        # 4. El Director Visual (Estética Chiaroscuro)
        # Llama 3.2 Vision: El ojo entrenado para descripción de escenas.
        elif task_name == "visual":
            return ResilientProvider(tiers=[
                NvidiaProvider(model_name="meta/llama-3.2-11b-vision-instruct"),
                GeminiProvider()
            ])
            
        # 5. El Auditor (Control de Calidad Doctrinal)
        # DeepSeek R1: Razonamiento puro para detectar "chatarra" y lenguaje suave.
        elif task_name == "auditor":
            return NvidiaProvider(model_name="deepseek-ai/deepseek-r1-distill-qwen-32b")
            
        # 6. El Estratega de Despliegue (SEO & Metadata)
        # Gemma 3: Modernidad y ganchos virales.
        elif task_name == "deployer":
            return NvidiaProvider(model_name="google/gemma-3-27b-it")
            
        # 7. El Emisario (Personalización de Emails)
        elif task_name == "emissary":
            return NvidiaProvider(model_name="deepseek-ai/deepseek-v3.2")
            
        # 8. El Cazador de Merch (Prompts de Imagen)
        # Gemma 3 es excelente para prompts creativos de imagen.
        elif task_name == "merch":
            return ResilientProvider(tiers=[
                NvidiaProvider(model_name="google/gemma-3-27b-it"),
                NvidiaProvider(model_name="deepseek-ai/deepseek-v3.2")
            ])
            
        else:
            return GeminiProvider()

if __name__ == "__main__":
    # Test de alineación estratégica
    print("\n🛡️ [Prueba de Factory] Verificando asignación de cerebros...")
    tasks = ["research", "architect", "auditor", "visual", "deployer"]
    
    for task in tasks:
        brain = LLMFactory.get_brain(task)
        model = "Unknown"
        if hasattr(brain, 'model'):
            model = brain.model
        elif hasattr(brain, 'tiers'):
            first_tier = brain.tiers[0]
            model = getattr(first_tier, 'model', 'Resilient/Multi-Tier')
            
        print(f"🔹 Tarea: {task:10} -> Cerebro: {type(brain).__name__:18} -> Modelo: {model}")