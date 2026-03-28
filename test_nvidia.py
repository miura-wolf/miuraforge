import os
import requests
from dotenv import load_dotenv

load_dotenv()

def test_nvidia_key(key, model):
    url = "https://integrate.api.nvidia.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": "Hola, responde con una palabra."}],
        "max_tokens": 10
    }
    try:
        response = requests.post(url, headers=headers, json=payload)
        if response.status_code == 200:
            return f"✅ {model}: OK"
        else:
            return f"❌ {model}: Error {response.status_code} - {response.text[:100]}"
    except Exception as e:
        return f"❌ {model}: Exception - {str(e)}"

# Extraer todas las llaves de NVIDIA del .env manually if needed, 
# but for now let's use the active one
active_key = os.getenv("OPENAI_API_KEY")
active_model = os.getenv("OPENAI_MODEL", "deepseek-ai/deepseek-v3")

print(f"Probando Llave Activa: {active_key[:10]}...")
print(test_nvidia_key(active_key, active_model))
print(test_nvidia_key(active_key, "deepseek-ai/deepseek-v3")) # Fallback model
