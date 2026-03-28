# ⚔️ MIURA FORGE ENGINE

## Módulo de Doctrina Digital

### Blog Engine --- PRD Completo para Agentes

**ID:** MF-003-Astro\
**Estado:** LISTO PARA FORJAR\
**Versión:** 1.0\
**Fecha:** Marzo 2026

------------------------------------------------------------------------

# 1. CONTEXTO GLOBAL --- MIURA FORGE ENGINE

Este documento forma parte del ecosistema **Miura Forge Engine**, un
sistema avanzado de IA para la creación automatizada de contenido de
alto impacto bajo la doctrina **Disciplina en Acero**.

El módulo **Blog Engine (MF-003)** es un nuevo componente que se integra
al pipeline existente, añadiendo un canal de contenido escrito
(**reseñas de libros**) para el dominio:

    disciplinaenacero.com

------------------------------------------------------------------------

# 1.1 Doctrina del Motor (reglas inquebrantables)

-   No humilla, no consuela, no dramatiza.
-   Revela, Diagnostica y Ordena.
-   Ataca el autoengaño del hombre para reconstruir su responsabilidad
    mediante acciones físicas concretas.

**Tono:**\
Andrés --- autoridad calmada, prensa hidráulica, inyección de carbono.

------------------------------------------------------------------------

# 1.2 Stack Tecnológico del Ecosistema

  Componente        Tecnología / Herramienta
  ----------------- ---------------------------------------------
  LLM Principal     Google Gemini 2.0 Pro (rotación de 10 keys)
  LLM Alternativo   NVIDIA DeepSeek
  Base de Datos     Google Sheets
  Imágenes          NVIDIA → Nebius → Replicate
  Voz               ElevenLabs
  Automatización    Python 3.10+, Playwright, FFMPEG
  Blog              Astro + Netlify + Google Sheets

------------------------------------------------------------------------

# 2. VISIÓN DEL MÓDULO BLOG (MF-003)

Sistema **100% automatizado**:

    Google Sheets → Python (MiuraForge) → Astro → Netlify

Resultado:

-   Sitio estático ultra rápido
-   SEO optimizado
-   Pipeline automático de publicación

------------------------------------------------------------------------

# 2.1 Ventajas de Astro para este módulo

-   **Content Collections** --- Astro lee automáticamente todos los
    `.md`.
-   **Zero JS por defecto** --- PageSpeed 95--100 garantizado.
-   **Netlify Image CDN + `<Image />`** --- optimización de imágenes.
-   **Extensible** --- audio player, leads, afiliados.

------------------------------------------------------------------------

# 2.2 Flujo General del Módulo

El proceso completo tiene **4 etapas**.

## Etapa 1 --- Escritura

El Soberano (Andrés) escribe en Google Sheets:

    BLOG_CONTENIDO

Estado:

    LISTO_PARA_FORJAR

------------------------------------------------------------------------

## Etapa 2 --- Alquimia

El script:

    forge_blog.py

-   Detecta filas listas
-   Extrae `Cuerpo_Raw`
-   Llama al **Alchemist (LLM)**

Resultado:

    Reseña de Acero

------------------------------------------------------------------------

## Etapa 3 --- Generación

Python genera archivos:

    .md

En:

    src/content/blog/

------------------------------------------------------------------------

## Etapa 4 --- Publicación

Se llama al **Build Hook de Netlify**

Resultado:

    Astro compila
    Netlify publica

Estado en Sheets:

    PUBLICADO

------------------------------------------------------------------------

# 3. GOOGLE SHEETS --- HOJA BLOG_CONTENIDO

Crear Spreadsheet:

    Miura_Blog_Content

Hoja principal:

    BLOG_CONTENIDO

------------------------------------------------------------------------

# 3.1 Estructura de Columnas (14)

  Col   Nombre                   Tipo          Descripción
  ----- ------------------------ ------------- --------------------------------------------
  A     ID                       Auto          Generado por Sheets
  B     Estado                   Enum          BORRADOR / LISTO_PARA_FORJAR / PUBLICADO
  C     Título                   Texto         Ej: Por qué Hábitos Atómicos no te salvará
  D     Slug                     Texto         URL amigable
  E     Fecha                    Fecha         YYYY-MM-DD
  F     Descripción (meta)       Texto         150--160 chars SEO
  G     Keywords                 CSV           disciplina-en-acero,habitos
  H     Categoría                Texto         Reseñas / Estoicismo
  I     Imagen_URL               URL           imagen portada
  J     Enlace_Afiliado_Amazon   URL           afiliado
  K     Cuerpo_Raw               Texto largo   borrador
  L     Tags                     CSV           hábitos,identidad
  M     ReadTime_Min             Número        tiempo lectura
  N     Featured                 Boolean       portada

------------------------------------------------------------------------

# 3.2 Estados del Ciclo de Vida

### BORRADOR

El Soberano escribe. Script **ignora**.

### LISTO_PARA_FORJAR

El script `forge_blog.py` procesa el contenido.

### PUBLICADO

-   Markdown generado
-   Netlify compiló
-   Sitio en vivo

------------------------------------------------------------------------

# 4. ARQUITECTURA DEL PROYECTO ASTRO

## 4.1 Inicialización

``` bash
npm create astro@latest . -- --template blog
npx astro add netlify
```

------------------------------------------------------------------------

# 4.2 Estructura de Directorios

    disciplinaenacero.com/

    src/
     ├─ content/
     │   └─ blog/
     ├─ content.config.ts
     ├─ layouts/
     │   └─ BlogPostLayout.astro
     ├─ pages/
     │   ├─ blog/
     │   │   └─ [slug].astro
     │   ├─ index.astro
     │   └─ blog.astro
     └─ components/
         ├─ ResenaCard.astro
         └─ CTA_Acero.astro

    astro.config.mjs
    netlify.toml
    package.json
    public/

------------------------------------------------------------------------

# Cierre doctrinal

> **"El acero no se oxida con orgullo; se templa con trabajo
> implacable."**

**MiuraForge Engine --- Doctrina Digital**
