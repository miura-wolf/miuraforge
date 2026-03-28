import os
import sys
from pathlib import Path

# Inyectar root
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.visual_director import VisualDirector
from dotenv import load_dotenv

load_dotenv()

def test_visual_bridge():
    print("🚀 Probando Puente de Sincronización Local -> Drive...")
    
    director = VisualDirector()
    
    # Datos de prueba
    prompt = "Cinematic industrial landscape, molten steel pouring into a miura shape, sparks, hyper-realistic, 8k"
    job_id = "test_001"
    
    print(f"🔨 Generando señal de trabajo para Colab...")
    job_path = director.forjar_video_colab(prompt, job_id)
    
    if os.path.exists(job_path):
        print(f"✅ ÉXITO: Archivo de señal creado en: {job_path}")
        print("   Contenido del JSON:")
        import json
        with open(job_path, "r") as f:
            print(json.dumps(json.load(f), indent=2))
            
        print("\n⏳ Ahora el siguiente paso es que Google Drive sincronice este archivo.")
        print("   Y que el Notebook de Colab lo detecte.")
    else:
        print(f"❌ FALLO: No se encontró el archivo en {job_path}")

if __name__ == "__main__":
    test_visual_bridge()
