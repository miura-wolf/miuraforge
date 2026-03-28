import sys, os, requests, base64
sys.path.append(r'd:\YT\MiuraForge')
from tools.image_forge import cargar_nvidia_keys

keys = cargar_nvidia_keys()
key = keys[0]

# Prompt suavizado para evitar el filtro de contenido de NVIDIA
prompt = 'Hyper-detailed dark heraldic crest emblem centered on pure black background. Majestic canine head with large curved horns similar to Spanish fighting bull, face in burnished silver steel texture with glowing amber eyes. Two ornate steel blades crossed behind the crest forming an X pattern, dark Damascus metal with gold filigree details. Below the crest the bold text MIURA STEEL in weathered industrial stencil typography, silver metallic letters. Dark dramatic coat of arms style, forged metalwork textures, symmetrical composition, 4k digital art.'

url = 'https://ai.api.nvidia.com/v1/genai/black-forest-labs/flux.2-klein-4b'
headers = {'Authorization': f'Bearer {key}', 'Accept': 'application/json'}
payload = {'prompt': prompt, 'width': 1024, 'height': 1024, 'seed': 7, 'steps': 4}

res = requests.post(url, headers=headers, json=payload)
print(f'Status: {res.status_code}')
data = res.json()

if 'artifacts' in data:
    a = data['artifacts'][0]
    b64val = a.get('base64', '')
    finish = a.get('finishReason', 'N/A')
    print(f'finishReason: {finish}')
    print(f'base64 len: {len(b64val)}')
    if b64val:
        os.makedirs(r'd:\YT\MiuraForge\output\merch', exist_ok=True)
        with open(r'd:\YT\MiuraForge\output\merch\MIURA_STEEL_LOGO_v1.png', 'wb') as f:
            f.write(base64.b64decode(b64val))
        print('SAVED!')
        os.startfile(r'd:\YT\MiuraForge\output\merch\MIURA_STEEL_LOGO_v1.png')
    else:
        print(f'FILTERED AGAIN: {finish}')
