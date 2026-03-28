import sys, os
sys.path.append(r'd:\YT\MiuraForge')
from tools.image_forge import generar_imagen_nebius

os.makedirs(r'd:\YT\MiuraForge\output\merch', exist_ok=True)

prompt = 'Hyper-detailed dark heraldic emblem logo centered on pure pitch black background. A serene calm wolf head with closed mouth and composed dignified expression, soft gray fur like a snowy mountain arctic wolf, pale ice-gray tones, with massive wide curved bull horns in the style of Spanish Miura fighting bulls extending outward from the head. Two large crossed longswords forming a full X shape behind the wolf head, the blades spanning the entire width crossing over the face from corner to corner, dark Damascus steel blades with subtle gold filigree on the guards. Below the emblem the bold text MIURA STEEL in weathered industrial military stencil font, metallic silver letters with subtle ember orange glow. Dark dramatic coat of arms aesthetic, extremely detailed metalwork, forged steel textures, pure black background, perfectly symmetrical composition, 4k ultra detailed digital art.'

ok = generar_imagen_nebius(prompt, r'd:\YT\MiuraForge\output\merch\MIURA_STEEL_NEBIUS_v2.png', size="1024x1024")
print('Resultado:', 'EXITO' if ok else 'FALLO')

if ok:
    os.startfile(r'd:\YT\MiuraForge\output\merch\MIURA_STEEL_NEBIUS_v2.png')
