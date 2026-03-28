"""
⚔️ TEST FLUX-DEV vs FLUX-SCHNELL — Comparativa de Calidad
Regenera clip_07 y clip_08 de MASIVA_SEMANA_202610_9_1420 con Nebius flux-dev.
Guarda como clip_07_FLUXDEV.png y clip_08_FLUXDEV.png para comparar lado a lado.
"""
import os
import sys
import requests
import base64
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env"))

# ══════════════════════════════════════════════════════════
#  Prompts originales de MASIVA_SEMANA_202610_9_1420
# ══════════════════════════════════════════════════════════
CLIPS = {
    "clip_07": {
        "prompt": (
            "A hand cutting a thick, rusted cable with industrial bolt cutters, "
            "sparks flying in a brief, sharp burst of Miura gold (#C8A96E) against "
            "a backdrop of steel panels (#2A2A2A), vertical 9:16."
        ),
        "guion": "Corta el circuito de comparación. Ahora. Mide solo el peso que tu estructura puede sostener. El real. El que construyes."
    },
    "clip_08": {
        "prompt": (
            "A clean, simple steel notebook (#2A2A2A) lying open on a bare workbench, "
            "a single line of text etched onto its page catching a razor-thin line of "
            "Miura gold (#C8A96E) light, surrounded by deep shadow (#0A0A0A), vertical 9:16."
        ),
        "guion": "Ejecuta el corte: Bloquea una fuente que alimente el estándar ajeno. Define tres movimientos que solo exijan tu ejecución. Ni aprobación. Ni testigos. Solo el registro del metal que hoy se templa."
    }
}

# ══════════════════════════════════════════════════════════
#  Config
# ══════════════════════════════════════════════════════════
OUT_DIR = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    "output", "imagenes_shorts", "MASIVA_SEMANA_202610_9_1420"
)

NEBIUS_KEY = os.getenv("NEBIUS_API_KEY")
if not NEBIUS_KEY:
    print("❌ NEBIUS_API_KEY no encontrada en .env")
    sys.exit(1)

client = OpenAI(
    base_url="https://api.tokenfactory.nebius.com/v1/",
    api_key=NEBIUS_KEY
)


def generar_flux_dev(nombre_clip, prompt):
    """Genera imagen con flux-dev y guarda como clip_XX_FLUXDEV.png"""
    nombre_archivo = f"{nombre_clip}_FLUXDEV.png"
    out_path = os.path.join(OUT_DIR, nombre_archivo)

    print(f"\n🔨 Generando {nombre_archivo} con flux-dev...")
    print(f"   Prompt: {prompt[:80]}...")

    try:
        response = client.images.generate(
            model="black-forest-labs/flux-dev",
            prompt=prompt,
            # flux-dev soporta más parámetros de calidad
            extra_body={
                "width": 752,
                "height": 1392,
                "num_inference_steps": 28,   # flux-dev: más pasos = más calidad
            }
        )

        print(f"   Respuesta raw: {response.to_json()[:200]}...")

        # Procesar respuesta (URL o b64)
        if response.data and len(response.data) > 0:
            img_data = response.data[0]

            os.makedirs(OUT_DIR, exist_ok=True)

            if hasattr(img_data, 'b64_json') and img_data.b64_json:
                with open(out_path, "wb") as f:
                    f.write(base64.b64decode(img_data.b64_json))
                print(f"   ✅ Guardado (b64): {out_path}")
                return True

            elif hasattr(img_data, 'url') and img_data.url:
                img_response = requests.get(img_data.url, timeout=60)
                if img_response.status_code == 200:
                    with open(out_path, "wb") as f:
                        f.write(img_response.content)
                    print(f"   ✅ Guardado (URL): {out_path}")
                    return True
                else:
                    print(f"   ❌ Error descargando desde URL: {img_response.status_code}")

        print("   ⚠️ Respuesta sin imagen válida")
        return False

    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False


def main():
    print("=" * 60)
    print("  COMPARATIVA: flux-dev vs flux-schnell")
    print("  Sesión: MASIVA_SEMANA_202610_9_1420")
    print("=" * 60)
    print(f"\n📁 Directorio de salida: {OUT_DIR}")
    print("\nLos originales (flux-schnell) ya están como clip_07.png y clip_08.png")
    print("Los nuevos (flux-dev) se guardarán como clip_07_FLUXDEV.png y clip_08_FLUXDEV.png\n")

    resultados = {}
    for nombre_clip, data in CLIPS.items():
        ok = generar_flux_dev(nombre_clip, data["prompt"])
        resultados[nombre_clip] = "✅ OK" if ok else "❌ FALLÓ"

    print("\n" + "=" * 60)
    print("  RESULTADO FINAL:")
    for clip, estado in resultados.items():
        print(f"  {clip} flux-dev: {estado}")
    print("=" * 60)
    print("\n💡 Para comparar abre ambas versiones:")
    print(f"   Original   → {OUT_DIR}\\clip_07.png")
    print(f"   Flux-Dev   → {OUT_DIR}\\clip_07_FLUXDEV.png")
    print(f"   Original   → {OUT_DIR}\\clip_08.png")
    print(f"   Flux-Dev   → {OUT_DIR}\\clip_08_FLUXDEV.png")


if __name__ == "__main__":
    main()
