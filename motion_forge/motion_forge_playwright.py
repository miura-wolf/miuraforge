"""
motion_forge_playwright.py — MiuraForgeEngine
================================================
Motor de automatización para Meta AI image-to-video.

Estrategia de intercepción (v3 — Solución #2):
  ┌─────────────────────────────────────────────────────────────┐
  │  CAPA 1 — Interceptor de red fbcdn.net (método principal)   │
  │                                                             │
  │  Captura URLs de MP4 directamente desde respuestas HTTP     │
  │  del dominio scontent.xx.fbcdn.net — donde Meta AI sirve   │
  │  sus videos generados con tokens de autenticación.          │
  │  Filtros: dominio fbcdn.net + rutas /t66. /t6/ /v/t .mp4  │
  │                                                             │
  │  CAPA 2 — Descarga con page.request (cookies activas)       │
  │                                                             │
  │  page.request.get() usa las cookies de sesión del browser.  │
  │  Resuelve el 403 que daba requests.get() con fbcdn.net.    │
  │  Si falla, reintenta con requests + cookies extraídas.      │
  │                                                             │
  │  CAPA 3 — Botón de descarga nativo (fallback click)         │
  │                                                             │
  │  Si el interceptor no captura nada, busca el botón de       │
  │  descarga de Meta AI y usa expect_download de Playwright.   │
  └─────────────────────────────────────────────────────────────┘

Prerequisito:
  1. pip install playwright && playwright install chromium
  2. python auth_forge.py   <- una sola vez para guardar la sesión

Uso standalone:
  python motion_forge_playwright.py --carpeta output/imagenes_shorts/S1_W1_disciplina
  python motion_forge_playwright.py --cola
  python motion_forge_playwright.py --test --imagen ruta/imagen.png --prompt "slow zoom in"
"""

import os
import sys
import time
import random
import json
import requests
import argparse
import uuid
from pathlib import Path
from playwright.sync_api import sync_playwright, Page, BrowserContext

sys.path.append(str(Path(__file__).resolve().parent.parent))
from motion_forge.queue_manager import (
    cargar_desde_carpeta,
    obtener_siguiente,
    marcar_completado,
    marcar_fallido,
    limpiar_procesando,
    estado_cola,
    reintentar_fallidos,
)

# Importar configuración centralizada
try:
    from core.config import META_STATE_PATH, get_meta_state_path, list_available_meta_accounts

    USING_CONFIG_MODULE = True
except ImportError:
    USING_CONFIG_MODULE = False
    META_STATE_PATH = Path("meta_state.json")

    def get_meta_state_path(index=None):
        if index is None:
            return Path("meta_state.json")
        return Path(f"meta_state_{index}.json")

    def list_available_meta_accounts():
        accounts = []
        if Path("meta_state.json").exists():
            accounts.append((None, Path("meta_state.json")))
        for i in range(1, 10):
            p = Path(f"meta_state_{i}.json")
            if p.exists():
                accounts.append((i, p))
        return accounts

# ---------------------------------------------------------------------------
# CONFIGURACIÓN
# ---------------------------------------------------------------------------

# Usar configuración centralizada si está disponible
STATE_FILE = META_STATE_PATH if USING_CONFIG_MODULE else Path("meta_state.json")
OUTPUT_BASE = Path("forja_local")

DELAY_ENTRE_CLIPS = (8, 15)
DELAY_ENTRE_SHORTS = (20, 40)

TIMEOUT_GENERACION = 150_000  # ms (Aumentado a 150s para mayor robustez)
TIMEOUT_NAVEGACION = 30_000  # ms

# Estrategia de captura de variantes:
# Después de detectar el primer video, esperar este tiempo adicional
# para que el interceptor capture la versión final de mayor calidad.
ESPERA_VARIANTES_SEG = 20  # segundos

# Tamaño mínimo para considerar una URL como video real (no preview/thumbnail)
TAMANO_MINIMO_KB = 500  # KB — variantes menores se descartan

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/120.0.0.0 Safari/537.36"
)

URL_META_AI = "https://www.meta.ai"


# ---------------------------------------------------------------------------
# PROGRESO POR CLIP — persistencia en JSON para no repetir trabajo
# ---------------------------------------------------------------------------


def _progreso_path(output_dir: Path) -> Path:
    """Ruta del archivo JSON de progreso dentro de la carpeta del Short."""
    return output_dir / "_progreso.json"


def _cargar_progreso(output_dir: Path) -> dict:
    """
    Carga el progreso guardado de clips ya completados.
    Formato: { "clip_01": ["ruta/clip_01_aaa.mp4", ...], ... }
    """
    p = _progreso_path(output_dir)
    if p.exists():
        try:
            return json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            return {}
    return {}


def _guardar_progreso(output_dir: Path, progreso: dict):
    """Guarda el diccionario de progreso en disco atomicamente."""
    p = _progreso_path(output_dir)
    tmp = p.with_suffix(".tmp")
    try:
        tmp.write_text(json.dumps(progreso, indent=2, ensure_ascii=False), encoding="utf-8")
        tmp.replace(p)
    except Exception as e:
        print(f"    ⚠️  No se pudo guardar progreso: {e}")


# ---------------------------------------------------------------------------
# DESCARGA — dos métodos
# ---------------------------------------------------------------------------


def descargar_video_con_session(page: Page, url: str, output_path: Path) -> bool:
    """
    Descarga un MP4 usando page.request.get() con cookies activas del browser.
    Resuelve el 403 que da requests.get() con URLs fbcdn.net autenticadas.
    """
    try:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        response = page.request.get(url, timeout=60_000)

        if response.status != 200:
            print(f"    ⚠️  HTTP {response.status} descargando con sesión")
            return False

        body = response.body()
        if len(body) < 10_000:
            print(f"    ⚠️  Respuesta muy pequeña ({len(body)} bytes) — no es un video real")
            return False

        with open(output_path, "wb") as f:
            f.write(body)

        size_kb = len(body) / 1024
        print(f"    💾 Guardado (session): {output_path.name} ({size_kb:.0f} KB)")
        return True

    except Exception as e:
        print(f"    ⚠️  Error descargando con sesión: {e}")
        return False


def descargar_video_requests(url: str, output_path: Path, cookies: dict = None) -> bool:
    """
    Fallback: descarga con requests.get() + cookies extraídas del browser.
    """
    try:
        headers = {"User-Agent": USER_AGENT}
        r = requests.get(url, stream=True, timeout=60, headers=headers, cookies=cookies or {})
        r.raise_for_status()
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
        size_kb = output_path.stat().st_size / 1024
        print(f"    💾 Guardado (requests): {output_path.name} ({size_kb:.0f} KB)")
        return True
    except Exception as e:
        print(f"    ❌ Error descargando con requests: {e}")
        return False


# ---------------------------------------------------------------------------
# INTERCEPTOR DE RED v3 — filtrado por dominio fbcdn.net
# ---------------------------------------------------------------------------


def crear_interceptor(videos_capturados: list, urls_ignoradas: set):
    """
    v4: Captura tuplas (url, content_length) de video de Meta AI.

    Guarda el Content-Length junto a la URL para que el paso de descarga
    pueda ordenar por tamaño y descargar SOLO la variante más grande,
    que es la de mayor calidad. Meta AI suele servir 2-3 variantes:
      - Preview/thumbnail animado (~200-500 KB) ← NO queremos esta
      - Video final comprimido (~1-5 MB)         ← ESTA es la buena
      - Video final calidad alta (~5-20 MB)      ← o esta si aparece

    Meta AI sirve sus videos en:
      https://scontent.xx.fbcdn.net/v/t66.36240-6/video.mp4?...
      https://scontent.fsxr1-2.fna.fbcdn.net/o1/v/t6/f2/m421/video.mp4
    """

    def on_response(response):
        try:
            url = response.url
            ct = response.headers.get("content-type", "").lower()
            size = int(response.headers.get("content-length", "0") or "0")

            # Filtro principal: dominio fbcdn.net con rutas de video de Meta AI
            es_fbcdn_video = "fbcdn.net" in url and (
                "/t66." in url or "/t6/" in url or "/v/t" in url or ".mp4" in url
            )

            # Filtro secundario: content-type video o extensión .mp4
            es_mp4_directo = (
                "video/mp4" in ct
                or "video/" in ct
                or url.lower().endswith(".mp4")
                or ".mp4?" in url.lower()
            )

            # Ignorar segmentos muy pequeños (thumbnails estáticos <50KB)
            if size > 0 and size < 50_000:
                return

            # Verificar que no esté ya capturada (comparar solo por URL)
            urls_ya = {u for u, _ in videos_capturados}
            if es_fbcdn_video or es_mp4_directo:
                if url not in urls_ya and url not in urls_ignoradas:
                    videos_capturados.append((url, size))
                    size_kb = f"{size / 1024:.0f} KB" if size > 0 else "tamaño desconocido"
                    print(f"    🎬 Video interceptado [{size_kb}]: ...{url[-55:]}")
        except Exception:
            pass

    return on_response


# ---------------------------------------------------------------------------
# DETECTOR DOM v3 — compatible con blob: y srcObject
# ---------------------------------------------------------------------------


def _contar_videos_dom(page: Page) -> int:
    """
    v3: Acepta blob:, http: y srcObject.
    Meta AI cambió a blob: URLs en 2025, lo que hacía que el conteo
    anterior siempre fuera 0 (solo buscaba src que empezara por 'http').
    """
    try:
        return page.evaluate("""() => {
            return Array.from(document.querySelectorAll('video'))
                .filter(v =>
                    (v.src && (v.src.startsWith('http') || v.src.startsWith('blob')))
                    || v.srcObject != null
                    || (v.currentSrc && v.currentSrc.length > 0)
                ).length;
        }""")
    except Exception:
        return 0


# ---------------------------------------------------------------------------
# BOTÓN DE DESCARGA — fallback click
# ---------------------------------------------------------------------------


def _descargar_via_click(
    page: Page, output_dir: Path, clip_nombre: str, urls_ignoradas: set
) -> list:
    """
    Descarga usando el botón nativo de Meta AI con expect_download.
    Último recurso si el interceptor de red no capturó nada.
    """
    clips_descargados = []

    selectores_descarga = [
        "[aria-label*='download' i]",
        "[data-testid*='download']",
        "button:has-text('Download')",
        "a[download]",
        "a[href*='.mp4']",
        "[aria-label*='Descargar' i]",
        "[data-testid*='save']",
        "button[title*='download' i]",
    ]

    try:
        for sel in selectores_descarga:
            try:
                botones = page.query_selector_all(sel)
            except Exception:
                continue
            if not botones:
                continue

            boton = botones[-1]

            with page.expect_download(timeout=60_000) as download_info:
                boton.click(force=True)

            download = download_info.value
            nombre_archivo = f"{clip_nombre}_{uuid.uuid4().hex[:4]}.mp4"
            output_path = output_dir / nombre_archivo
            output_path.parent.mkdir(parents=True, exist_ok=True)
            download.save_as(str(output_path))

            size_kb = output_path.stat().st_size / 1024
            print(f"    💾 Descargado via click: {nombre_archivo} ({size_kb:.0f} KB)")
            clips_descargados.append(str(output_path))

            if download.url:
                urls_ignoradas.add(download.url)
            break

    except Exception as e:
        print(f"    ⚠️  Descarga via click falló: {e}")

    return clips_descargados


# ---------------------------------------------------------------------------
# SUBIDA + ANIMACIÓN
# ---------------------------------------------------------------------------


def subir_imagen_y_animar(
    page: Page,
    imagen_path: str,
    prompt_animacion: str,
    output_dir: Path,
    clip_nombre: str,
    urls_ignoradas: set = None,
    videos_red: list = None,
) -> list:
    """
    Sube una imagen a Meta AI, envía el prompt y descarga el video.

    Capas de detección y descarga:
      1. Interceptor de red (fbcdn.net) — detecta y descarga con page.request
      2. DOM <video> con blob:/http: — detección alternativa
      3. Botón de descarga nativo — último recurso
    """
    if urls_ignoradas is None:
        urls_ignoradas = set()
    if videos_red is None:
        videos_red = []

    videos_dom_base = _contar_videos_dom(page)
    urls_red_base = len(videos_red)
    print(f"    📊 Videos DOM base: {videos_dom_base} | URLs red base: {urls_red_base}")

    if "meta.ai" not in page.url:
        print(f"    🌐 Navegando a Meta AI...")
        page.goto(URL_META_AI, timeout=TIMEOUT_NAVEGACION)
        time.sleep(3)

    clips_descargados = []

    try:
        # ── PASO 1: Subir imagen ─────────────────────────────────────
        print(f"    📎 Subiendo imagen: {Path(imagen_path).name}")

        file_input = None
        for sel in [
            "input[type='file']",
            "input[accept*='image']",
            "[data-testid*='file']",
            "[aria-label*='image' i]",
            "input[accept*='video']",
        ]:
            try:
                elementos = page.query_selector_all(sel)
                if elementos:
                    file_input = elementos[0]
                    break
            except Exception:
                continue

        if not file_input:
            page.evaluate("""
                const inputs = document.querySelectorAll('input[type=file]');
                inputs.forEach(i => {
                    i.style.display    = 'block';
                    i.style.opacity    = '1';
                    i.style.visibility = 'visible';
                    i.style.position   = 'static';
                });
            """)
            time.sleep(0.5)
            file_input = page.query_selector("input[type='file']")

        if not file_input:
            raise Exception(
                "CUENTA_BLOQUEADA: Meta AI no muestra interfaz de subida. "
                "Posible bloqueo de cuenta o sesión expirada."
            )

        file_input.set_input_files(imagen_path)
        time.sleep(2)

        # ── PASO 2: Prompt ───────────────────────────────────────────
        print(f"    ✍️  Prompt: {prompt_animacion[:70]}...")

        textarea = None
        for sel in [
            "textarea",
            "[contenteditable='true']",
            "[role='textbox']",
            "[data-testid*='composer']",
            "[placeholder*='message' i]",
            "[placeholder*='prompt' i]",
            "[placeholder*='Describe' i]",
        ]:
            try:
                el = page.query_selector(sel)
                if el and el.is_visible():
                    textarea = el
                    break
            except Exception:
                continue

        if textarea:
            textarea.click()
            time.sleep(0.3)
            textarea.fill(prompt_animacion)
            time.sleep(0.5)
        else:
            print(f"    ⚠️  No se encontró textarea — enviando solo con Enter")

        # ── PASO 3: Enviar ───────────────────────────────────────────
        page.keyboard.press("Enter")
        print(f"    ⏳ Generando... (puede tardar 40-90 segundos)")

        # ── PASO 4: Esperar primer video + ESPERA_VARIANTES_SEG extra ─
        # Fase A — esperar hasta que llegue el PRIMER video (señal)
        # Fase B — continuar esperando ESPERA_VARIANTES_SEG segundos más
        #          para capturar la versión final de mayor calidad,
        #          que Meta AI suele servir unos segundos después del preview.
        tiempo_inicio = time.time()
        video_listo = False
        timeout_seg = TIMEOUT_GENERACION / 1000
        tiempo_primera = None  # momento en que llegó la primera señal

        while time.time() - tiempo_inicio < timeout_seg:
            # Capturar interceptados hasta ahora
            nuevas_red = videos_red[urls_red_base:]
            hay_nueva_red = len(nuevas_red) > 0
            hay_nueva_dom = _contar_videos_dom(page) > videos_dom_base

            # 🚀 SALIDA TEMPRANA: Si detectamos que ya hay un video de calidad (>=500KB),
            # salimos de la espera inmediatamente para ahorrar tiempo.
            if any(size >= TAMANO_MINIMO_KB * 1024 for _, size in nuevas_red):
                print(
                    f"    🚀 [Salida Temprana] Video de calidad detectado (>= {TAMANO_MINIMO_KB} KB)."
                )
                video_listo = True
                break

            # Primera señal — arrancar cuenta regresiva de espera extra
            if (hay_nueva_red or hay_nueva_dom) and tiempo_primera is None:
                origen = "RED" if hay_nueva_red else "DOM"
                n_red = len(nuevas_red)
                print(
                    f"    ✅ Primera señal [{origen}]: {n_red} URL(s) red | esperando {ESPERA_VARIANTES_SEG}s más o salida temprana..."
                )
                tiempo_primera = time.time()

            # Fase B — ya pasaron los segundos de espera extra → salir
            if tiempo_primera is not None:
                espera_transcurrida = time.time() - tiempo_primera
                restante = int(ESPERA_VARIANTES_SEG - espera_transcurrida)
                if espera_transcurrida >= ESPERA_VARIANTES_SEG:
                    n_total = len(videos_red) - urls_red_base
                    print(f"    ✅ Espera completada — {n_total} variante(s) capturada(s) en total")
                    video_listo = True
                    break
                # Mostrar cuenta regresiva cada 5s
                if restante % 5 == 0 and restante > 0:
                    n_ahora = len(videos_red) - urls_red_base
                    print(
                        f"    ⏳ Capturando variantes... {restante}s restantes ({n_ahora} URL(s) hasta ahora)"
                    )

            else:
                elapsed = int(time.time() - tiempo_inicio)
                if elapsed > 0 and elapsed % 15 == 0:
                    print(f"    ⏳ Esperando primer video... {elapsed}s")

            time.sleep(1.5)

        if not video_listo:
            print(f"    ⚠️  Timeout ({int(timeout_seg)}s) — sin video para {clip_nombre}")
            return []

        # ── PASO 5: Descargar TODAS las variantes ≥ TAMANO_MINIMO_KB ─
        # Se filtran previews pequeños y se descargan todas las que
        # superan el umbral mínimo. El usuario verifica cuál es la buena.
        # Nombrado: clip_01_aaa.mp4, clip_01_bbb.mp4, etc.
        nuevas_todas = [(u, s) for u, s in videos_red[urls_red_base:] if u not in urls_ignoradas]

        # Separar por umbral de tamaño
        nuevas_ok = [(u, s) for u, s in nuevas_todas if s == 0 or s >= TAMANO_MINIMO_KB * 1024]
        nuevas_pequeñas = [(u, s) for u, s in nuevas_todas if s > 0 and s < TAMANO_MINIMO_KB * 1024]

        print(f"    📊 Variantes capturadas: {len(nuevas_todas)} total")
        if nuevas_pequeñas:
            print(
                f"       🗑️  {len(nuevas_pequeñas)} descartada(s) por ser <{TAMANO_MINIMO_KB} KB (previews):"
            )
            for u, s in nuevas_pequeñas:
                print(f"          {s // 1024:>5} KB  ...{u[-45:]}")
        if nuevas_ok:
            print(f"       📥 {len(nuevas_ok)} a descargar (≥{TAMANO_MINIMO_KB} KB):")
            for u, s in nuevas_ok:
                kb = f"{s // 1024} KB" if s > 0 else "? KB"
                print(f"          {kb:>8}  ...{u[-45:]}")

        # Marcar todas (ok + pequeñas) para no repetirlas
        for u, _ in nuevas_todas:
            urls_ignoradas.add(u)

        if not nuevas_ok:
            print(f"    ⚠️  Ninguna variante superó el umbral de {TAMANO_MINIMO_KB} KB")

        if nuevas_ok:
            # Extraer cookies una sola vez para toda la tanda
            cookies_dict = {}
            try:
                browser_cookies = page.context.cookies()
                cookies_dict = {
                    c["name"]: c["value"]
                    for c in browser_cookies
                    if any(d in c.get("domain", "") for d in ["fbcdn", "meta", "facebook"])
                }
            except Exception as e:
                print(f"    ⚠️  Error extrayendo cookies: {e}")

            for idx, (url_mp4, size) in enumerate(nuevas_ok, start=1):
                nombre_archivo = f"{clip_nombre}_{uuid.uuid4().hex[:4]}.mp4"
                output_path = output_dir / nombre_archivo
                kb = f"{size // 1024} KB" if size > 0 else "? KB"
                print(f"    📥 [{idx}/{len(nuevas_ok)}] {nombre_archivo} ({kb})")

                ok = descargar_video_con_session(page, url_mp4, output_path)
                if not ok:
                    print(f"    🔄 Reintentando con requests + cookies...")
                    ok = descargar_video_requests(url_mp4, output_path, cookies_dict)

                if ok:
                    clips_descargados.append(str(output_path))

        # ── PASO 6: Fallback — botón de descarga nativo ──────────────
        if not clips_descargados:
            print(f"    🔄 Fallback: botón de descarga de Meta AI...")
            clips_descargados = _descargar_via_click(page, output_dir, clip_nombre, urls_ignoradas)

        # ── PASO 7: Último recurso — URL http del DOM ─────────────────
        if not clips_descargados:
            print(f"    🔄 Último recurso: URL http del DOM...")
            video_src = page.evaluate("""() => {
                const videos = Array.from(document.querySelectorAll('video'))
                    .filter(v => v.src && v.src.startsWith('http'));
                return videos.length > 0 ? videos[videos.length - 1].src : null;
            }""")
            if video_src and video_src not in urls_ignoradas:
                nombre_archivo = f"{clip_nombre}_{uuid.uuid4().hex[:4]}.mp4"
                output_path = output_dir / nombre_archivo
                ok = descargar_video_con_session(page, video_src, output_path)
                if not ok:
                    ok = descargar_video_requests(video_src, output_path)
                if ok:
                    clips_descargados.append(str(output_path))
                    urls_ignoradas.add(video_src)

    except Exception as e:
        if "CUENTA_BLOQUEADA" in str(e):
            raise
        print(f"    ❌ Error en subir_imagen_y_animar: {e}")

    return clips_descargados


# ---------------------------------------------------------------------------
# MOTOR PRINCIPAL
# ---------------------------------------------------------------------------


class MotionForgePlaywright:
    def __init__(self, state_file: str = str(STATE_FILE)):
        OUTPUT_BASE.mkdir(parents=True, exist_ok=True)

        self._cuentas = self._cargar_cuentas(state_file)
        self._cuenta_idx = 0
        self._clips_en_cuenta_actual = 0

        if not self._cuentas:
            print("No se encontro ningun archivo de sesion")
            print("Ejecuta primero: python auth_forge.py")
            sys.exit(1)

        print(f"Cuentas disponibles: {len(self._cuentas)}")
        for i, c in enumerate(self._cuentas):
            print(f"  [{i + 1}] {Path(c).name}")

        self.urls_vistas = set()
        # Lista compartida donde el interceptor deposita URLs de MP4 capturadas
        self._videos_red: list = []

    def _cargar_cuentas(self, state_file: str) -> list:
        cuentas = []
        base = Path(state_file)
        if base.exists():
            cuentas.append(str(base))
        stem = base.stem
        for i in range(1, 10):
            variante = base.parent / f"{stem}_{i}{base.suffix}"
            if variante.exists() and str(variante) not in cuentas:
                cuentas.append(str(variante))
        return cuentas

    @property
    def state_file(self) -> str:
        return self._cuentas[self._cuenta_idx % len(self._cuentas)]

    def _rotar_cuenta(self):
        if len(self._cuentas) > 1:
            self._cuenta_idx = (self._cuenta_idx + 1) % len(self._cuentas)
            self._clips_en_cuenta_actual = 0
            print(f"  🔄 Rotando a cuenta [{self._cuenta_idx + 1}]: {Path(self.state_file).name}")

    def _abrir_browser(self, playwright):
        """
        Abre el browser y registra el interceptor de red fbcdn.net
        en el contexto para capturar URLs de MP4 antes del DOM.
        """
        browser = playwright.chromium.launch(
            headless=True, args=["--no-sandbox", "--disable-dev-shm-usage"]
        )
        context = browser.new_context(
            storage_state=self.state_file,
            viewport={"width": 1280, "height": 800},
            user_agent=USER_AGENT,
        )

        # Registrar interceptor en el contexto del browser
        context.on("response", crear_interceptor(self._videos_red, self.urls_vistas))

        page = context.new_page()
        print(
            f"  🌐 Cargando Meta AI — cuenta [{self._cuenta_idx + 1}]: {Path(self.state_file).name}..."
        )
        page.goto(URL_META_AI, timeout=TIMEOUT_NAVEGACION)
        time.sleep(3)
        return browser, page

    def procesar_short(self, id_sesion: str, clips: list) -> list:
        """
        Procesa todos los clips de un Short.
        - Salta clips ya descargados (según _progreso.json en la carpeta).
        - Rota de cuenta inmediatamente si detecta bloqueo.
        """
        output_dir = OUTPUT_BASE / id_sesion
        output_dir.mkdir(parents=True, exist_ok=True)
        todos_los_clips = []

        # ── Cargar progreso previo ────────────────────────────────────
        progreso = _cargar_progreso(output_dir)
        clips_ya_hechos = set(progreso.keys())

        # Reconstruir lista de clips ya descargados (para el retorno final)
        for nombre_clip, rutas in progreso.items():
            todos_los_clips.extend(rutas)

        clips_pendientes = [c for c in clips if c.get("nombre", "") not in clips_ya_hechos]

        print(f"\n{'─' * 60}")
        print(f"🎬 Procesando Short: {id_sesion}")
        print(f"   Total clips:      {len(clips)}")
        if clips_ya_hechos:
            print(f"   ✅ Ya descargados: {len(clips_ya_hechos)} — {sorted(clips_ya_hechos)}")
        print(f"   ⏳ Pendientes:     {len(clips_pendientes)}")
        print(f"{'─' * 60}")

        if not clips_pendientes:
            print(f"  ✅ Todos los clips ya estaban descargados. Nada que hacer.")
            return todos_los_clips

        with sync_playwright() as p:
            browser, page = self._abrir_browser(p)

            i = 0
            while i < len(clips_pendientes):
                clip = clips_pendientes[i]
                imagen = clip.get("imagen", "")
                prompt = clip.get("prompt", "slow cinematic zoom in")
                nombre = clip.get("nombre", f"clip_{i + 1:02d}")

                if not imagen or not Path(imagen).exists():
                    print(f"  ⚠️  Imagen no encontrada: {imagen} — saltando")
                    i += 1
                    continue

                MAX_REINTENTOS = 2
                clip_ok = False
                cuenta_rotada = False

                for intento in range(MAX_REINTENTOS):
                    str_intento = (
                        f" (Intento {intento + 1}/{MAX_REINTENTOS})" if intento > 0 else ""
                    )
                    idx_global = len(clips_ya_hechos) + i + 1
                    print(f"\n  [{idx_global}/{len(clips)}] {nombre}{str_intento}")

                    try:
                        clips_generados = subir_imagen_y_animar(
                            page,
                            imagen,
                            prompt,
                            output_dir,
                            nombre,
                            urls_ignoradas=self.urls_vistas,
                            videos_red=self._videos_red,
                        )

                        if clips_generados:
                            todos_los_clips.extend(clips_generados)
                            self._clips_en_cuenta_actual += 1
                            clip_ok = True

                            # ── Guardar progreso inmediatamente ──────
                            progreso[nombre] = clips_generados
                            _guardar_progreso(output_dir, progreso)
                            print(
                                f"    💾 Progreso guardado: {nombre} → {len(clips_generados)} archivo(s)"
                            )
                            break
                        else:
                            print(f"    🔁 Sin resultado. Reintentando en 5s...")
                            time.sleep(5)
                            if intento < MAX_REINTENTOS - 1:
                                page.reload(timeout=TIMEOUT_NAVEGACION)
                                time.sleep(5)

                    except Exception as e:
                        if "CUENTA_BLOQUEADA" in str(e):
                            print(f"  🛑 Cuenta [{self._cuenta_idx + 1}] bloqueada o expirada.")
                            try:
                                browser.close()
                            except Exception:
                                pass

                            if len(self._cuentas) > 1:
                                self._cuenta_idx = (self._cuenta_idx + 1) % len(self._cuentas)
                                self._clips_en_cuenta_actual = 0
                                print(
                                    f"  🔄 Rotando AHORA a [{self._cuenta_idx + 1}]: {Path(self.state_file).name}"
                                )
                                time.sleep(8)
                                browser, page = self._abrir_browser(p)
                                cuenta_rotada = True
                                break
                            else:
                                print(f"  ❌ Sin más cuentas. Abortando Short.")
                                return todos_los_clips
                        else:
                            raise e

                if clip_ok or not cuenta_rotada:
                    i += 1

                if clip_ok and i < len(clips_pendientes):
                    delay = random.uniform(*DELAY_ENTRE_CLIPS)
                    print(f"  ⏸️  Pausa {delay:.0f}s antes del siguiente clip...")
                    time.sleep(delay)

            try:
                browser.close()
            except Exception:
                pass

        print(f"\n  ✅ Short {id_sesion} completado: {len(todos_los_clips)} clips")
        return todos_los_clips

    def procesar_cola(self):
        """Procesa todos los Shorts en la cola de pendientes."""
        huerfanas = limpiar_procesando()
        if huerfanas:
            print(f"🔄 {huerfanas} tarea(s) recuperadas de sesión anterior")

        estado = estado_cola()
        print(f"\n📊 Estado de la cola:")
        print(f"   Pendientes:  {estado['pendientes']}")
        print(f"   Completados: {estado['completados']}")
        print(f"   Fallidos:    {estado['fallidos']}")

        if estado["pendientes"] == 0:
            print("\n✅ No hay tareas pendientes.")
            return

        procesados = 0
        while True:
            tarea = obtener_siguiente()
            if not tarea:
                break

            filename, data = tarea
            id_sesion = data["id_sesion"]
            clips = data["clips"]

            try:
                clips_generados = self.procesar_short(id_sesion, clips)

                if len(clips_generados) >= len(clips):
                    marcar_completado(filename, clips_generados)
                    procesados += 1
                else:
                    raise ValueError(
                        f"Descargas incompletas. "
                        f"(Físicos: {len(clips_generados)}/{len(clips)}). "
                        f"Bloqueo inminente asumido por Meta AI."
                    )

            except Exception as e:
                print(f"  ❌ Error procesando {id_sesion}: {e}")
                marcar_fallido(filename, str(e))
                self._rotar_cuenta()
                reintentar_fallidos()

            if estado_cola()["pendientes"] > 0:
                delay = random.uniform(*DELAY_ENTRE_SHORTS)
                print(f"\n⏸️  Pausa {delay:.0f}s antes del siguiente Short...")
                time.sleep(delay)

        print(f"\n{'=' * 60}")
        print(f"🔩 Forja completada: {procesados} Shorts procesados")
        estado_final = estado_cola()
        print(f"   Completados: {estado_final['completados']}")
        print(f"   Fallidos:    {estado_final['fallidos']}")

    def test_conexion(self, imagen_path: str, prompt: str = "slow cinematic zoom in"):
        """Prueba con una sola imagen para verificar que la sesión funciona."""
        print("\n🧪 MODO TEST — 1 clip de prueba")
        clips = [{"imagen": imagen_path, "prompt": prompt, "nombre": "test_clip"}]
        resultado = self.procesar_short("TEST_SHORT", clips)
        if resultado:
            print(f"\n✅ Test exitoso. MP4 guardado en: {resultado[0]}")
        else:
            print("\n❌ Test fallido. Verifica la sesión con: python auth_forge.py")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Motion Forge — Meta AI image-to-video")
    parser.add_argument("--cola", action="store_true", help="Procesar toda la cola de pendientes")
    parser.add_argument("--status", type=str, default="", help="Auditar una carpeta base")
    parser.add_argument(
        "--carpeta", type=str, default="", help="Carpeta de un Short (agrega a cola y procesa)"
    )
    parser.add_argument("--test", action="store_true", help="Modo prueba con una sola imagen")
    parser.add_argument("--imagen", type=str, default="", help="Ruta de imagen para el modo test")
    parser.add_argument(
        "--prompt",
        type=str,
        default="slow cinematic zoom in, smoke drifting upward",
        help="Prompt de animación para el modo test",
    )
    parser.add_argument(
        "--state",
        type=str,
        default=str(STATE_FILE),
        help=f"Archivo de sesión (default: {STATE_FILE})",
    )
    parser.add_argument("--reintentar", action="store_true", help="Reintentar tareas fallidas")
    args = parser.parse_args()

    forge = MotionForgePlaywright(state_file=args.state)

    if args.reintentar:
        n = reintentar_fallidos()
        print(f"↩️  {n} tarea(s) movidas de vuelta a pendientes")

    if args.test:
        if not args.imagen:
            print("❌ --test requiere --imagen ruta/imagen.png")
            sys.exit(1)
        forge.test_conexion(args.imagen, args.prompt)

    elif args.carpeta:
        print(f"📁 Cargando carpeta: {args.carpeta}")
        filename = cargar_desde_carpeta(args.carpeta)
        print(f"✅ Tarea agregada a la cola: {filename}")
        forge.procesar_cola()

    elif args.status:
        from queue_manager import auditar_directorio

        auditar_directorio(args.status)

    elif args.cola:
        forge.procesar_cola()

    else:
        parser.print_help()
