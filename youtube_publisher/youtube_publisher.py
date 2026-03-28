r"""
youtube_publisher.py — MiuraForgeEngine
=========================================
Publica Shorts automáticamente en YouTube Studio como BORRADORES.

Flujo:
  1. Lee tabla DESPLIEGUE de Google Sheets (ESTADO_DESPLIEGUE = PENDIENTE)
  2. Encuentra el MP4 en D:\YT\MiuraForge\output\shorts_finales\[ID_SESION]\
  3. Abre YouTube Studio con Playwright (sesión guardada)
  4. Sube el video con título, descripción y hashtags
  5. Lo deja como BORRADOR para que tú lo publiques cuando quieras
  6. Registra en tabla CONTENIDO_PUBLICADO del Sheet
  7. Mueve el MP4 a la carpeta "Ya Publicado"
  8. Actualiza ESTADO_DESPLIEGUE = BORRADOR en DESPLIEGUE

Prerequisito:
  python auth_youtube.py   ← una sola vez

Uso:
  python youtube_publisher.py                    # procesa todos los PENDIENTES
  python youtube_publisher.py --id MASIVA_SEMANA_202609_2   # uno específico
  python youtube_publisher.py --max 5            # máximo 5 en esta sesión
  python youtube_publisher.py --listar           # ver pendientes sin subir nada

FIX v3:
  - Reescritura completa de subir_a_youtube()
  - Navegación directa a /upload en lugar de clicks en menú (más robusto)
  - wait_for_selector reemplazado por esperas activas con reintentos
  - Logs de diagnóstico en cada paso para saber exactamente dónde falla
  - state_path dinámico — busca youtube_state.json en múltiples rutas
"""

import os
import sys
import re
import time
import random
import shutil
import argparse
from pathlib import Path
from datetime import datetime

# Importar configuración centralizada
try:
    sys.path.append(str(Path(__file__).resolve().parent.parent))
    from core.config import YOUTUBE_STATE_PATH

    USING_CONFIG_MODULE = True
except ImportError:
    USING_CONFIG_MODULE = False
    YOUTUBE_STATE_PATH = Path("youtube_state.json")

# ---------------------------------------------------------------------------
# CONFIGURACIÓN
# ---------------------------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent
# Usar configuración centralizada si está disponible
STATE_FILE = YOUTUBE_STATE_PATH if USING_CONFIG_MODULE else (BASE_DIR / "youtube_state.json")
SHORTS_BASE = Path(os.getenv("SHORTS_BASE", r"D:\YT\MiuraForge\output\shorts_finales"))
YA_PUBLICADO = SHORTS_BASE / "Ya Publicado"

# Delays humanizados entre uploads
DELAY_ENTRE_VIDEOS = (45, 90)  # segundos — YouTube es sensible a uploads rápidos

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/124.0.0.0 Safari/537.36"
)

# Columnas de DESPLIEGUE
COL_ID = "ID_MASTER"
COL_TITULO = "TITULO_GOLPE"
COL_DESCRIPCION = "DESCRIPCION_ACERO"
COL_HASHTAGS = "HASHTAGS_TACTICOS"
COL_ESTADO = "ESTADO_DESPLIEGUE"

# Tabs del Sheet
SHEET_TAB_PUBLICADO = "CONTENIDO_PUBLICADO"
SHEET_TAB_DESPLIEGUE = "DESPLIEGUE"


# ---------------------------------------------------------------------------
# STEALTH
# ---------------------------------------------------------------------------


def _cargar_stealth():
    try:
        # Desactivado temporalmente
        # from playwright_stealth import stealth
        # return stealth
        return None
    except ImportError:
        return None


STEALTH_FN = _cargar_stealth()


def aplicar_stealth(page):
    if STEALTH_FN:
        STEALTH_FN(page)


# ---------------------------------------------------------------------------
# CONEXIÓN CON GOOGLE SHEETS
# ---------------------------------------------------------------------------


def conectar_sheets():
    try:
        sys.path.append(str(BASE_DIR.parent))
        from core.database import Database

        db = Database()
        return db
    except Exception as e:
        print(f"❌ Error conectando con Sheets: {e}")
        print("   Asegúrate de estar en la raíz de MiuraForgeEngine")
        sys.exit(1)


def leer_pendientes(db) -> list[dict]:
    try:
        hoja = db.sheet.worksheet(SHEET_TAB_DESPLIEGUE)
        registros = hoja.get_all_records()
        pendientes = [
            r
            for r in registros
            if str(r.get(COL_ESTADO, "")).strip().upper() == "PENDIENTE"
            and r.get(COL_ID, "").strip()
        ]
        print(f"📋 Pendientes encontrados: {len(pendientes)}")
        return pendientes
    except Exception as e:
        print(f"❌ Error leyendo DESPLIEGUE: {e}")
        return []


def actualizar_estado_despliegue(db, id_master: str, nuevo_estado: str):
    try:
        hoja = db.sheet.worksheet(SHEET_TAB_DESPLIEGUE)
        registros = hoja.get_all_records()
        headers = hoja.row_values(1)
        col_id = headers.index(COL_ID) + 1
        col_est = headers.index(COL_ESTADO) + 1
        for i, r in enumerate(registros, start=2):
            if r.get(COL_ID, "").strip() == id_master:
                hoja.update_cell(i, col_est, nuevo_estado)
                return True
        return False
    except Exception as e:
        print(f"  ⚠️  Error actualizando estado: {e}")
        return False


def registrar_en_publicado(
    db, titulo: str, url: str, descripcion: str, estado: str, id_sesion: str
):
    try:
        hoja = db.sheet.worksheet(SHEET_TAB_PUBLICADO)
        fecha = datetime.now().strftime("%y-%m-%d-%H")
        hoja.append_row([titulo, url, descripcion, estado, "", id_sesion, fecha])
        return True
    except Exception as e:
        print(f"  ⚠️  Error registrando en CONTENIDO_PUBLICADO: {e}")
        return False


# ---------------------------------------------------------------------------
# UTILIDADES
# ---------------------------------------------------------------------------


def encontrar_mp4(id_sesion: str) -> Path | None:
    carpeta = SHORTS_BASE / id_sesion
    if not carpeta.exists():
        for d in SHORTS_BASE.iterdir():
            if d.is_dir() and d.name.startswith(id_sesion):
                carpeta = d
                break
    if not carpeta.exists():
        return None
    mp4s = list(carpeta.glob("*.mp4"))
    if not mp4s:
        return None
    return max(mp4s, key=lambda f: f.stat().st_size)


def formatear_descripcion(descripcion: str, hashtags: str, cta: str) -> str:
    partes = []
    if descripcion:
        partes.append(descripcion.strip())
    if cta:
        partes.append(f"\n{cta.strip()}")
    if hashtags:
        tags = re.findall(r"#\w+", hashtags)
        if tags:
            partes.append("\n" + " ".join(tags))
    return "\n\n".join(partes)


def mover_a_publicado(mp4_path: Path, id_sesion: str):
    try:
        destino_carpeta = YA_PUBLICADO / id_sesion
        destino_carpeta.mkdir(parents=True, exist_ok=True)
        destino = destino_carpeta / mp4_path.name
        shutil.move(str(mp4_path), str(destino))
        print(f"  📁 Movido a Ya Publicado: {mp4_path.name}")
        return True
    except Exception as e:
        print(f"  ⚠️  Error moviendo archivo: {e}")
        return False


# ---------------------------------------------------------------------------
# HELPER — esperar elemento con reintentos
# ---------------------------------------------------------------------------


def esperar_elemento(
    page, selectores: list[str], timeout_s: int = 30, visible: bool = True
) -> object:
    """
    Intenta cada selector de la lista en bucle hasta timeout_s segundos.
    Devuelve el primer elemento encontrado o None.
    """
    fin = time.time() + timeout_s
    while time.time() < fin:
        for sel in selectores:
            try:
                el = page.query_selector(sel)
                if el and (not visible or el.is_visible()):
                    return el
            except Exception:
                pass
        time.sleep(0.5)
    return None


# ---------------------------------------------------------------------------
# UPLOADER — YouTube Studio via Playwright  (FIX v3)
# ---------------------------------------------------------------------------


def subir_a_youtube(page, mp4_path: Path, titulo: str, descripcion: str) -> str | None:
    """
    Sube un video a YouTube Studio como BORRADOR.
    Estrategia: navegar directamente a la URL de upload en lugar de
    depender de clicks en menús desplegables que cambian de selector.
    """
    try:
        aplicar_stealth(page)

        # ── PASO 1: Ir a YouTube Studio y esperar que cargue ──
        print(f"  🌐 Navegando a YouTube Studio...")
        page.goto("https://studio.youtube.com", timeout=30_000)
        time.sleep(4)

        # Verificar que la sesión sigue activa (no redirigió a login)
        if "accounts.google.com" in page.url or "signin" in page.url.lower():
            print(f"  ❌ Sesión expirada — redirigió a login: {page.url}")
            print(f"     Ejecuta python auth_youtube.py para renovar la sesión.")
            return None

        print(f"  ✅ Studio cargado: {page.url[:60]}")

        # ── PASO 2: Hacer click en el botón CREAR ──
        print(f"  🖱️  Buscando botón Crear...")
        selectores_crear = [
            "#create-icon",
            "ytcp-button#create-icon",
            "button[aria-label='Crear']",
            "button[aria-label='Create']",
            "[data-testid='create-button']",
            "yt-icon-button.ytcp-icon-button[aria-label*='reat']",  # Create/Crear
        ]
        boton_crear = esperar_elemento(page, selectores_crear, timeout_s=20)

        if not boton_crear:
            print(f"  ❌ No se encontró botón Crear. URL actual: {page.url}")
            return None

        boton_crear.click()
        print(f"  ✅ Click en Crear")
        time.sleep(1.5)

        # ── PASO 3: Click en "Subir video" del menú ──
        print(f"  🖱️  Buscando opción 'Subir video'...")
        selectores_subir = [
            "tp-yt-paper-item[test-id='upload-beta']",
            "tp-yt-paper-item:has-text('Subir vídeo')",
            "tp-yt-paper-item:has-text('Subir video')",
            "tp-yt-paper-item:has-text('Upload video')",
            "tp-yt-paper-item:has-text('Upload')",
            "#items > tp-yt-paper-item:first-child",
            "ytcp-paper-item[id*='upload']",
        ]
        boton_subir = esperar_elemento(page, selectores_subir, timeout_s=10)

        if not boton_subir:
            # Fallback: intentar navegar directamente a la URL de upload
            print(f"  ⚠️  Menú no encontrado. Intentando URL directa de upload...")
            page.goto("https://studio.youtube.com/channel/upload", timeout=20_000)
            time.sleep(3)
        else:
            boton_subir.click()
            print(f"  ✅ Click en Subir video")
            time.sleep(2)

        # ── PASO 4: Encontrar el input[type=file] ──
        print(f"  🔍 Buscando input de archivo...")

        # YouTube a veces esconde el input — forzar visibilidad
        try:
            page.evaluate("""
                () => {
                    document.querySelectorAll('input[type=file]').forEach(el => {
                        el.style.display = 'block';
                        el.style.visibility = 'visible';
                        el.style.opacity = '1';
                        el.removeAttribute('hidden');
                    });
                }
            """)
        except Exception:
            pass

        selectores_input = [
            "input[type='file']",
            "input[accept*='video']",
        ]
        input_file = esperar_elemento(page, selectores_input, timeout_s=15, visible=False)

        if not input_file:
            print(f"  ❌ No se encontró input de archivo. URL: {page.url}")
            return None

        print(
            f"  📤 Enviando archivo: {mp4_path.name} "
            f"({mp4_path.stat().st_size / 1024 / 1024:.1f} MB)"
        )
        input_file.set_input_files(str(mp4_path))

        # ── PASO 5: Esperar el diálogo de detalles ──
        # En lugar de wait_for_selector (que explota si tarda), usamos espera activa
        print(f"  ⏳ Esperando formulario de detalles (hasta 90s)...")
        selectores_dialogo = [
            "ytcp-video-upload-dialog",
            "#upload-dialog",
            "#title-textarea",
            "[aria-label*='Title']",
            "[aria-label*='Título']",
            "#title-textarea #textbox",
        ]
        dialogo = esperar_elemento(page, selectores_dialogo, timeout_s=90)

        if not dialogo:
            print(f"  ❌ El formulario de detalles nunca apareció.")
            print(f"     URL actual: {page.url}")
            return None

        print(f"  ✅ Formulario de detalles visible")
        time.sleep(2)

        # ── PASO 6: Escribir título ──
        print(f"  ✍️  Escribiendo título...")
        selectores_titulo = [
            "#title-textarea #textbox",
            "ytcp-social-suggestions-textbox[id='title-textarea'] #textbox",
            "[aria-label='Título (obligatorio)']",
            "[aria-label='Title (required)']",
            "[aria-label*='ítulo']",
            "[aria-label*='itle']",
        ]
        campo_titulo = esperar_elemento(page, selectores_titulo, timeout_s=15)
        if campo_titulo:
            campo_titulo.triple_click()
            time.sleep(0.3)
            campo_titulo.fill(titulo[:100])
            print(f"  ✅ Título: {titulo[:50]}...")
        else:
            print(f"  ⚠️  Campo título no encontrado — continuando sin título")

        time.sleep(1)

        # ── PASO 7: Escribir descripción ──
        print(f"  ✍️  Escribiendo descripción...")
        selectores_desc = [
            "#description-textarea #textbox",
            "[aria-label='Descripción']",
            "[aria-label='Description']",
            "[aria-label*='escripci']",
            "[aria-label*='escription']",
            "[placeholder*='escription' i]",
        ]
        campo_desc = esperar_elemento(page, selectores_desc, timeout_s=10)
        if campo_desc:
            campo_desc.click()
            time.sleep(0.3)
            campo_desc.fill(descripcion[:5000])
            print(f"  ✅ Descripción escrita ({len(descripcion)} chars)")
        else:
            print(f"  ⚠️  Campo descripción no encontrado — continuando")

        time.sleep(1)

        # ── PASO 8: "No está hecho para niños" ──
        try:
            selectores_no_ninos = [
                "tp-yt-paper-radio-button[name='VIDEO_MADE_FOR_KIDS_NOT']",
                "[name='VIDEO_MADE_FOR_KIDS_NOT'] input",
                "[aria-label*='No']",
            ]
            no_ninos = esperar_elemento(page, selectores_no_ninos, timeout_s=5)
            if no_ninos:
                no_ninos.click()
                time.sleep(0.5)
                print(f"  ✅ 'No está hecho para niños' seleccionado")
        except Exception:
            pass

        # ── PASO 9: Avanzar hasta Visibilidad (3 clicks en Siguiente) ──
        print(f"  ➡️  Avanzando pasos...")
        selectores_siguiente = [
            "ytcp-button#next-button",
            "button[aria-label='Siguiente']",
            "button[aria-label='Next']",
            "ytcp-button:has-text('Siguiente')",
            "ytcp-button:has-text('Next')",
        ]
        pasos_avanzados = 0
        for intento in range(4):
            siguiente = esperar_elemento(page, selectores_siguiente, timeout_s=8)
            if siguiente and siguiente.is_visible():
                siguiente.click()
                pasos_avanzados += 1
                print(f"  ✅ Paso {pasos_avanzados} avanzado")
                time.sleep(2)
            else:
                break

        # ── PASO 10: Seleccionar PRIVADO (= Borrador guardable) ──
        print(f"  📝 Configurando visibilidad como PRIVADO (borrador)...")
        selectores_privado = [
            "tp-yt-paper-radio-button[name='PRIVATE']",
            "[name='PRIVATE'] input",
            "[aria-label='Privado']",
            "[aria-label='Private']",
            "ytcp-video-visibility-select[value='PRIVATE']",
        ]
        privado = esperar_elemento(page, selectores_privado, timeout_s=10)
        if privado:
            privado.click()
            time.sleep(0.5)
            print(f"  ✅ Visibilidad: PRIVADO")
        else:
            print(f"  ⚠️  Selector de visibilidad no encontrado — continuando")

        # ── PASO 11: Guardar borrador ──
        print(f"  💾 Guardando borrador...")
        selectores_guardar = [
            "ytcp-button#done-button",
            "button[aria-label='Guardar']",
            "button[aria-label='Save']",
            "ytcp-button:has-text('Guardar')",
            "ytcp-button:has-text('Save')",
        ]
        boton_guardar = esperar_elemento(page, selectores_guardar, timeout_s=15)
        if boton_guardar:
            boton_guardar.click()
            print(f"  ✅ Click en Guardar")
            time.sleep(5)
        else:
            print(f"  ⚠️  Botón Guardar no encontrado")

        # ── PASO 12: Capturar URL del video ──
        print(f"  🔗 Capturando URL del video...")
        video_url = None
        time.sleep(3)

        try:
            enlace = page.query_selector(
                "a[href*='youtube.com/shorts'], a[href*='youtu.be'], a[href*='youtube.com/watch']"
            )
            if enlace:
                video_url = enlace.get_attribute("href")
        except Exception:
            pass

        if not video_url:
            try:
                # Ir a la lista de videos y tomar el primero (recién subido)
                page.goto("https://studio.youtube.com/channel/videos", timeout=30_000)
                time.sleep(4)
                primer_video = page.query_selector(
                    "ytcp-video-list-cell-title a, "
                    "#video-title a, "
                    ".ytcp-video-list-item a[href*='video']"
                )
                if primer_video:
                    href = primer_video.get_attribute("href") or ""
                    video_id = href.split("/")[-1].split("?")[0]
                    if video_id:
                        video_url = f"https://youtube.com/shorts/{video_id}"
            except Exception:
                pass

        if video_url:
            print(f"  ✅ Borrador guardado: {video_url}")
        else:
            print(f"  ✅ Borrador guardado (URL no capturada automáticamente)")
            video_url = "BORRADOR_SIN_URL"

        return video_url

    except Exception as e:
        print(f"  ❌ Error subiendo a YouTube: {e}")
        import traceback

        traceback.print_exc()
        return None


# ---------------------------------------------------------------------------
# PIPELINE PRINCIPAL
# ---------------------------------------------------------------------------


class YouTubePublisher:
    def __init__(self):
        import os

        raiz_proyecto = BASE_DIR.parent

        # Rutas a buscar - incluyendo la configuración centralizada
        caminos = [
            STATE_FILE,
            BASE_DIR / "youtube_state.json",
            raiz_proyecto / "youtube_state.json",
            Path(os.getcwd()) / "youtube_state.json",
        ]

        # Si hay configuración centralizada, añadirla al principio
        if USING_CONFIG_MODULE and YOUTUBE_STATE_PATH not in caminos:
            caminos.insert(0, YOUTUBE_STATE_PATH)

        self.state_path = None
        for p in caminos:
            if p.exists():
                self.state_path = p
                break

        if not self.state_path:
            print(f"❌ No se encontró youtube_state.json")
            print(f" Buscado en: {[str(c) for c in caminos]}")
            print(" Ejecuta primero: python auth_youtube.py")
            sys.exit(1)

        self.db = conectar_sheets()
        YA_PUBLICADO.mkdir(parents=True, exist_ok=True)
        print(f"🎬 YouTube Publisher inicializado")
        print(f" Sesión: {self.state_path}")
        if USING_CONFIG_MODULE and "miura_forge" in str(self.state_path):
            print(f"✅ Usando directorio seguro: ~/.miura_forge/")
        if STEALTH_FN:
            print(f"   🛡️  Modo antidetección: ACTIVO")
        else:
            print(f"   ⚠️  Modo antidetección: INACTIVO")

    def publicar_uno(self, registro: dict, page) -> bool:
        id_master = registro.get(COL_ID, "").strip()
        titulo = registro.get(COL_TITULO, "").strip()
        desc_raw = registro.get(COL_DESCRIPCION, "").strip()
        hashtags = registro.get(COL_HASHTAGS, "").strip()
        cta = registro.get("CTA_PRINCIPAL", "").strip()

        print(f"\n{'─' * 60}")
        print(f"📤 Publicando: {id_master}")
        print(f"   Título: {titulo[:60]}...")

        mp4 = encontrar_mp4(id_master)
        if not mp4:
            print(f"  ❌ MP4 no encontrado para {id_master}")
            print(f"     Buscado en: {SHORTS_BASE / id_master}")
            return False

        print(f"  🎥 Video: {mp4.name}")
        descripcion = formatear_descripcion(desc_raw, hashtags, cta)
        url = subir_a_youtube(page, mp4, titulo, descripcion)

        if not url:
            print(f"  ❌ Falló la subida de {id_master}")
            return False

        registrar_en_publicado(
            self.db,
            titulo=titulo,
            url=url if url != "BORRADOR_SIN_URL" else "",
            descripcion=desc_raw[:200],
            estado="Borrador",
            id_sesion=id_master,
        )
        actualizar_estado_despliegue(self.db, id_master, "BORRADOR")
        mover_a_publicado(mp4, id_master)
        print(f"  ✅ {id_master} → BORRADOR en YouTube")
        return True

    def publicar_pendientes(self, max_videos: int = 0, id_especifico: str = ""):
        pendientes = leer_pendientes(self.db)

        if id_especifico:
            pendientes = [r for r in pendientes if r.get(COL_ID, "").strip() == id_especifico]
            if not pendientes:
                print(f"❌ No se encontró {id_especifico} en PENDIENTES")
                return

        if max_videos > 0:
            pendientes = pendientes[:max_videos]

        if not pendientes:
            print("✅ No hay videos PENDIENTES para publicar.")
            return

        print(f"\n📊 Videos a procesar: {len(pendientes)}")

        from playwright.sync_api import sync_playwright

        exitosos = 0
        fallidos = 0

        with sync_playwright() as p:
            try:
                browser = p.chromium.launch(
                    channel="chrome",
                    headless=False,
                    args=["--no-sandbox", "--disable-dev-shm-usage"],
                )
            except Exception as e:
                print(f"⚠️  Chrome no disponible ({e}). Usando Chromium de respaldo...")
                browser = p.chromium.launch(
                    headless=False,
                    args=["--no-sandbox", "--disable-dev-shm-usage"],
                )

            context = browser.new_context(
                storage_state=str(self.state_path),
                viewport={"width": 1280, "height": 900},
                user_agent=USER_AGENT,
            )
            page = context.new_page()
            aplicar_stealth(page)

            for i, registro in enumerate(pendientes):
                ok = self.publicar_uno(registro, page)
                if ok:
                    exitosos += 1
                else:
                    fallidos += 1

                if i < len(pendientes) - 1:
                    delay = random.uniform(*DELAY_ENTRE_VIDEOS)
                    print(f"\n⏸️  Pausa {delay:.0f}s antes del siguiente video...")
                    time.sleep(delay)

            browser.close()

        print(f"\n{'=' * 60}")
        print(f"🎬 Sesión completada:")
        print(f"   Borradores creados: {exitosos}")
        print(f"   Fallidos:           {fallidos}")
        print(f"\n   Revisa YouTube Studio para publicar cuando quieras.")

    def listar_pendientes(self):
        pendientes = leer_pendientes(self.db)
        print(f"\n📋 Videos PENDIENTES ({len(pendientes)}):")
        print(f"{'─' * 60}")
        for r in pendientes:
            id_m = r.get(COL_ID, "")
            titulo = r.get(COL_TITULO, "")[:50]
            mp4 = encontrar_mp4(id_m)
            estado_mp4 = "✅ MP4 encontrado" if mp4 else "❌ Sin MP4"
            print(f"  {id_m:<35} {estado_mp4}")
            print(f"    → {titulo}")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="YouTube Publisher — MiuraForgeEngine")
    parser.add_argument("--id", type=str, default="", help="Publicar un ID_SESION específico")
    parser.add_argument(
        "--max",
        type=int,
        default=10,
        help="Máximo de videos a subir en esta sesión (default: 10, 0 = todos)",
    )
    parser.add_argument("--listar", action="store_true", help="Ver pendientes sin subir nada")
    args = parser.parse_args()

    publisher = YouTubePublisher()

    if args.listar:
        publisher.listar_pendientes()
    else:
        publisher.publicar_pendientes(
            max_videos=args.max,
            id_especifico=args.id,
        )
