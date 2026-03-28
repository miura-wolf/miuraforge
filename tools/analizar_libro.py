import os
import json
from llm.factory import LLMFactory
from dotenv import load_dotenv

load_dotenv()

class BookAnalyst:
    def __init__(self):
        # Usamos el cerebro PDF_READER (Gemini) porque es el único que puede deglutir PDFs complejos
        self.brain = LLMFactory.get_brain("pdf_reader")
    
    def analizar_manuscrito(self, pdf_path):
        """Escanea el libro y extrae el ADN doctrinal para la forja."""
        if not os.path.exists(pdf_path):
            print(f"❌ [Analista] El manuscrito no está en el búnker: {pdf_path}")
            return None
        
        print(f"📖 [Analista] Abriendo el manuscrito: {os.path.basename(pdf_path)}...")
        
        prompt = """
        Actúa como el Analista Jefe de Disciplina en Acero. Tu misión es extraer la Inteligencia Doctrinal de este libro.
        
        1. Identifica los 4 DOLORES MAESTROS que menciona el libro.
        2. Para cada dolor, extrae:
           - El Síntoma (Lo que el hombre siente).
           - El Mecanismo (Por qué sucede esto en la mente).
           - La Secuencia de Interrupción (La solución física prescrita).
        3. Extrae 10 'Frases de Acero' (Hitos narrativos de altísimo impacto emocional).
        4. Identifica las metáforas visuales recurrentes (ej: forja, desierto, espejo, etc.).
        
        Responde en un formato estructurado para ser inyectado en la memoria de la Forja (JSON).
        """
        
        try:
            # GeminiProvider soporta pasar una lista de archivos como contexto
            resultado = self.brain.generate(prompt, context_files=[pdf_path])
            return resultado
        except Exception as e:
            print(f"⚠️ [Analista] Fallo en la lectura del manuscrito: {e}")
            return None

if __name__ == "__main__":
    analyst = BookAnalyst()
    ruta_libro = r"d:\YT\MiuraForge\Libro\ElHombreQueDejoDeMentirse_v2.pdf"
    analisis = analyst.analizar_manuscrito(ruta_libro)
    
    if analisis:
        # Guardamos el ADN en una ubicación segura para que el resto de agentes lo consulten
        os.makedirs("doctrina", exist_ok=True)
        with open("doctrina/libro1_adn.txt", "w", encoding="utf-8") as f:
            f.write(analisis)
        print("✅ [Analista] ADN Doctrinal extraído y guardado en 'doctrina/libro1_adn.txt'.")
        print("\n--- RESUMEN DE LA DOCTRINA ---")
        print(analisis[:1000] + "...")
