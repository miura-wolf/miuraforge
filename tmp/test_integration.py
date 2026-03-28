import os
import sys
from pathlib import Path

# Inyectar root
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.voice_director import VoiceDirector

def test_pipeline_integrado():
    print("🚀 Probando Integración de AudioAuditor en VoiceDirector...")
    
    director = VoiceDirector()
    
    texto = "Este es un golpe de acero... La disciplina no pide permiso... Se ejecuta con precisión industrial."
    output_path = "output/test_integracion_auditoria.wav"
    
    # Asegurar que el directorio de salida existe
    os.makedirs("output", exist_ok=True)
    
    print(f"🎙️ Generando voz para: '{texto}'")
    success = director.generar_voz(texto, output_path)
    
    if success:
        print(f"✅ ÉXITO: Archivo generado en {output_path}")
        # Verificar si es estéreo
        import soundfile as sf
        data, sr = sf.read(output_path)
        print(f"   Propiedades: Canales={data.shape[1] if len(data.shape)>1 else 1} | SR={sr}")
    else:
        print("❌ FALLO: No se pudo generar el archivo.")

if __name__ == "__main__":
    test_pipeline_integrado()
