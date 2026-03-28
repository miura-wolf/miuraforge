# ⚔️ BLOG ENGINE - Plan de Trabajo Estructurado

> Implementación del módulo Blog Engine (MF-003) para disciplinaenacero.com  
> **ID:** BLOG-001  
> **Estado:** LISTO_PARA_FORJAR  
> **Fecha:** Marzo 2026

---

## 📋 RESUMEN EJECUTIVO

**Objetivo:** Migrar disciplinaenacero.com a Astro + implementar sistema de blog automatizado para reseñas de libros.

**Flujo:** Google Sheets → Python (MiuraForge) → Astro → Netlify

**Stack:** Astro + Netlify + Google Sheets + Python

---

## 🎯 FASES DEL PROYECTO

### FASE 1: Infraestructura Gentleman AI (PRE-REQUISITO)
**Estado:** ⏳ PENDIENTE  
**Prioridad:** ALTA

**Tareas:**
- [ ] Instalar Gentleman AI (Windows PowerShell)
- [ ] Configurar con Engram + SDD
- [ ] Seleccionar agente (Claude Code u OpenCode)
- [ ] Verificar integración con proyecto

**Comandos:**
```powershell
# Instalar
irm https://raw.githubusercontent.com/Gentleman-Programming/gentle-ai/main/scripts/install.ps1 | iex

# Iniciar
gentle-ai
```

**Entregable:** Gentleman AI funcionando como coequipero

---

### FASE 2: Preparación del Proyecto Astro
**Estado:** ⏳ PENDIENTE  
**Prioridad:** ALTA

**Tareas:**
- [ ] Inicializar proyecto Astro con template blog
- [ ] Configurar integración Netlify
- [ ] Migrar contenido HTML existente a Astro
- [ ] Crear estructura de directorios

**Comandos:**
```bash
# Crear proyecto Astro
npm create astro@latest disciplinaenacero-astro -- --template blog

# Agregar Netlify
cd disciplinaenacero-astro
npx astro add netlify
```

**Estructura objetivo:**
```
disciplinaenacero-astro/
├── src/
│   ├── content/
│   │   └── blog/          ← Posts generados
│   ├── layouts/
│   │   └── BlogPost.astro
│   ├── pages/
│   │   ├── blog/
│   │   │   └── [slug].astro
│   │   ├── index.astro
│   │   └── blog.astro
│   └── components/
│       ├── ResenaCard.astro
│       └── CTA_Acero.astro
├── public/
├── astro.config.mjs
├── netlify.toml
└── package.json
```

**Entregable:** Proyecto Astro base funcionando localmente

---

### FASE 3: Configuración Google Sheets
**Estado:** ⏳ PENDIENTE  
**Prioridad:** ALTA

**Tareas:**
- [ ] Crear spreadsheet "Miura_Blog_Content"
- [ ] Configurar hoja "BLOG_CONTENIDO" con 14 columnas
- [ ] Definir estados: BORRADOR / LISTO_PARA_FORJAR / PUBLICADO
- [ ] Agregar credenciales al sistema de config centralizado

**Estructura de columnas:**
| Col | Nombre | Tipo | Descripción |
|-----|--------|------|-------------|
| A | ID | Auto | ID único |
| B | Estado | Enum | BORRADOR / LISTO_PARA_FORJAR / PUBLICADO |
| C | Título | Texto | Título del post |
| D | Slug | Texto | URL amigable |
| E | Fecha | Fecha | YYYY-MM-DD |
| F | Descripción | Texto | Meta description (150-160 chars) |
| G | Keywords | CSV | disciplina-en-acero,habitos |
| H | Categoría | Texto | Reseñas / Estoicismo |
| I | Imagen_URL | URL | Imagen de portada |
| J | Enlace_Afiliado | URL | Link de Amazon |
| K | Cuerpo_Raw | Texto largo | Contenido en Markdown |
| L | Tags | CSV | hábitos,identidad |
| M | ReadTime_Min | Número | Tiempo de lectura |
| N | Featured | Boolean | Destacado en portada |

**Entregable:** Hoja configurada y accesible desde core/database.py

---

### FASE 4: Implementación del Módulo forge_blog.py
**Estado:** ⏳ PENDIENTE  
**Prioridad:** ALTA

**Tareas:**
- [ ] Crear archivo `core/forge_blog.py`
- [ ] Implementar clase `BlogForge`
- [ ] Método `detectar_posts_listos()` - leer filas LISTO_PARA_FORJAR
- [ ] Método `procesar_post()` - transformar con LLM (Alchemist)
- [ ] Método `generar_markdown()` - crear archivos .md
- [ ] Método `actualizar_estado()` - marcar como PUBLICADO
- [ ] Integrar con sistema de configuración centralizada

**Flujo del módulo:**
```python
class BlogForge:
    def __init__(self):
        self.db = Database()
        self.alchemist = Alchemist()
    
    def detectar_posts_listos(self):
        """Lee hoja BLOG_CONTENIDO y filtra Estado == 'LISTO_PARA_FORJAR'"""
    
    def procesar_post(self, post_data):
        """Llama a Alchemist para transformar Cuerpo_Raw en reseña de acero"""
    
    def generar_markdown(self, post_procesado):
        """Crea archivo .md en src/content/blog/"""
    
    def actualizar_estado(self, post_id, nuevo_estado):
        """Actualiza columna Estado en Sheets"""
```

**Prompt para Alchemist (Blog):**
```
Actúa como reseñista de libros bajo la doctrina "Disciplina en Acero".

DOCTRINA:
- No consueles, no humilles, no dramatizes
- Revela, diagnostica y ordena
- Ataca el autoengaño, no al hombre
- Tono: Andrés (autoridad calmada, prensa hidráulica)

INPUT:
- Libro: {titulo}
- Categoría: {categoria}
- Borrador: {cuerpo_raw}

OUTPUT:
- Reseña completa (800-1200 palabras)
- Estructura: Diagnóstico → Revelación → Acción
- CTA: Enlace afiliado + suscripción
- Formato: Markdown con frontmatter
```

**Entregable:** Módulo forge_blog.py funcional y testeado

---

### FASE 5: Creación de Componentes Astro
**Estado:** ⏳ PENDIENTE  
**Prioridad:** MEDIA

**Tareas:**
- [ ] Crear `src/layouts/BlogPost.astro`
- [ ] Crear `src/components/ResenaCard.astro`
- [ ] Crear `src/components/CTA_Acero.astro`
- [ ] Crear página índice `src/pages/blog.astro`
- [ ] Crear página dinámica `src/pages/blog/[slug].astro`
- [ ] Configurar Content Collections en `src/content.config.ts`

**Componentes requeridos:**

**BlogPost.astro (Layout):**
- Header con branding Disciplina en Acero
- Slot para contenido
- CTA de suscripción al final
- SEO optimizado (OpenGraph, Twitter cards)

**ResenaCard.astro:**
- Imagen de portada
- Título
- Extracto (160 chars)
- Tiempo de lectura
- Tags
- Link a post completo

**CTA_Acero.astro:**
- Mensaje de suscripción
- Input de email
- Botón "Unirme al Acero"
- Diseño industrial/metálico

**Entregable:** Componentes Astro creados y estilizados

---

### FASE 6: Configuración Netlify + Build Hook
**Estado:** ⏳ PENDIENTE  
**Prioridad:** MEDIA

**Tareas:**
- [ ] Configurar `netlify.toml`
- [ ] Generar Build Hook URL en Netlify
- [ ] Agregar URL a `.env` como `NETLIFY_BUILD_HOOK`
- [ ] Implementar trigger de build en forge_blog.py

**Configuración netlify.toml:**
```toml
[build]
  command = "npm run build"
  publish = "dist"

[build.environment]
  NODE_VERSION = "20"

[[redirects]]
  from = "/blog/*"
  to = "/blog/:splat"
  status = 200

[[headers]]
  for = "/images/*"
  [headers.values]
    Cache-Control = "public, max-age=31536000, immutable"
```

**Trigger de build (en forge_blog.py):**
```python
import requests

def trigger_netlify_build():
    build_hook = os.getenv('NETLIFY_BUILD_HOOK')
    response = requests.post(build_hook)
    return response.status_code == 200
```

**Entregable:** Build hook configurado y funcionando

---

### FASE 7: Testing y Validación
**Estado:** ⏳ PENDIENTE  
**Prioridad:** MEDIA

**Tareas:**
- [ ] Test unitarios para forge_blog.py
- [ ] Test de integración: Sheets → Markdown
- [ ] Test de build: Astro compila correctamente
- [ ] Test de deploy: Netlify publica sin errores
- [ ] Validar SEO: metadatos, OpenGraph, structured data

**Checklist de validación:**
- [ ] Posts se generan desde Sheets correctamente
- [ ] Markdown tiene frontmatter válido
- [ ] Imágenes se optimizan con Netlify Image CDN
- [ ] Slugs son únicos y SEO-friendly
- [ ] Links afiliados funcionan
- [ ] Responsive en móvil
- [ ] PageSpeed 95+ (Astro Zero-JS)

**Entregable:** Sistema testeado y validado

---

### FASE 8: Documentación y Archivo
**Estado:** ⏳ PENDIENTE  
**Prioridad:** BAJA

**Tareas:**
- [ ] Crear `Docs/BLOG_ENGINE_SETUP.md` - Guía completa
- [ ] Actualizar `SKILL_REGISTRY.md` con skills de blog
- [ ] Crear template para escritura de posts
- [ ] Documentar flujo de trabajo para el Soberano
- [ ] Guardar lecciones aprendidas en Engram

**Documentación requerida:**
1. Cómo escribir en Sheets
2. Cómo ejecutar forge_blog.py
3. Estructura de frontmatter
4. Troubleshooting común

**Entregable:** Documentación completa

---

## 📊 CRONOGRAMA ESTIMADO

| Fase | Duración | Dependencias |
|------|----------|--------------|
| Fase 1: Gentleman AI | 30 min | - |
| Fase 2: Astro base | 2-3 horas | Fase 1 |
| Fase 3: Sheets | 1 hora | Fase 2 |
| Fase 4: forge_blog.py | 3-4 horas | Fase 3 |
| Fase 5: Componentes Astro | 2-3 horas | Fase 4 |
| Fase 6: Netlify | 1 hora | Fase 5 |
| Fase 7: Testing | 2 horas | Fase 6 |
| Fase 8: Documentación | 1 hora | Fase 7 |

**Total estimado:** 12-16 horas de trabajo

---

## 🎯 PROXIMOS PASOS INMEDIATOS

1. **Instalar Gentleman AI** ← EMPEZAR AQUÍ
2. Crear proyecto Astro
3. Configurar hoja BLOG_CONTENIDO en Sheets
4. Implementar forge_blog.py
5. Crear componentes Astro
6. Deploy en Netlify

---

## 📁 ARCHIVOS RELACIONADOS

- `MiuraForge_BlogEngine_PRD.md` - Especificación completa
- `SESSION_MEMORY_20260325.md` - Contexto de sesión anterior
- `GENTLEMAN_AI_SETUP.md` - Guía de instalación Gentleman
- `core/config.py` - Sistema de configuración centralizada
- `core/database.py` - Conexión a Google Sheets

---

**Versión:** 1.0  
**Última actualización:** Marzo 2026  
**Autor:** Gran Visir  
**Estado:** LISTO_PARA_FORJAR
