import os
import requests
import re
from pathlib import Path

def get_keys_and_models():
    env_path = Path(".env")
    if not env_path.exists():
        return [], []
    
    with open(env_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Encontrar keys (activas y comentadas)
    keys = re.findall(r"(?:#)?OPENAI_API_KEY=(nvapi-[^\s#]+)", content)
    # Encontrar modelos (activos y comentados)
    models = re.findall(r"(?:#)?OPENAI_MODEL=([^\s#]+)", content)
    
    return list(set(keys)), list(set(models))

def list_remote_models(key):
    url = "https://integrate.api.nvidia.com/v1/models"
    headers = {"Authorization": f"Bearer {key}"}
    try:
        resp = requests.get(url, headers=headers)
        if resp.status_code == 200:
            return resp.json().get("data", [])
        return []
    except:
        return []

def test_model(key, model):
    url = "https://integrate.api.nvidia.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": "Hi"}],
        "max_tokens": 5
    }
    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=10)
        return resp.status_code, resp.text[:100]
    except Exception as e:
        return 500, str(e)

keys, env_models = get_keys_and_models()

print(f"--- REPORTE DE DIAGNÓSTICO NVIDIA ---")
print(f"Llaves encontradas: {len(keys)}")
print(f"Modelos en .env: {len(env_models)}")

for k in keys:
    print(f"\n🔑 Probando llave: {k[:15]}...")
    remote_models = list_remote_models(k)
    if remote_models:
        print(f"✅ Llave VALIDA. Catálogo remoto: {len(remote_models)} modelos found.")
        # Solo listar los primeros 5 para no saturar
        print(f"Ejemplos del catálogo: {[m['id'] for m in remote_models[:5]]}")
    else:
        print(f"❌ Llave INVALIDA o catálogo no accesible (401/403).")
        continue

    print(f"\n🔍 Probando modelos específicos del .env con esta llave:")
    for m in env_models:
        status, text = test_model(k, m)
        if status == 200:
            print(f"  ✅ {m}: OK")
        else:
            print(f"  ❌ {m}: Error {status}")

print(f"\n--- FIN DEL DIAGNÓSTICO ---")
