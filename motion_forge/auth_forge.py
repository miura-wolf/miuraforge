"""
auth_forge.py — MiuraForgeEngine
==================================
Ejecución ÚNICA. Abre el navegador para que hagas login manual
en Meta AI y guarda el estado de sesión en state.json.

Después de esto, motion_forge_playwright.py corre solo sin que
vuelvas a hacer login.

Uso:
  python auth_forge.py
  python auth_forge.py --output mi_sesion.json

El estado se guarda en ~/.miura_forge/ por defecto (directorio seguro).
"""

import argparse
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright

# Importar configuración centralizada
try:
    sys.path.append(str(Path(__file__).resolve().parent.parent))
    from core.config import META_STATE_PATH, ensure_secrets_dir, get_meta_state_path

    USING_CONFIG_MODULE = True
    DEFAULT_STATE = str(META_STATE_PATH)
except ImportError:
    USING_CONFIG_MODULE = False
    DEFAULT_STATE = "meta_state.json"

    def ensure_secrets_dir():
        return Path.cwd()

    def get_meta_state_path(index=None):
        if index is None:
            return Path("meta_state.json")
        return Path(f"meta_state_{index}.json")


def capturar_sesion(output_path=None):
    # Si no se especifica ruta, usar la configuración centralizada
    if output_path is None:
        if USING_CONFIG_MODULE:
            ensure_secrets_dir()
            output_path = str(META_STATE_PATH)
        else:
            output_path = DEFAULT_STATE

    output_path_obj = Path(output_path)

    # Asegurar que existe el directorio padre
    output_path_obj.parent.mkdir(parents=True, exist_ok=True)

    print("=" * 60)
    print("🔩 MIURA AUTH FORGE — Captura de sesión Meta AI")
    print("=" * 60)
    print()
    print(f"💾 La sesión se guardará en: {output_path}")
    print()
    print("Se abrirá el navegador. Haz login en Meta AI manualmente.")
    print("Cuando estés dentro (veas la interfaz principal), vuelve")
    print("aquí y presiona ENTER.")
    print()

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(
            viewport={"width": 1280, "height": 800},
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            ),
        )
        page = context.new_page()
        page.goto("https://www.meta.ai")

        input("✅ Presiona ENTER cuando hayas iniciado sesión...")

        context.storage_state(path=str(output_path_obj))
        print(f"\n💾 Sesión guardada en: {output_path_obj}")
        if USING_CONFIG_MODULE:
            print("✅ Directorio seguro: ~/.miura_forge/")
        print("🔒 NO lo subas a git (.gitignore ya lo cubre).")
        browser.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Captura sesión de Meta AI para automatización.")
    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help=f"Ruta donde guardar el estado (default: {DEFAULT_STATE})",
    )
    args = parser.parse_args()
    capturar_sesion(args.output)
