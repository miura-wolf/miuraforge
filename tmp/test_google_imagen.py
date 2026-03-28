"""
⚔️ TEST Gemini 2.5 Flash Image — Modelos nuevos disponibles
Prueba los 3 modelos detectados con el prompt real de Miura.
"""
import os
import sys
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env"))

GEMINI_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_KEY:
    print("❌ GEMINI_API_KEY no encontrada")
    sys.exit(1)

# Prompt real de clip_07 de MASIVA_SEMANA_202610_9_1420
PROMPT = (
    "A hand cutting a thick, rusted cable with industrial bolt cutters, "
    "sparks flying in a brief, sharp burst of Miura gold (#C8A96E) against "
    "a backdrop of steel panels (#2A2A2A), vertical 9:16, extreme chiaroscuro, "
    "hyperrealistic photography, industrial forge atmosphere, absolute black background."
)

OUT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "tmp")
os.makedirs(OUT_DIR, exist_ok=True)

MODELOS = [
    "gemini-2.5-flash-image",
    "gemini-3-pro-image-preview",
    "gemini-3.1-flash-image-preview",
]


def test_modelo_genai(model_name):
    """Prueba generación via generate_content con response_modalities IMAGE."""
    print(f"\n{'='*55}")
    print(f"  Probando: {model_name}")
    print(f"{'='*55}")
    try:
        from google import genai as gai
        from google.genai import types as gtypes

        client = gai.Client(api_key=GEMINI_KEY)

        response = client.models.generate_content(
            model=model_name,
            contents=PROMPT,
            config=gtypes.GenerateContentConfig(
                response_modalities=["IMAGE", "TEXT"],
            )
        )

        # Buscar parte con imagen en la respuesta
        for part in response.candidates[0].content.parts:
            if hasattr(part, 'inline_data') and part.inline_data is not None:
                nombre = model_name.replace("/", "_").replace("-", "_")
                out = os.path.join(OUT_DIR, f"test_{nombre}.png")
                with open(out, "wb") as f:
                    f.write(part.inline_data.data)
                print(f"✅ ¡IMAGEN GENERADA! → {out}")
                return True, out

        print("⚠️ Respuesta sin imagen (solo texto)")
        return False, None

    except Exception as e:
        print(f"❌ Error: {e}")
        return False, None


if __name__ == "__main__":
    print("⚔️ TEST GEMINI IMAGE — Modelos detectados")
    print(f"API Key: ...{GEMINI_KEY[-6:]}")
    print(f"Prompt: {PROMPT[:70]}...")

    exitosos = []

    for modelo in MODELOS:
        ok, ruta = test_modelo_genai(modelo)
        if ok:
            exitosos.append((modelo, ruta))

    print(f"\n{'='*55}")
    print("RESUMEN:")
    if exitosos:
        for modelo, ruta in exitosos:
            print(f"  ✅ {modelo}")
            print(f"     → {ruta}")
        print(f"\n🏆 Mejor modelo disponible: {exitosos[0][0]}")
        # Abrir la primera imagen generada
        try:
            import subprocess
            subprocess.Popen(["explorer", exitosos[0][1]])
        except:
            pass
    else:
        print("  ❌ Ningún modelo generó imagen.")
        print("  Tip: La generación de imágenes con Gemini puede requerir")
        print("       región específica o permisos adicionales.")
    print(f"{'='*55}")
