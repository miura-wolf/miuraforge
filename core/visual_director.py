import os
import pandas as pd
import hashlib
import json
import time
import requests
from llm.factory import LLMFactory

class KeyRotator:
    def __init__(self, keys_list):
        self.keys = [k.strip() for k in keys_list if k and k.strip()]
        self.current = 0

    def get_key(self):
        if not self.keys:
            return None
        return self.keys[self.current]

    def rotate(self):
        if len(self.keys) > 1:
            self.current = (self.current + 1) % len(self.keys)
            print(f"🔄 [KeyRotator] Rotando a la llave índice {self.current}")
            return True
        return False

class VisualDirector:
    def __init__(self, db_manager=None, cache_file="output/visual_cache.json"):
        # Le pedimos a la Factory el cerebro con capacidad de recuperación
        self.brain = LLMFactory.get_brain("visual")
        self.db = db_manager
        self.cache_file = cache_file
        self.cache = self._load_cache()
        
        # Configuración de Sincronización (Colab/Drive)
        self.sync_path = os.getenv("DRIVE_SYNC_PATH", "MiuraForge_Sync")
        os.makedirs(self.sync_path, exist_ok=True)
        


        # Configuración de Grok (xAI)
        self.xai_api_key = os.getenv("XAI_API_KEY")
        self.grok_model = "grok-imagine-video" # O grok-4-1-fast para prompts

    def _load_cache(self):
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except:
                return {}
        return {}

    def _save_cache(self):
        os.makedirs(os.path.dirname(self.cache_file), exist_ok=True)
        # Reload para fusionar con lo que otros procesos hayan escrito
        current_cache = self._load_cache()
        current_cache.update(self.cache)
        with open(self.cache_file, "w", encoding="utf-8") as f:
            json.dump(current_cache, f, indent=2, ensure_ascii=False)
        self.cache = current_cache

    def leer_doctrina(self):
        ruta = os.path.join("prompts", "visual.txt")
        with open(ruta, "r", encoding="utf-8") as f:
            return f.read()

    def _extraer_inteligencia_real(self, tema_buscado):
        """Busca en el Puente de Mando (Sheets) el dolor validado."""
        if not self.db:
            return None
        try:
            investigaciones = self.db.obtener_investigacion_reciente(tema_buscado, limite=1)
            if investigaciones:
                return investigaciones[0]
            
            # Si no hay investigación directa, buscar en clusters
            if self.db.clusters:
                clusters = self.db.clusters.get_all_records()
                for c in clusters:
                    if tema_buscado.lower() in str(c.get('nombre_cluster', '')).lower():
                        return {
                            "DOLOR_PRINCIPAL": c.get('nombre_cluster'),
                            "FRASES_POTENTES": c.get('frase_dominante'),
                            "PROBLEMA_RAIZ": c.get('temas_relacionados')
                        }
            return None
        except Exception as e:
            print(f"⚠️ [Director Visual] Error extrayendo inteligencia: {e}")
            return None

    def estimar_duracion_segundos(self, texto):
        """Calcula la duración aproximada en base a 155 palabras por minuto."""
        palabras = len(texto.strip().split())
        minutos = palabras / 155
        return round(float(minutos * 60), 2)

    def diseñar_estetica(self, guion_texto, tema_global=None):
        """Forja la narrativa visual basada en el guion y el ADN Miura."""
        instruccion_base = self.leer_doctrina()
        
        # Creamos un hash del guion, tema y doctrina para la caché resiliente
        unique_key = hashlib.md5(f"{guion_texto}{tema_global}{instruccion_base}".encode()).hexdigest()
        
        if unique_key in self.cache:
            print("💾 [Director Visual] Reutilizando estética idéntica desde la caché (Ahorro de Créditos).")
            return self.cache[unique_key]

        duracion = self.estimar_duracion_segundos(guion_texto)
        # Cadencia Miura: 6 segundos por clip para alta retención (Ideal Grok Shorts)
        num_clips = max(1, round(duracion / 6))
        
        print(f"🎨 [Director Visual] Diseñando narrativa visual ({duracion}s, {num_clips} clips)...")
        
        info_real = None
        if tema_global:
            info_real = self._extraer_inteligencia_real(tema_global)
            
        contexto_inteligencia = ""
        if info_real:
            dolor = info_real.get('DOLOR_PRINCIPAL', info_real.get('dolor_principal', 'N/A'))
            frase = info_real.get('FRASES_POTENTES', info_real.get('frase_representativa', 'N/A'))
            contexto_inteligencia = f"""
            --- INTELIGENCIA DEL SUJETO (PARA SIMBOLISMO) ---
            DOLOR_DETECTADO: {dolor}
            FRASE_CLAVE: "{frase}"
            """
            print(f"🎯 [Director Visual] Usando simbolismo Miura para: {dolor}")

        categoria = info_real.get('DOLOR_PRINCIPAL', info_real.get('dolor_principal', 'General')) if info_real else 'General'
        arquetipo = info_real.get('ARQUETIPO_SUGERIDO', info_real.get('arquetipo_sugerido', '')) if info_real else ''
        
        prompt = f"""
        {instruccion_base}
        
        --- VARIABLES DE PRODUCCIÓN ---
        CATEGORIA_DOLOR: {categoria}
        NUM_CLIPS: {num_clips}
        ARQUETIPO_ANCLA: {arquetipo}
        
        {contexto_inteligencia}
        
        --- GUION MASTER ---
        {guion_texto}
        """
        
        # El cerebro (NVIDIA/DeepSeek) genera los prompts de imagen/video
        resultado = self.brain.generate(prompt)
        
        # Guardamos en caché
        self.cache[unique_key] = resultado
        self._save_cache()
        
        return resultado

    def forjar_video_colab(self, prompt, job_id):
        """Envía una señal a Google Colab via Drive Sync."""
        job_data = {
            "id": job_id,
            "prompt": prompt,
            "status": "pending",
            "timestamp": time.time()
        }
        path = os.path.join(self.sync_path, f"job_{job_id}.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(job_data, f)
        print(f"📡 [Director Visual] Señal enviada a Colab: {path}")
        return path

    def check_video_status(self, job_path):
        """Verifica si Colab ha terminado el video."""
        if not os.path.exists(job_path):
            return None
        try:
            with open(job_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            if data.get("status") == "completed":
                return data.get("video_path")
        except:
            pass
        return None



    def generar_video_grok(self, prompt, duration=6):
        """Genera video usando la API de xAI (Grok-Imagine-Video). Costo estimado: $0.25/seg."""
        if not self.xai_api_key:
            print("❌ [Director Visual] Error: XAI_API_KEY no configurada.")
            return None

        url = "https://api.x.ai/v1/videos/generations"
        headers = {
            "Authorization": f"Bearer {self.xai_api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": self.grok_model,
            "prompt": prompt,
            "duration": duration,
            "aspect_ratio": "9:16"
        }

        try:
            response = requests.post(url, json=payload, headers=headers)
            if response.status_code in [200, 201]:
                task_id = response.json().get("id")
                print(f"🎬 [Director Visual] Tarea de video iniciada en Grok: {task_id}")
                return task_id
            else:
                print(f"❌ [Director Visual] Error Grok ({response.status_code}): {response.text}")
                return None
        except Exception as e:
            print(f"❌ [Director Visual] Error enviando a Grok: {e}")
            return None

    def generar_imagen_puter(self, prompt):
        """Genera una imagen usando Puter.js (vía puente Node/Terminal)."""
        # Puter permite Grok Image gratis a través de su plataforma.
        # Esto requiere llamar a un script de Node que use la SDK de Puter.
        puter_script = os.path.join("scripts", "puter_generate.js")
        if not os.path.exists(puter_script):
            self._crear_script_puter(puter_script)
        
        import subprocess
        try:
            cmd = ["node", puter_script, prompt]
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                img_url = result.stdout.strip()
                print(f"🖼️ [Director Visual] Imagen generada vía Puter: {img_url}")
                return img_url
            else:
                print(f"❌ [Director Visual] Error en Puter: {result.stderr}")
                return None
        except Exception as e:
            print(f"❌ [Director Visual] Fallo ejecutando Puter.js: {e}")
            return None

    def _crear_script_puter(self, path):
        """Crea el script de Node.js necesario para interactuar con Puter."""
        js_code = """
const puter = require('@puter/sdk');
const prompt = process.argv[2];

async function generate() {
    try {
        const image = await puter.ai.txt2img(prompt);
        // Puter devuelve un objeto Blob/Buffer o URL según la versión
        // Para este caso, suponemos que queremos la URL o guardarlo.
        console.log(image.src); 
    } catch (e) {
        console.error(e);
        process.exit(1);
    }
}
generate();
"""
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(js_code)
