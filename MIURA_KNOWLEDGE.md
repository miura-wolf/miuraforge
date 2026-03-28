# ⚔️ BÚNKER DE CONOCIMIENTO ABSOLUTO - MIURA FORGE ENGINE ⚔️

Este es el documento maestro fundacional del proyecto Miura Forge. Todo el diseño arquitectónico, las lógicas antibaneo, sincronizaciones audiovisuales y las decisiones estratégicas de este flujo avanzado (Idea -> Guion -> Web Automatizada -> Ensamblador de Video -> SEO) están resguardadas aquí bajo absoluta precisión técnica.

---

## 1. ARQUITECTURA ESTRATÉGICA DEL FLUJO
El motor forja videos masivos iterando sobre una arquitectura de módulos altamente especializados en forma de tubería (Pipeline):
1. **Google Sheets (El Oráculo):** Almacena las ideas abstractas, los Guiones de texto depurados, los Títulos (Hooks de Anclaje) y los Metadatos.
2. **Generador de Audio (Voice Engine / Whisper):** Convierte el guion a un archivo `.wav` local usando modelos TTS avanzados. (Paso actualmente manual/semi-automático que precede al ensamblaje final).
3. **Motion Forge (Meta AI / Playwright):** Módulo de automatización que convierte imágenes y prompts en clips MP4. **Integrado ahora en la Forja Total (~Opción 10~).**
4. **Short Assembler (MovieLite / FFMPEG):** Ensamblaje final de video con subtítulos estilo "Hormozi". Se mantiene como paso independiente para control de calidad post-voz.

---

## 2. NÚCLEO WEB AUTOMATIZADO (Meta AI / Playwright)
**Archivo de Producción:** `motion_forge/motion_forge_playwright.py`

### La Tormenta Inicial de la UI de Meta
Meta AI bloqueaba los selectores de búsqueda (Scraping de DOM estándar iterativo) y mutaba aleatoriamente los códigos de red. Esto provocaba que se descargaran videos incorrectos o que el script colapsara eternamente. La instrucción regular `page.query_selector("video")` se consideró inestable y caduca para producción industrial.

### La Solución de 3 Capas (Defensa de Oro de Claude)
Se inyectó un diseño táctico ciber-robusto de 3 pasos infalibles para extraer los renders generativos sin fallo estructural:
1. **Línea Base del DOM (Conteo Visual Predictivo):** `_contar_videos_dom()`1. **El Motor Central (Orquestador)** corre un pipeline en lote (`forja masiva`)
2. **Control de Interrupción:** Si apagas el bot repentinamente, no quemamos créditos LLM ni perdemos videos, el gestor de colas nativo reconstruirá el JSON desde disco.

---

## 8. INTEGRACIÓN EN LA NUBE (Replicate API) - ALTERNATIVA ANTI-BLOQUEO
Ante instancias extremas donde los crawlers locales (Meta AI a través de Playwright) sufren bloqueos permanentes de IP o cuenta, el **Búnker** incluye una interfaz directa asíncrona hacia GPUs alquiladas por segundo mediante Replicate.

### Modelos de Video Ultra-Económicos Configurados:
1. **Minimax (`minimax/video-01`)**: El modelo tope de gama en realismo cinemático asiático. ~$0.04 USD por compilación de video. Altísima fidelidad al prompt.
2. **Lightricks (`lightricks/ltx-video`)**: Velocidad absurda y código abierto. Cuesta fracciones de centavo (~$0.003 USD/video).
3. **THUDM (`thudm/cogvideox-5b`)**: Desarrollo de la U. de Tsinghua. Es Open Source y se caracteriza por movimientos artísticos de Text-to-Video de bajísimo coste.

### Pruebas de Sistema (Test Script):
Se forjó un eslabón aislado `test_replicate.py` en la raíz del proyecto.
- Ejecutable libre de menús mediante `python test_replicate.py`.
- **Interactivo:** Interroga al comandante en terminal sobre qué modelo numérico (1/2/3) desea despertar (Minimax, LTX, o CogVideoX).
- **Inyección Dócil:** Jala automáticamente el `REPLICATE_API_TOKEN` encriptado en el archivo `.env`, envía la orden de render (Text-to-Video) a la nube y transfiere el mp4 resuelto `prueba_<modelo>.mp4` al disco C local sin intervención manual. Su propósito es probar fluidez y saldos en la nube antes de implementarlos al bucle forja de Playwright.

---hat. El bot queda en un `while` loop de espera continua hasta que el conteo en tiempo real logre una suma mayor al conteo anterior ("Línea Base"). Así garantizamos que lo que se evalúa es el render actual solicitado, y escapamos de clips viejos subidos en el historial del chat.
2. **Descarga Nativa de Playwright (Via Inyección de Clic Transparente):** `_descargar_via_click()`. Emplear la librería Python de origen `requests.get()` generaba "Fallos HTTP 403 Forbidden" por problemas de sesión y rechazo de cookies desautorizadas. La solución fue ubicar el atributo de texto "Download" en la página, emitir un `boton.click()` directo sobre el Frontend inyectado desde Playwright y llamar al suceso reactivo en segundo plano `expect_download()`. La sesión asimila internamente los binarios evadiendo rastreadores con la navegación genuina intacta.
3. **Fallback de Red (Respaldo en Tiempo de Ejecución):** Como red de seguridad terciaria, si el botón de descarga colapsa o es removido temporalmente por el servidor local de Meta, extraemos con inyección de JS la ruta base en crudo del atributo `src="..."` de la etiqueta final observada de video y pasamos a forzar intercepciones bajo un catálogo local de descarte de redundancia que bloquea URL repetidas (`urls_ignoradas`).

### Auto-Corrección y Fuerza Bruta en Meta AI (Protocolos de Reintento Agresivo)
**Petición del Soberano:** "Si al finalizar no puede volver a enviar el clip que faltó y reenviarlo de nuevo para completar la creación de los videos de la carpeta... Meta bloquea el clic de descarga."
**Soluciones Implementadas:**
1. **Forced Click (Rompe-Escudos Visuales):** Meta AI superpone ventanas invisibles en la UI generando el error analítico `intercepts pointer events` que provoca un *Timeout*. Se empleó un comando agresivo nativo en Playwright: `boton.click(force=True)`. Esto fuerza virtualmente la interacción del DOM atravesando cualquier div o modal protector que Meta coloque temporalmente.
2. **Bucle de Tolerancia Cero al Fallo (Retry System Automático):** A nivel algorítmico global (bucle `procesar_short()`), se recubrió la instanciación de cada clip en un iterador aislado de control de fallos: `for intento in range(MAX_REINTENTOS)`. Antes, si se agotaba el Timeout, el clip se perdía. Ahora el algoritmo detecta la ausencia de generación natural, loguea la alerta `Auto-Corrección`, limpia la caché inestable refrescando forzosamente la página con `.reload()`, e inyecta la automatización repetidamente hasta que el video existe, garantizando en un `$100\%$` tasas de Shorts llenos sin importar fluctuaciones en la red de Meta.

### Antibaneo de Nivel Militar y Rotación de Bases
**Variables Analíticas:** `CLIPS_POR_CUENTA = 4`.
Al intentar y sobreprocesar solicitudes iterativas sin detenerse en la misma conexión, Meta AI interfiere dictando "rate-limits temporales" o Soft Bans encubiertos. Se fabricó una directiva global controlada en la clase principal `MotionForgePlaywright` bajo un gestor de instancias indexadas. Este motor escanea implícitamente todo tu directorio al inicio buscando los archivos JSON extraídos con `auth_forge.py`. En la presencia de metadatos `meta_state_1.json`, `meta_state_2.json`, el contador se activará. El núcleo ciclará hacia un nuevo perfil de Facebook estéril luego de iterar su cuarta (`4`) respuesta satisfactoria asestando un hard-reset con una cuenta totalmente distinta para evadir banderas rojas operacionales de las cookies activas.

---

## 3. NÚCLEO DE ENSAMBLAJE CINEMATOGRÁFICO Y MOTORES DE TRANSICIÓN
**Archivo de Producción:** `motion_forge/short_assembler.py`

### Algoritmo de Flujo Dinámico (Circular Chain Engine)
Dado que debemos unificar archivos `.mp4` de Meta AI dispersos entre duraciones de `1.5s - 5s` contra la longitud cruda de una pista en audio generada (`duracion_total`), el `short_assembler` aplica un diseño de anillo repetitivo (Ciclo sobre la lista base).
A cada fracción anexada a tu `clips_procesados` se le obliga un **Pan & Scan adaptativo**: 
1. Los recursos visuales son redimensionables proporcionalmente preservando el ratio base del archivo usando como techo un crop escalado `max(OUTPUT_SIZE)`.
2. Una directiva activa de efecto en base `vfx.ZoomIn` desplaza sutil e ininterrumpidamente el centro del visual desde una escala `1.0` hasta `1.08`. El cruce de los metrajes inyecta un Alpha progresivo simulando disolución óptica (`FadeIn`), borrando cortes ásperos.

### Hooks de Base, Integraciones y Efectos Visuales Implementados
Aparte de colorear silábicamente ("*Hormozi Style*") los textos transcritos individualmente por Faster-Whisper, las inclusiones maestras dictadas al sistema fueron:
1. **Jerarquía Absoluta y Asimilación de Rutas (Hook Inteligente):** El ensamblador automatizado establece un túnel a tu clase matriz en core: `Database()`. Empleando un cruce bidireccional local, captura el ID único que procesas (`MASIVA_XXXX`). Realiza un escaneo directo de la API de *Google Sheets* e inyecta las celdas directas del `TITULO_GOLPE` y del `TITULO`. El código compulsa el texto, le adhiere saneamiento riguroso UTF (`re.sub(/[\\/*?:"<>|]/)`) y consolida la subcarpeta y final `output_folder`: Resultando en un mapeo de datos exacto: *Ejemplo: `output/shorts_finales/MASIVA_BIZANCIO_202610_4/LA PAZ MENTAL ES UN SISTEMA.mp4`*.
2. **Marca de Agua Hipnótica Cinetética (Efecto de Rebote Anton):** Definimos una imposición subliminal orientada al hemisferio superior del video. Para persuadir el CTA se implantó estáticamente el rótulo "SUSCRÍBETE".
   - *Estética de Impacto:* Letra molde `Anton`, color `#FF0000` (Rojo Base absoluto), opacidad contorneada, y sombras duras.
   - *Física Vectorial Aplicada:* En base temporal inyectando sobre la lista local `set_position()`, procesamos una variable dependiente `rebote_y(t) = base_y - abs(math.sin(t * 5)) * 20`. Esta función genera un recorrido ascendente constante y un freno parabólico amortiguado (rebote superior que vuelve a apoyarse en su inicio inferior puro sin salir del contorno estatuido del `15%` de la pantalla).
3. **Outro Cinemático Universal (Ruptura del viejo CTA / Inyección Final.mp4):** Entendiendo que los finales autogenerados estandarizaban la rutina y mermaban impacto ocular, el CTA de MovieLite originario se suprimió en presencia del argumento `--outro`. Se ha desarrollado una superposición transversal en las vías del *Writer* insertando a perpetuidad la lógica que extrae por metadatos `Final.mp4` (`D:\\YT\\MiuraForge\\forja_local\\Final.mp4`). El núcleo captura la longitud en segundos orgánicos del Outro y posiciona matemáticamente su marca de inicio visual en `(audio.duration - outro.duration)`. Forzando así, sin desfases asincrónicos, un colapso maestro de fotogramas donde el cierre del último silencio dictado por la locución se empalma asombrosa e incondicionalmente en paralelo con la desintegración pura de `Final.mp4` (El fin vocal abraza al fin metraje). La sincronía ahora pertenece netamente al material audiovisual precargado.

### Corrección Estructural de Control (Context Binding y Colas)
1. **Binding de Contexto del Navegador (Fix de Rotación):** Originalmente, la rotación de cuentas se invocaba localmente por clip dentro de `procesar_short()`. El error lógico subyacía en que Playwright **ya tenía cargado en memoria** el contexto de cookies inicial (`BrowserContext`), inutilizando el cambio de JSON. Se modificó el diseño desplazando `_rotar_cuenta_si_necesario()` al escalafón global de `procesar_cola()` para que rote perimetral y legítimamente los perfiles basándose en recuento por lote (`len(clips)`), lo que fuerza una carga física verídica de la nueva configuración antes del siguiente ciclo de `new_context()`.
2. **Purgado Tóxico de Cola (Phantom State Bug):** Detectamos que el manejador disparataba por doquier un estado de `procesando` huérfano. Explicación técnica: el loop finalizaba solicitando precipitadamente `siguiente = obtener_siguiente()` sin consumirlo en ese tick. Se erradicó este comando y se delegó la evaluación final de espera asincrónica a una monitorización pasiva `estado_cola()["pendientes"] > 0`, devolviendo limpieza matemática al `while True` nativo de cola en el Backend.

### Corrección Híbrida de Doblaje (Soporte MP3/WAV y Rutas Globales)
* **Desacople de Rastreo Estricto:** Inicialmente, el ensamblador esperaba rutas absolutas formadas con lógica en subcarpetas (`output\imagenes_shorts\ID_SESION\ID_SESION.wav`). Se descubrió que varios recursos de voz eran volcados masivamente al *root folder* originario. El sistema ahora aplica un trazado avanzado (`list.glob(f"*{fid}*.mp3")`) que analiza la identificación intrínseca en el nombre del archivo rastreando en `output/sesion_X`, `forja_local` y la raíz central de `imagenes_shorts`.
* **Compatibilidad Universal:** Se reescribió en Python la capacidad paramétrica nativa de MovieLite/MoviePy para tragar formatos `.mp3` indistintamente desde el rastreo base del oráculo. Ahora, frente a recursos carentes de WAV, `short_assembler` importa locuciones de codificación MPEG layer 3 nativamente.

### Inyección de N-Cuentas en Meta AI (Sistema Multi-Rotacional)
El motor de **Motion Forge (Opción 7)** ya cuenta con la arquitectura de Auto-Rotación (`_rotar_cuenta_si_necesario`). Su lógica nativa absorbe todos los perfiles que sigan la nomenclatura `meta_state_X.json` en la raíz de tu proyecto, y rotará de cuenta con cada Short nuevo que comience a animar.
**Pasos para Inyectar Cuentas:**
1. Abre tu terminal en `D:\YT\MiuraForge`
2. Ejecuta el enlazador dictando el número de cuenta: `python motion_forge/auth_forge.py --output meta_state_1.json` (Puedes usar el 1, 2, 3... hasta el 9).
3. Se abrirá una ventana de incógnito. Inicia sesión en Meta AI con el correo nuevo.
4. Vuelve al terminal oscuro y presiona **[ENTER]**.
5. ¡Listo! Al arrancar la **Opción 7**, el terminal te dirá: *"Cuentas disponibles: 2"*, y rotará automáticamente de perfil para salvaguardar tu hardware y burlar todo bloqueo.

9. **Integración en Forja Total (Opción 10):** Se ha unificado el motor de animación dentro del flujo maestro de `main.py`. Al ejecutar la **Forja Total**, el sistema ahora transiciona automáticamente de la generación de imágenes a la animación de video en Meta AI antes de generar el SEO.

---

## 5. NÚCLEO DE PUBLICACIÓN AUTOMÁTICA (YouTube Publisher)
**Archivos de Producción:** `youtube_publisher/auth_youtube.py` y `youtube_publisher.py`

### 5.1 Protocolo de Autenticación (`auth_youtube.py`)
Utiliza un sistema de **Captura de Sesión** para evadir bloqueos de seguridad de Google:
- Se ejecuta una única vez para generar `youtube_state.json`.
- Permite que el bot navegue por YouTube Studio con la identidad del Soberano ya validada.

### 5.2 Motor de Subida Automática (`youtube_publisher.py`)
Encargado del despliegue masivo controlado:
1. **Filtro de Estado:** Solo procesa videos marcados como `PENDIENTE` en la tabla `DESPLIEGUE`.
2. **Límite Operativo:** Configurado por defecto a **10 videos por sesión** para proteger la salud del canal.
3. **Optimización de Metadatos:** Une Título, Descripción y Hashtags dinámicamente.
4. **Modo Borrador:** Sube los videos como **Privados/Borradores** para revisión final obligatoria.
5. **Ciclo de Vida del Archivo:** Tras la subida exitosa, el MP4 se mueve a la carpeta `Ya Publicado` y el Sheet se actualiza a estado `BORRADOR`.
6. **Integración Maestro:** Ejecutable desde la **Opción 11** del Menú Central.

---

## 6. METODOLOGÍA DEL ESPEJO BÚNKER (Reglas de Forja de Sistema)
**Acertijo de Operación en el Backend:** "Para proteger la línea productiva del motor principal, todo ataque logístico a los generadores principales pasa por un escudo espejo."

Cualquier prueba esporádica (Estrategias de texto, marcas de agua, colisiones vectoriales generadas, experimentaciones de video Outro) jamás se editarán en caliente dentro del archivo principal.
- Se crea implícitamente un clon inmaculado asilado con el apelativo `_test.py`.
- Se realizan los ensayos iterativos con rendimientos limitados (1 video de muestra por carpeta).
- Apenas el "Output Visual" (MP4 en crudo) supera las estrictas métricas de excelencia expuestas por el Soberano; se desintegra la variante temporal y se fusiona limpiamente de regreso a la línea fundamental de automatización superior en `main.py` y archivos raíz, certificando CERO regresiones en la programación final.
