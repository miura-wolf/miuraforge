import os
import re
import requests
import json
from google.genai import Client as GeminiClient
from dotenv import load_dotenv
from tenacity import retry, stop_after_attempt, wait_exponential

load_dotenv()

class GeminiProvider:
    def __init__(self):
        self.api_keys = self._load_api_keys()
        self.current_key_idx = 0
        if not self.api_keys:
            print("❌ [Gemini] No se encontraron API Keys en .env")
            self.client = None
            return
            
        self.api_key = self.api_keys[self.current_key_idx]
        self.client = GeminiClient(api_key=self.api_key)
        self.model = os.getenv("ACTIVE_MODEL")

    def _load_api_keys(self):
        """Carga todas las llaves posibles desde .env, incluso las comentadas."""
        keys = []
        # Probar rutas probables para el archivo .env
        potential_paths = [
            ".env",
            os.path.join(os.getcwd(), ".env"),
            os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env")
        ]
        
        for env_path in potential_paths:
            try:
                if os.path.exists(env_path):
                    with open(env_path, "r", encoding="utf-8") as f:
                        for line in f:
                            # Solo cargar si la línea NO empieza con #
                            if "GEMINI_API_KEY=" in line and not line.strip().startswith("#"):
                                # Extraer la llave
                                match = re.search(r'GEMINI_API_KEY=([a-zA-Z0-9_-]+)', line)
                                if match:
                                    keys.append(match.group(1))
                    if keys: break 
            except Exception as e:
                pass
        
        if not keys:
            print("⚠️ [Gemini] No se detectaron llaves en ninguna de las rutas del .env")
            
        # Eliminar duplicados manteniendo el orden
        return list(dict.fromkeys(keys))

    def _rotate_key(self):
        """Cambia a la siguiente API Key disponible."""
        if not self.api_keys: return
        self.current_key_idx = (self.current_key_idx + 1) % len(self.api_keys)
        self.api_key = self.api_keys[self.current_key_idx]
        self.client = GeminiClient(api_key=self.api_key)
        print(f"🔄 [Gemini] Rotando a API Key {self.current_key_idx + 1}/{len(self.api_keys)}")

    @retry(
        stop=stop_after_attempt(12), # Suficientes intentos para rotar por varias llaves
        wait=wait_exponential(multiplier=1, min=2, max=10),
        reraise=True
    )
    def generate(self, prompt, context_files=None, temperature=0.7, **kwargs):
        if not self.client:
            raise Exception("No valid Gemini API keys found.")
            
        try:
            processed_contents = []
            if context_files:
                for item in context_files:
                    # Si es una ruta (string), subimos el archivo con el cliente actual
                    if isinstance(item, str) and os.path.exists(item):
                        # print(f"📁 [Gemini] Subiendo contexto: {os.path.basename(item)}")
                        uploaded_file = self.client.files.upload(file=item)
                        processed_contents.append(uploaded_file)
                    else:
                        processed_contents.append(item)
            
            contents = processed_contents + [prompt]
            
            # Configuramos la generación (Gemini SDK)
            from google.genai.types import GenerateContentConfig
            config = GenerateContentConfig(
                temperature=temperature
            )
            
            response = self.client.models.generate_content(
                model=self.model,
                contents=contents,
                config=config
            )
            return response.text
        except Exception as e:
            err_msg = str(e).lower()
            if "429" in err_msg or "resource_exhausted" in err_msg or "quota" in err_msg:
                print(f"⚠️ [Gemini] Cuota agotada detectada. Rotando...")
                self._rotate_key()
            else:
                print(f"⚠️ [Gemini] Error detectado: {e}")
            raise e

class NvidiaProvider:
    def __init__(self, model_name):
        self.api_keys = self._load_api_keys()
        self.current_key_idx = 0
        if not self.api_keys:
            print("⚠️ [NVIDIA] No se detectaron llaves múltiples. Usando variable de entorno única.")
            self.api_key = os.getenv("OPENAI_API_KEY")
        else:
            self.api_key = self.api_keys[self.current_key_idx]

        self.invoke_url = "https://integrate.api.nvidia.com/v1/chat/completions"
        self.model = model_name

    def _load_api_keys(self):
        """Carga todas las llaves posibles desde .env."""
        keys = []
        potential_paths = [
            ".env",
            os.path.join(os.getcwd(), ".env"),
            os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env")
        ]
        
        for env_path in potential_paths:
            try:
                if os.path.exists(env_path):
                    with open(env_path, "r", encoding="utf-8") as f:
                        for line in f:
                            # Solo cargar si la línea NO empieza con # (evitar llaves comentadas)
                            if "OPENAI_API_KEY=" in line and not line.strip().startswith("#"):
                                # Extraer la llave (soportando nvapi- o similar)
                                match = re.search(r'OPENAI_API_KEY=([a-zA-Z0-9_-]+)', line)
                                if match:
                                    keys.append(match.group(1))
                    if keys: break 
            except: pass
        return list(dict.fromkeys(keys))

    def _rotate_key(self):
        """Cambia a la siguiente API Key disponible."""
        if not self.api_keys: return
        self.current_key_idx = (self.current_key_idx + 1) % len(self.api_keys)
        self.api_key = self.api_keys[self.current_key_idx]
        print(f"🔄 [NVIDIA] Rotando a API Key {self.current_key_idx + 1}/{len(self.api_keys)}")

    @retry(
        stop=stop_after_attempt(10), 
        wait=wait_exponential(multiplier=1, min=2, max=10),
        reraise=True
    )
    def generate(self, prompt, context_files=None, temperature=0.7, frequency_penalty=0.0, **kwargs):
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Accept": "application/json"
        }

        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 1048,
            "temperature": temperature,
            "frequency_penalty": frequency_penalty,
            "top_p": 1.0,
            "stream": False
        }
        
        payload.update(kwargs)

        try:
            print(f"📡 [NVIDIA] Invocando al modelo: {self.model}...")
            response = requests.post(self.invoke_url, headers=headers, json=payload)

            if response.status_code == 200:
                resultado = response.json()
                content = resultado.get('choices', [{}])[0].get('message', {}).get('content')
                return content if content is not None else ""
            
            # Si hay error 429, 401, 403 o 500, lanzamos excepción para rotar
            elif response.status_code in [401, 403, 429, 500]:
                print(f"⚠️ [NVIDIA] Error {response.status_code} detectado. Activando rotación...")
                response.raise_for_status()
            else:
                print(f"⚠️ [NVIDIA] Error {response.status_code}: {response.text}")
                response.raise_for_status()

        except Exception as e:
            err_msg = str(e).lower()
            if any(x in err_msg for x in ["401", "403", "429", "500", "rate_limit", "internal", "quota", "exhausted"]):
                self._rotate_key()
            raise e


from groq import Groq

class GroqProvider:
    def __init__(self, model_name="groq/compound"):
        self.api_keys = self._load_api_keys()
        self.current_key_idx = 0
        if not self.api_keys:
            print("❌ [Groq] No se encontraron API Keys en .env")
            self.client = None
            return
            
        self.api_key = self.api_keys[self.current_key_idx]
        self.client = Groq(api_key=self.api_key)
        self.model = model_name

    def _load_api_keys(self):
        keys = []
        potential_paths = [".env", os.path.join(os.getcwd(), ".env")]
        for env_path in potential_paths:
            try:
                if os.path.exists(env_path):
                    with open(env_path, "r", encoding="utf-8") as f:
                        for line in f:
                            # Solo si empieza con GROQ o si no tiene # antes
                            if "GROQ_API_KEY=" in line and not line.strip().startswith("#"):
                                match = re.search(r'GROQ_API_KEY=([a-zA-Z0-9_-]+)', line)
                                if match: keys.append(match.group(1))
                    if keys: break
            except: pass
        return list(dict.fromkeys(keys))

    def _rotate_key(self):
        if not self.api_keys: return
        self.current_key_idx = (self.current_key_idx + 1) % len(self.api_keys)
        self.api_key = self.api_keys[self.current_key_idx]
        self.client = Groq(api_key=self.api_key)
        print(f"🔄 [Groq] Rotando a API Key {self.current_key_idx + 1}/{len(self.api_keys)}")

    @retry(stop=stop_after_attempt(5), wait=wait_exponential(multiplier=1, min=2, max=10), reraise=True)
    def generate(self, prompt, context_files=None, temperature=0.7, **kwargs):
        if not self.client: raise Exception("No valid Groq API keys found.")
        
        try:
            # Configuración para modelos Compound (Búsqueda web integrada, intérprete y visita)
            compound_config = {
                "tools": {
                    "enabled_tools": ["web_search", "code_interpreter", "visit_website"]
                }
            }
            
            # Si se pasan dominios específicos para el Oráculo
            if "search_domains" in kwargs:
                compound_config["tools"]["web_search_settings"] = {
                    "include_domains": kwargs["search_domains"]
                }

            print(f"📡 [Groq] Invocando al modelo: {self.model} (Compound Mode)...")
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=temperature,
                max_completion_tokens=1024,
                top_p=1,
                stream=False,
                compound_custom=compound_config
            )
            return completion.choices[0].message.content or ""
            
        except Exception as e:
            err_msg = str(e).lower()
            if any(x in err_msg for x in ["429", "401", "quota", "exhausted", "limit", "rate_limit", "invalid_api_key"]):
                print(f"⚠️ [Groq] Error de acceso/cuota detectado. Rotando...")
                self._rotate_key()
            else:
                print(f"⚠️ [Groq] Error detectado: {e}")
            raise e

class ResilientProvider:
    """Implementa la Directiva de Resiliencia: Cadena de Tiers (Multi-respaldo)."""
    def __init__(self, tiers):
        self.tiers = tiers # Lista de proveedores en orden de prioridad

    def generate(self, prompt, context_files=None, **kwargs):
        last_error = None
        for i, provider in enumerate(self.tiers):
            try:
                if i > 0:
                    print(f"🚨 [SISTEMA] Activando RESPALDO Tier {i+1}...")
                return provider.generate(prompt, context_files=context_files, **kwargs)
            except Exception as e:
                err_msg = str(e).lower()
                # Si es un error de cuota, intentamos el siguiente Tier
                if any(x in err_msg for x in ["429", "quota", "exhausted", "limit", "resource_exhausted", "rate_limit"]):
                    last_error = e
                    continue
                else:
                    # Si es un error estructural o de otro tipo, lo lanzamos de una vez
                    raise e
        
        if last_error:
            print(f"❌ [SISTEMA] Todos los Tiers de respaldo han fallado.")
            raise last_error