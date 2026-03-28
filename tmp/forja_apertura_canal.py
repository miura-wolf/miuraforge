import os
import sys
import time
from pathlib import Path

# Inyectar root
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.database import Database
from core.architect import Architect
from core.voice_director import VoiceDirector
from core.visual_director import VisualDirector
from llm.factory import LLMFactory

def forja_apertura_canal():
    print("🚀 [Gran Visir] Iniciando Forja de la Trilogía de Apertura...")
    
    db = Database()
    arquitecto = Architect(db)
    andres_voice = VoiceDirector()
    visual_dir = VisualDirector()
    auditor_brain = LLMFactory.get_brain("auditor")
    
    # Leer el documento de inicio
    ruta_inicio = r"D:\YT\MiuraForge\Docs\Inicios del canal.txt"
    with open(ruta_inicio, "r", encoding="utf-8") as f:
        doc_inicio = f.read()

    videos = [
        {
            "id": "Apertura_01",
            "tema": "El Manifiesto de Disciplina en Acero",
            "objetivo": "Un llamado a las armas. No motivacion barata, sino disciplina forjada. Presentar la voz y el canal."
        },
        {
            "id": "Apertura_02",
            "tema": "El Código de Comunicación (Sultán y Gran Visir)",
            "objetivo": "Explicar que el lenguaje crea realidades. Adoptar la mentalidad de soberano."
        },
        {
            "id": "Apertura_03",
            "tema": "La Hoja de Ruta del Imperio",
            "objetivo": "Promesa de valor. 40 guiones, psicologia del consumidor, dominio propio. Llamado a lead magnet."
        }
    ]

    for video in videos:
        timestamp = f"INICIO_{video['id']}_{int(time.time())}"
        print(f"\n=======================================================")
        print(f"🎬 [Trilogía] Pre-producción de: {video['tema']}")
        print(f"=======================================================")
        
        # 1. ARQUITECTO GENERA
        print("\n1. 🖊️ ARQUITECTO: Escribiendo guion...")
        instruccion_arquitecto = f"""
        CONSEJOS DEL VISIR (Documento base):
        {doc_inicio}
        
        OBJETIVO ESPECÍFICO PARA ESTE SHORT:
        {video['objetivo']}
        
        Escribe un guion corto (max 100 palabras) para este Short. Debe usar la voz de Andrés. 
        Aplica la puntuación de acero (usar puntos suspensivos en lugar de comas, oraciones cortas).
        """
        
        guion_original = arquitecto.brain.generate(instruccion_arquitecto, temperature=0.3)
        print(f"\n[GUION BORRADOR]:\n{guion_original}")
        
        # 2. AUDITOR REVISA
        print("\n2. ⚖️ AUDITOR: Revisando Puntuación de Acero...")
        with open("prompts/auditoria.txt", "r", encoding="utf-8") as f:
            prompt_auditor = f.read()
            
        analisis_auditor = auditor_brain.generate(
            f"{prompt_auditor}\n\nGUION A AUDITAR:\n{guion_original}",
            temperature=0.2
        )
        
        guion_final = auditor_brain.generate(
            f"Basándote en la auditoría, entrega ÚNICAMENTE el texto final optimizado para locución. Sin etiquetas de fase ni encabezados. Puntuación percusiva.\n\nAuditoría:\n{analisis_auditor}\n\nGuion borrador:\n{guion_original}",
            temperature=0.1
        ).strip()
        print(f"\n[GUION FINAL PARA LOCUCIÓN]:\n{guion_final}")
        
        # 3. LOCUCIÓN
        print("\n3. 🎙️ VOICE DIRECTOR: Generando Voz...")
        output_audio = f"output/{video['id']}_voice.wav"
        success_voice = andres_voice.generar_voz(guion_final, output_audio)
        if success_voice:
            print(f"✅ Voz generada y auditada en: {output_audio}")
        else:
            print("❌ Error en la generación de voz.")
            
        # 4. VISUAL (Señal para Colab)
        print("\n4. 👁️ VISUAL DIRECTOR: Diseñando Estética y enviando señal a Colab...")
        estetica = visual_dir.diseñar_estetica(guion_final, tema_global=video['tema'])
        
        # Pedimos al cerebro que extraiga un prompt T2V de 1 frase en inglés para Wan2.1
        prompt_t2v = visual_dir.brain.generate(
            f"Basado en esta estética, genera UN SOLO PROMPT corto y descriptivo en INGLÉS (max 20 palabras) para un generador de Video IA (Wan2.1). Estética oscura, cinemática, industrial.\n\nEstética:\n{estetica}",
            temperature=0.4
        ).strip()
        
        # Limpiar posibles comillas
        prompt_t2v = prompt_t2v.replace('"', '').replace("'", "")
        print(f"🎨 Prompt de Video Extraído: {prompt_t2v}")
        
        job_path = visual_dir.forjar_video_colab(prompt_t2v, video['id'])
        print(f"✅ Señal de video enviada a Google Drive: {job_path}")
        
        print("\n⏱️ Esperando 5 segundos antes del siguiente video...")
        time.sleep(5)
        
    print("\n🚀 [Gran Visir] La Trilogía ha sido forjada. Revisa la carpeta de salida y espera a que Colab renderice los videos.")

if __name__ == "__main__":
    forja_apertura_canal()
