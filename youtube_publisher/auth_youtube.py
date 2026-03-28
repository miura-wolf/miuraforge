"""
auth_youtube.py — MiuraForgeEngine
=====================================
Ejecución ÚNICA. Captura la sesión de YouTube Studio y la guarda
en youtube_state.json para que youtube_publisher.py corra solo.

FIX v4 — Solución definitiva al error DevTools/perfil bloqueado:
Chrome no permite que Playwright use el perfil "Default" en vivo con
remote debugging. Solución: abrir Chrome sin perfil, hacer login manual
UNA vez, guardar el state. El publisher ya no necesita login nunca más.

Uso:
  python auth_youtube.py
  python auth_youtube.py --output mi_sesion_yt.json

El estado se guarda en ~/.miura_forge/ por defecto (directorio seguro).
"""

import argparse
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright

# Importar configuración centralizada
try:
    sys.path.append(str(Path(__file__).resolve().parent.parent))
    from core.config import YOUTUBE_STATE_PATH, ensure_secrets_dir

    USING_CONFIG_MODULE = True
    DEFAULT_STATE = str(YOUTUBE_STATE_PATH)
except ImportError:
    USING_CONFIG_MODULE = False
    DEFAULT_STATE = "youtube_state.json"

    def ensure_secrets_dir():
        return Path.cwd()


def capturar_sesion(output_path: str = None):
    # Si no se especifica ruta, usar la configuración centralizada
    if output_path is None:
        if USING_CONFIG_MODULE:
            ensure_secrets_dir()
            output_path = str(YOUTUBE_STATE_PATH)
        else:
            output_path = DEFAULT_STATE

    output_path_obj = Path(output_path)
    print("=" * 60)
    print("🎬 MIURA AUTH YOUTUBE — Captura de sesión YouTube Studio")
    print("=" * 60)
    print()

    # Verificar playwright-stealth
    try:
        from playwright_stealth import stealth

        stealth_disponible = True
        print("✅ playwright-stealth activo")
    except ImportError:
        stealth_disponible = False
        print("⚠️  playwright-stealth no instalado (pip install playwright-stealth)")
    print()

    print("Se abrirá una ventana de Chrome.")
    print("1. Inicia sesión en Google con tu cuenta de YouTube")
    print("2. Cuando veas el dashboard de Studio, vuelve aquí y presiona ENTER")
    print()

    with sync_playwright() as p:
        # Usar Chrome real del sistema (channel="chrome")
        # Sin --user-data-dir personalizado → evita el error DevTools
        try:
            browser = p.chromium.launch(
                channel="chrome",
                headless=False,
                args=[
                    "--no-sandbox",
                    "--disable-blink-features=AutomationControlled",
                    "--start-maximized",
                ],
            )
            print("✅ Chrome real abierto")
        except Exception as e:
            print(f"⚠️  Chrome no disponible ({e}). Usando Chromium de Playwright...")
            browser = p.chromium.launch(
                headless=False,
                args=[
                    "--no-sandbox",
                    "--disable-blink-features=AutomationControlled",
                    "--start-maximized",
                ],
            )

        context = browser.new_context(
            viewport={"width": 1280, "height": 900},
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0.0.0 Safari/537.36"
            ),
        )
        page = context.new_page()

        # Stealth antes de navegar
        # Stealth desactivado a petición del Soberano
        # if stealth_disponible:
        #     from playwright_stealth import stealth
        #     stealth(page)
        #     print("🛡️  Stealth activo")

        # Ir directo a YouTube Studio
        print("\n🌐 Abriendo studio.youtube.com...")
        page.goto("https://studio.youtube.com", timeout=30_000)

        print()
        print("─" * 60)
        print("👉 ACCIÓN REQUERIDA en la ventana de Chrome:")
        print("   1. Inicia sesión con tu cuenta de Google/YouTube")
        print("   2. Espera a ver el dashboard de YouTube Studio")
        print("─" * 60)
        input("\n✅ Presiona ENTER cuando el dashboard esté visible...")

        # Verificar URL
        url_actual = page.url
        if "studio.youtube.com" not in url_actual:
            print(f"\n⚠️  URL actual: {url_actual}")
            continuar = (
                input("   No parece Studio. ¿Guardar de todas formas? (s/n): ").strip().lower()
            )
            if continuar != "s":
                print("Cancelado.")
                browser.close()
                return

    # Guardar estado de sesión completo (cookies + localStorage)
    context.storage_state(path=str(output_path_obj))
    print(f"\n💾 Sesión guardada en: {output_path_obj}")
    if USING_CONFIG_MODULE:
        print("✅ Directorio seguro: ~/.miura_forge/")
    print("🔒 NO lo subas a git (.gitignore ya lo cubre).")
    print()
    print("✅ Listo. youtube_publisher.py ya puede correr sin login.")
    browser.close()



if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output", default=None, help=f"Archivo de salida (default: {DEFAULT_STATE})"
    )
    args = parser.parse_args()
    capturar_sesion(args.output)
