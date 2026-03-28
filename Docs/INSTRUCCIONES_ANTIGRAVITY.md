# ⚔️ Blog Engine MF-003 — Instrucciones de Implementación para Antigravity

## Contexto del proyecto

**Proyecto:** Disciplina en Acero — canal de YouTube Shorts + blog de reseñas  
**Propietario:** Andrés (Soberano)  
**Engine:** MiuraForgeEngine — Python en `D:\YT\MiuraForge\`  
**Sitio web:** disciplinaenacero.com — alojado en Netlify  
**Base de datos:** Google Sheets (ya conectada via `core/database.py`)  

---

## ¿Qué construimos?

Un sistema automatizado de publicación de blog:

```
Google Sheets → forge_blog.py → archivos .md → Astro → Netlify
```

1. El Soberano escribe ideas en la pestaña `BLOG_CONTENIDO` del Sheet
2. Cambia el Estado a `LISTO_PARA_FORJAR`
3. Corre `python forge_blog.py` 
4. El script transforma el texto con el Alchemist y genera los `.md`
5. Netlify reconstruye el sitio automáticamente

---

## Archivos que se entregan en este paquete

| Archivo | Destino en el proyecto | Descripción |
|---------|----------------------|-------------|
| `forge_blog.py` | `D:\YT\MiuraForge\tools\forge_blog.py` | Script principal — NÚCLEO |
| `astro.config.mjs` | `disciplinaenacero.com/astro.config.mjs` | Config Astro + Netlify CDN |
| `content.config.ts` | `disciplinaenacero.com/src/content.config.ts` | Schema Zod |
| `BlogPostLayout.astro` | `disciplinaenacero.com/src/layouts/BlogPostLayout.astro` | Layout de reseñas |
| `[slug].astro` | `disciplinaenacero.com/src/pages/blog/[slug].astro` | Ruta dinámica |
| `blog.astro` | `disciplinaenacero.com/src/pages/blog.astro` | Listado de reseñas |
| `ResenaCard.astro` | `disciplinaenacero.com/src/components/ResenaCard.astro` | Tarjeta de reseña |
| `ejemplo_habitos_atomicos.md` | `disciplinaenacero.com/src/content/blog/` | Ejemplo de output |

---

## Pasos de implementación (en orden)

### Paso 1 — Crear la hoja de Google Sheets

Crear una nueva hoja llamada **`Miura_Blog_Content`** en el mismo Google Drive del proyecto.

Crear la pestaña **`BLOG_CONTENIDO`** con estas columnas exactas (en este orden):

| Col | Nombre exacto | Tipo |
|-----|--------------|------|
| A | `A: ID` | Número autoincremental |
| B | `B: Estado` | `BORRADOR` / `LISTO_PARA_FORJAR` / `PUBLICADO` |
| C | `C: Título` | Texto |
| D | `D: Slug` | Texto (url-amigable) |
| E | `E: Fecha` | Texto YYYY-MM-DD |
| F | `F: Descripción (meta)` | Texto 150-160 chars |
| G | `G: Keywords` | Texto separado por comas |
| H | `H: Categoría` | Texto |
| I | `I: Imagen_URL` | URL |
| J | `J: Enlace_Afiliado_Amazon` | URL |
| K | `K: Cuerpo_Raw` | Texto largo (el borrador) |
| L | `L: Tags` | Texto separado por comas |
| M | `M: ReadTime_Min` | Número |
| N | `N: Featured` | `TRUE` / `FALSE` |

---

### Paso 2 — Instalar dependencias Python

```bash
pip install python-frontmatter
```

Las demás dependencias (`gspread`, `requests`, `python-dotenv`) ya están en el engine.

---

### Paso 3 — Agregar variable de entorno

En `.env` de MiuraForgeEngine añadir:

```env
# ── BLOG ENGINE ──────────────────────────────────────────────────────────────
NETLIFY_BUILD_HOOK=https://api.netlify.com/build_hooks/TU_ID_AQUI
```

El Build Hook se obtiene en:  
`Netlify Dashboard → [sitio] → Site Configuration → Build & Deploy → Build Hooks`  
→ Crear hook con nombre "MiuraForge Blog Engine"

---

### Paso 4 — Instalar Astro en el sitio

En la carpeta de `disciplinaenacero.com`:

```bash
# Si el sitio aún no tiene Astro:
npm create astro@latest . -- --template blog

# Agregar el adapter de Netlify:
npx astro add netlify

# Instalar Tailwind CSS (para los estilos de los layouts):
npx astro add tailwind
```

---

### Paso 5 — Copiar los archivos del paquete

Siguiendo la tabla de destinos del apartado anterior.

Crear las carpetas si no existen:
- `src/content/blog/` — aquí van los `.md` generados por Python
- `src/layouts/`
- `src/pages/blog/`
- `src/components/`

---

### Paso 6 — Configurar Netlify

En el dashboard de Netlify:
- **Build command:** `astro build`
- **Publish directory:** `dist`

Netlify detecta Astro automáticamente y puede sugerir estos valores.

---

### Paso 7 — Prueba completa

```bash
# Desde D:\YT\MiuraForge\:

# 1. Primero en modo dry-run para verificar sin escribir nada:
python tools\forge_blog.py --dry-run

# 2. Si todo está bien, procesar el primer artículo real:
python tools\forge_blog.py --id 1

# 3. Verificar que el .md se generó en:
# disciplinaenacero.com/src/content/blog/

# 4. Probar el build local de Astro:
cd disciplinaenacero.com
npm run build
npm run preview
```

---

## Notas técnicas importantes

### Sobre el Alchemist

`forge_blog.py` llama al Alchemist via `LLMFactory.get_brain("alchemist")` — el mismo que usa el pipeline de guiones. Si no está configurado como cerebro "alchemist", puede usar el brain "visual" o "default" del engine. Verificar la configuración en `core/llm/factory.py`.

### Sobre las rutas de archivos

`BLOG_OUTPUT_DIR` en `forge_blog.py` apunta a:
```
D:\YT\MiuraForge\disciplinaenacero.com\src\content\blog\
```

Si el repositorio del sitio está en otra ubicación, actualizar esta línea:
```python
BLOG_OUTPUT_DIR = BASE_DIR / "disciplinaenacero.com" / "src" / "content" / "blog"
```

O mejor: agregar al `.env`:
```env
BLOG_OUTPUT_DIR=D:\ruta\al\sitio\src\content\blog
```

Y en `forge_blog.py` leer desde el entorno.

### Sobre los nombres de columnas del Sheet

Los headers del Sheet deben coincidir **exactamente** con los valores del diccionario `COL` en `forge_blog.py`. Si los headers tienen espacios extra o caracteres distintos, el script fallará silenciosamente. Verificar con:

```python
from core.database import Database
db = Database()
hoja = db.spreadsheet.worksheet("BLOG_CONTENIDO")
print(hoja.row_values(1))  # debe imprimir los headers exactos
```

---

## Módulos futuros (no implementar ahora)

- **Audio-resumen:** Supertonic/MiniMax genera un audio del resumen del artículo embebido en el post
- **Newsletter automático:** Emissary envía email a la lista cuando se publica un artículo (Brevo API ya integrada)
- **Pixel de Facebook + GA4:** Scripts en `BaseLayout.astro` via variables de entorno de Netlify
- **Interlinking automático:** El script detecta menciones de otros artículos del blog y agrega links

---

## Estado actual del proyecto

| Componente | Estado |
|-----------|--------|
| `forge_blog.py` | ✅ Listo para implementar |
| Astro layouts/pages | ✅ Listos para copiar |
| Hoja Sheets BLOG_CONTENIDO | ⏳ Crear manualmente |
| Build Hook Netlify | ⏳ Configurar en dashboard |
| Astro instalado en el sitio | ⏳ Verificar / instalar |
| Primera prueba end-to-end | ⏳ Pendiente |
