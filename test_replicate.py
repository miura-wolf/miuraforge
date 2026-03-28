import os
import time
import requests
from dotenv import load_dotenv

load_dotenv()

def probar_modelo_economico():
    print("="*60)
    print("🧪 PRUEBA DE ESTUDIO: MODELOS DE REPLICATE (API NATIVA)")
    print("="*60)
    print("Elige el motor de IA de video:")
    print("  [1] Minimax Video-01 (Ultra realista, $0.04/generación)")
    print("  [2] Lightricks LTX-Video (Extremadamente barato, ~$0.003/gen)")
    print("  [3] THUDM CogVideoX-5B (Open Source, T2V, muy barato)")
    
    opcion = input("\nSoberano, digita tu elección (1/2/3): ").strip()
    
    if opcion == "1":
        modelo = "minimax/video-01"
    elif opcion == "2":
        modelo = "lightricks/ltx-video"
    elif opcion == "3":
        modelo = "thudm/cogvideox-5b"
    else:
        print("❌ Opción inválida.")
        return

    prompt_dinamico = "A brilliant cinematic shot of a futuristic steel wolf with horns like Miura bulls charging through dense smoke, slow motion, professional 4K lighting."
    
    print(f"\n🎬 Modelo seleccionado: {modelo}")
    print(f"✍️ Prompt: {prompt_dinamico}")
    print("⏳ Enviando a procesar en la nube...")

    token = os.getenv("REPLICATE_API_TOKEN")
    if not token:
        print("❌ REPLICATE_API_TOKEN no encontrado en .env")
        return

    try:
        input_args = { "prompt": prompt_dinamico }
        if opcion == "3":
            input_args["num_inference_steps"] = 50
            input_args["guidance_scale"] = 6.0
        elif opcion == "1":
            input_args["prompt_optimizer"] = True

        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        API_URL = f"https://api.replicate.com/v1/models/{modelo}/predictions"
        res = requests.post(API_URL, headers=headers, json={"input": input_args})
        
        if res.status_code not in [200, 201]:
            print(f"❌ Error API: {res.text}")
            return
            
        pred = res.json()
        get_url = pred["urls"]["get"]
        
        print("⏳ Generando... (Consultando estado cada 5 segundos)")
        while True:
            estado = pred.get("status")
            if estado == "succeeded":
                break
            elif estado in ["failed", "canceled"]:
                print(f"\n❌ Generación fallida/cancelada: {pred.get('error')}")
                return
                
            time.sleep(5)
            pred = requests.get(get_url, headers=headers).json()
            print(f"   ...estado: {pred.get('status')}")
            
        output = pred.get("output")
        video_url = output if isinstance(output, str) else output[0] if isinstance(output, list) else list(output)[-1]
        
        print(f"\n✅ ¡Video Generado con Éxito!")
        print(f"🔗 URL Temporal: {video_url}")
        
        print("\n📥 Descargando a tu disco duro...")
        respuesta = requests.get(video_url)
        
        nombre_archivo = f"prueba_{modelo.split('/')[-1]}.mp4"
        with open(nombre_archivo, "wb") as f:
            f.write(respuesta.content)
            
        print(f"💾 Guardado localmente como: {nombre_archivo}")
        
    except Exception as e:
        print(f"\n❌ Se produjo un error local: {e}")

if __name__ == "__main__":
    probar_modelo_economico()
