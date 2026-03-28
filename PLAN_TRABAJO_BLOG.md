# ⚔️ PLAN DE TRABAJO: Blog Engine para disciplinaenacero.com

> **ID:** PLAN-BLOG-001  
> **Proyecto:** Miura Forge Engine - Módulo MF-003  
> **Estado:** LISTO_PARA_FORJAR  
> **Fecha:** Marzo 2026

---

## 📚 CONTEXTO Y DOCUMENTACIÓN EXISTENTE

Antes de empezar, estos documentos ya están creados y deben consultarse:

| Documento | Ubicación | Propósito |
|-----------|-----------|-----------|
| **SKILL_REGISTRY.md** | `skills/SKILL_REGISTRY.md` | 13 skills SDD para el pipeline de producción |
| **MIURA_WORKFLOW_SD.md** | `Docs/MIURA_WORKFLOW_SD.md` | Las 9 fases del workflow adaptadas de Gentleman AI |
| **Blog Engine PRD** | `MiuraForge_BlogEngine_PRD.md` | Especificación completa del módulo MF-003 |
| **Setup Gentleman AI** | `GENTLEMAN_AI_SETUP.md` | Guía de instalación del coequipero |
| **Memoria Sesión 25/03** | `SESSION_MEMORY_20260325.md` | Logros y pendientes de la sesión anterior |

---

## 🎯 DECISIONES ARQUITECTÓNICAS

### Decisión 1: Google Sheets
**Opción A:** Crear spreadsheet nuevo "Miura_Blog_Content"  
**Opción B:** Usar hoja existente de MiuraForge, agregar pestaña "BLOG_CONTENIDO"

**Decisión:** Opción B  
**Justificación:** Centralizar la gestión de contenido en un solo lugar. Ya tenemos credenciales configuradas, conexión establecida en `core/database.py`, y lógica de rotación de API keys. Agregar una pestaña es más simple que mantener dos spreadsheets.

### Decisión 2: Estructura del Proyecto
**Opción A:** Integrar blog en proyecto Astro existente  
**Opción B:** Crear proyecto Astro separado `disciplinaenacero-astro/`

**Decisión:** Opción B (inicialmente)  
**Justificación:** Permite desarrollo independiente sin afectar el sitio HTML actual que ya está funcionando. Una vez validado, podemos migrar todo el sitio a Astro.

---

## 📋 FASES DEL PROYECTO

### 🔧 FASE 1: Preparación del Entorno (Infraestructura)
**Duración:** 30 minutos  
**Dependencias:** Ninguna

**Objetivo:** Tener Gentleman AI como coequipero de desarrollo.

**Documentación base:** `GENTLEMAN_AI_SETUP.md`

**Tareas:**
1. [ ] Instalar Gentleman AI vía PowerShell
2. [ ] Configurar con Engram + SDD habilitados
3. [ ] Verificar que opencode/OpenCode tiene acceso a memoria
4. [ ] Guardar contexto de inicio de proyecto en Engram

**Comandos:**
```powershell
# Instalar (PowerShell como Administrador)
irm https://raw.githubusercontent.com/Gentleman-Programming/gentle-ai/main/scripts/install.ps1 | iex

# Iniciar
gentle-ai

# Configurar para MiuraForge
# - Engram: SÍ
# - SDD: SÍ  
# - Skills: Python, Astro
# - Agente: OpenCode
```

**Criterios de éxito:**
- [ ] Comando `gentle-ai` responde
- [ ] Memoria persistente activa
- [ ] OpenCode tiene contexto del proyecto

---

### 🚀 FASE 2: Inicialización del Proyecto Astro
**Duración:** 2-3 horas  
**Dependencias:** Fase 1 completada

**Objetivo:** Crear proyecto Astro base y migrar contenido HTML existente.

**Documentación base:** Blog Engine PRD (sección 4)

**Tareas:**
1. [ ] Crear proyecto con template blog
2. [ ] Instalar integración Netlify
3. [ ] Migrar `disciplinaenacero/index.html` a Astro
4. [ ] Migrar `disciplinaenacero/pages/*.html` a Astro
5. [ ] Migrar CSS y assets
6. [ ] Crear estructura de directorios final

**Comandos:**
```bash
# Crear proyecto
cd D:\YT\MiuraForge
npm create astro@latest disciplinaenacero-astro -- --template blog

# Instalar integración
cd disciplinaenacero-astro
npx astro add netlify

# Instalar dependencias adicionales
npm install @astrojs/tailwind
npx astro add tailwind
```

**Estructura final esperada:**
```
disciplinaenacero-astro/
├── src/
│   ├── content/
│   │   └── blog/              ← Posts generados por MiuraForge
│   ├── layouts/
│   │   ├── Layout.astro       ← Layout base
│   │   └── BlogPost.astro     ← Layout para posts
│   ├── pages/
│   │   ├── index.astro        ← Home (migrado de index.html)
│   │   ├── blog.astro         ← Índice de posts
│   │   ├── about.astro        ← Nosotros/Doctrina
│   │   └── blog/
│   │       └── [slug].astro    ← Página dinámica
│   ├── components/
│   │   ├── ResenaCard.astro
│   │   ├── CTA_Acero.astro
│   │   ├── Header.astro
│   │   └── Footer.astro
│   └── content.config.ts
├── public/
│   └── images/                ← Imágenes de portada
├── astro.config.mjs
├── netlify.toml
└── package.json
```

**Criterios de éxito:**
- [ ] `npm run dev` funciona sin errores
- [ ] Sitio accesible en `localhost:4321`
- [ ] Diseño consistente con sitio actual

---

### 📊 FASE 3: Configuración de Google Sheets
**Duración:** 1 hora  
**Dependencias:** Fase 2 completada

**Objetivo:** Crear pestaña BLOG_CONTENIDO en hoja existente con estructura de 14 columnas.

**Documentación base:** Blog Engine PRD (sección 3)

**Tareas:**
1. [ ] Abrir spreadsheet existente de MiuraForge
2. [ ] Crear nueva pestaña "BLOG_CONTENIDO"
3. [ ] Configurar 14 columnas según especificación
4. [ ] Crear fila de ejemplo para testing
5. [ ] Actualizar `core/database.py` si es necesario

**Estructura de columnas:**

| Col | Nombre | Tipo | Descripción | Ejemplo |
|-----|--------|------|-------------|---------|
| A | ID | Auto | Generado por Sheets | 1 |
| B | Estado | Enum | BORRADOR / LISTO_PARA_FORJAR / PUBLICADO | LISTO_PARA_FORJAR |
| C | Título | Texto | Título del post | Por qué Hábitos Atómicos no te salvará |
| D | Slug | Texto | URL amigable | habitos-atomicos-verdad |
| E | Fecha | Fecha | YYYY-MM-DD | 2026-03-26 |
| F | Descripción | Texto | Meta description (150-160 chars) | La reseña que James Clear no quiere que leas... |
| G | Keywords | CSV | Keywords SEO | disciplina-en-acero,habitos,libros |
| H | Categoría | Texto | Reseñas / Estoicismo | Reseñas |
| I | Imagen_URL | URL | Imagen de portada | https://... |
| J | Enlace_Afiliado | URL | Link Amazon afiliado | https://amzn.to/... |
| K | Cuerpo_Raw | Texto largo | Borrador en Markdown | # Hábitos Atómicos... |
| L | Tags | CSV | Tags del post | hábitos,productividad,cambio |
| M | ReadTime_Min | Número | Tiempo de lectura | 5 |
| N | Featured | Boolean | Destacado en home | TRUE |

**Estados del ciclo de vida:**
- **BORRADOR:** Andrés escribe, script ignora
- **LISTO_PARA_FORJAR:** Script procesa el contenido
- **PUBLICADO:** Contenido generado y publicado

**Criterios de éxito:**
- [ ] Hoja creada con headers correctos
- [ ] Fila de prueba con estado LISTO_PARA_FORJAR
- [ ] `core/database.py` puede leer la hoja

---

### ⚙️ FASE 4: Implementación de forge_blog.py
**Duración:** 3-4 horas  
**Dependencias:** Fase 3 completada

**Objetivo:** Crear módulo Python que procese contenido de Sheets y genere Markdown.

**Documentación base:** 
- Blog Engine PRD (sección 2.2)
- SKILL_REGISTRY.md (sdd-spec, sdd-implement)
- MIURA_WORKFLOW_SD.md (Fase 2-3)

**Tareas:**
1. [ ] Crear `core/forge_blog.py`
2. [ ] Implementar clase `BlogForge`
3. [ ] Integrar con `core/database.py` existente
4. [ ] Integrar con `core/alchemist.py` para transformar contenido
5. [ ] Implementar generación de frontmatter
6. [ ] Implementar trigger de build en Netlify
7. [ ] Crear script CLI `tools/forge_blog.py`

**Estructura del módulo:**

```python
# core/forge_blog.py

from core.database import Database
from core.alchemist import Alchemist
from core.config import Config
import os
import re
from datetime import datetime

class BlogForge:
    """
    Módulo de Blog Engine para MiuraForge.
    Convierte contenido de Google Sheets en posts de Astro.
    """
    
    def __init__(self):
        self.config = Config()
        self.db = Database()
        self.alchemist = Alchemist()
        self.output_dir = "../disciplinaenacero-astro/src/content/blog/"
    
    def detectar_posts_listos(self):
        """
        Lee hoja BLOG_CONTENIDO y retorna filas con Estado = 'LISTO_PARA_FORJAR'
        """
        hoja = self.db.get_sheet("BLOG_CONTENIDO")
        datos = hoja.get_all_records()
        return [fila for fila in datos if fila.get('Estado') == 'LISTO_PARA_FORJAR']
    
    def procesar_contenido(self, post_data):
        """
        Usa Alchemist para transformar Cuerpo_Raw en reseña de acero.
        """
        prompt = f"""
        Actúa como reseñista de libros bajo la doctrina "Disciplina en Acero".
        
        DOCTRINA:
        - No consueles, no humilles, no dramatizes
        - Revela, diagnostica y ordena  
        - Ataca el autoengaño, no al hombre
        - Tono: Andrés (autoridad calmada, prensa hidráulica, inyección de carbono)
        
        LIBRO A RESEÑAR: {post_data.get('Título')}
        CATEGORÍA: {post_data.get('Categoría')}
        
        BORRADOR DEL SOBERANO:
        {post_data.get('Cuerpo_Raw')}
        
        TRANSFORMA este borrador en una reseña de 800-1200 palabras con:
        - Diagnóstico quirúrgico del problema que el libro aborda
        - Revelación incómoda sobre por qué la mayoría fracasa
        - Acción concreta que el lector puede tomar HOY
        - CTA con enlace afiliado: {post_data.get('Enlace_Afiliado')}
        
        FORMATO: Markdown estructurado.
        """
        
        return self.alchemist.transform(prompt)
    
    def generar_frontmatter(self, post_data, contenido_procesado):
        """
        Genera frontmatter YAML para Astro.
        """
        return f"""---
title: "{post_data.get('Título')}"
description: "{post_data.get('Descripción')}"
pubDate: {post_data.get('Fecha')}
heroImage: "{post_data.get('Imagen_URL')}"
category: "{post_data.get('Categoría')}"
tags: [{post_data.get('Tags')}]
readTime: {post_data.get('ReadTime_Min')}
featured: {str(post_data.get('Featured', False)).lower()}
amazonLink: "{post_data.get('Enlace_Afiliado')}"
---

{contenido_procesado}
"""
    
    def generar_markdown(self, post_data, contenido_procesado):
        """
        Crea archivo .md en src/content/blog/
        """
        slug = post_data.get('Slug') or self.generar_slug(post_data.get('Título'))
        filename = f"{slug}.md"
        filepath = os.path.join(self.output_dir, filename)
        
        frontmatter = self.generar_frontmatter(post_data, contenido_procesado)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(frontmatter)
        
        return filepath
    
    def generar_slug(self, titulo):
        """Genera slug URL-friendly"""
        slug = re.sub(r'[^\w\s-]', '', titulo.lower())
        slug = re.sub(r'[-\s]+', '-', slug)
        return slug[:50]
    
    def actualizar_estado(self, post_id, nuevo_estado):
        """
        Actualiza columna Estado en Sheets.
        """
        hoja = self.db.get_sheet("BLOG_CONTENIDO")
        # Lógica para actualizar fila específica
        
    def trigger_build(self):
        """
        Llama al build hook de Netlify.
        """
        import requests
        build_hook = os.getenv('NETLIFY_BUILD_HOOK')
        if build_hook:
            response = requests.post(build_hook)
            return response.status_code == 200
        return False
    
    def ejecutar(self):
        """
        Flujo completo del Blog Engine.
        """
        posts_listos = self.detectar_posts_listos()
        
        for post in posts_listos:
            # Procesar con Alchemist
            contenido = self.procesar_contenido(post)
            
            # Generar Markdown
            filepath = self.generar_markdown(post, contenido)
            print(f"✅ Post generado: {filepath}")
            
            # Actualizar estado
            self.actualizar_estado(post.get('ID'), 'PUBLICADO')
        
        # Trigger build si hay cambios
        if posts_listos:
            if self.trigger_build():
                print("🚀 Build de Netlify disparado")
            else:
                print("⚠️ No se pudo disparar el build")

# tools/forge_blog.py
from core.forge_blog import BlogForge

def main():
    forge = BlogForge()
    forge.ejecutar()

if __name__ == "__main__":
    main()
```

**Prompt para Alchemist (Blog):**

Según SKILL_REGISTRY.md (sdd-spec), adaptar el template de guion MASTER para posts de blog.

**Criterios de éxito:**
- [ ] `python tools/forge_blog.py` ejecuta sin errores
- [ ] Detecta filas LISTO_PARA_FORJAR
- [ ] Genera archivos .md con frontmatter válido
- [ ] Actualiza estado a PUBLICADO
- [ ] Trigger de Netlify funciona

---

### 🎨 FASE 5: Componentes Astro
**Duración:** 2-3 horas  
**Dependencias:** Fase 4 completada

**Objetivo:** Crear layouts y componentes para mostrar posts.

**Documentación base:**
- Blog Engine PRD (sección 4.2)
- Astro Content Collections docs

**Tareas:**
1. [ ] Crear `src/content.config.ts` para Content Collections
2. [ ] Crear `src/layouts/BlogPost.astro`
3. [ ] Crear `src/components/ResenaCard.astro`
4. [ ] Crear `src/components/CTA_Acero.astro`
5. [ ] Crear `src/pages/blog.astro` (índice)
6. [ ] Crear `src/pages/blog/[slug].astro` (dinámica)

**Content Collections (`src/content.config.ts`):**
```typescript
import { defineCollection, z } from 'astro:content';

const blogCollection = defineCollection({
  type: 'content',
  schema: z.object({
    title: z.string(),
    description: z.string(),
    pubDate: z.coerce.date(),
    heroImage: z.string(),
    category: z.string(),
    tags: z.array(z.string()),
    readTime: z.number(),
    featured: z.boolean(),
    amazonLink: z.string(),
  }),
});

export const collections = {
  'blog': blogCollection,
};
```

**Criterios de éxito:**
- [ ] `/blog` muestra lista de posts
- [ ] `/blog/[slug]` muestra post individual
- [ ] Componentes renderizan datos del frontmatter
- [ ] Diseño responsive
- [ ] Imágenes optimizadas con `<Image />`

---

### 🌐 FASE 6: Netlify + Build Hook
**Duración:** 1 hora  
**Dependencias:** Fase 5 completada

**Objetivo:** Configurar deploy automático en Netlify.

**Tareas:**
1. [ ] Configurar `netlify.toml`
2. [ ] Generar Build Hook en dashboard de Netlify
3. [ ] Agregar `NETLIFY_BUILD_HOOK` a `.env`
4. [ ] Verificar que el hook dispara el build

**Configuración `netlify.toml`:**
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

**Criterios de éxito:**
- [ ] `netlify.toml` configurado
- [ ] Build Hook URL en variables de entorno
- [ ] Deploy funciona al llamar al hook

---

### ✅ FASE 7: Testing y Validación
**Duración:** 2 horas  
**Dependencias:** Fase 6 completada

**Objetivo:** Validar que todo funciona correctamente.

**Tareas:**
1. [ ] Test unitario: `core/forge_blog.py`
2. [ ] Test integración: Sheets → Markdown
3. [ ] Test build: Astro compila sin errores
4. [ ] Test deploy: Netlify publica correctamente
5. [ ] Validar SEO: metadatos, OpenGraph

**Checklist de validación:**
- [ ] Posts se generan desde Sheets
- [ ] Markdown tiene frontmatter válido
- [ ] Slugs son únicos
- [ ] Imágenes se optimizan
- [ ] Links afiliados funcionan
- [ ] Responsive en móvil
- [ ] PageSpeed > 95

**Criterios de éxito:**
- [ ] Todos los tests pasan
- [ ] Sitio desplegado y accesible
- [ ] Flujo completo: Sheets → Publicación

---

### 📖 FASE 8: Documentación Final
**Duración:** 1 hora  
**Dependencias:** Fase 7 completada

**Objetivo:** Documentar el sistema para uso del Soberano.

**Tareas:**
1. [ ] Crear `Docs/BLOG_ENGINE_GUIDE.md`
2. [ ] Actualizar `SKILL_REGISTRY.md` con skill de blog
3. [ ] Crear template de escritura para Andrés
4. [ ] Documentar troubleshooting
5. [ ] Guardar lecciones en Engram

**Estructura del guide:**
```markdown
# Guía: Blog Engine

## Cómo escribir un post
1. Abrir Google Sheets → pestaña BLOG_CONTENIDO
2. Crear fila con Estado = BORRADOR
3. Escribir Título, Categoría, Cuerpo_Raw
4. Agregar metadatos
5. Cambiar Estado a LISTO_PARA_FORJAR

## Cómo publicar
1. Ejecutar: python tools/forge_blog.py
2. Verificar que estado cambia a PUBLICADO
3. Esperar build de Netlify (~2 min)
4. Verificar en dominio

## Troubleshooting
...
```

**Criterios de éxito:**
- [ ] Guía completa escrita
- [ ] Skill agregado al registry
- [ ] Lecciones guardadas en Engram

---

## 📅 CRONOGRAMA

| Fase | Duración | Dependencias | Documentos Base |
|------|----------|--------------|-----------------|
| **FASE 1** | 30 min | - | GENTLEMAN_AI_SETUP.md |
| **FASE 2** | 2-3 horas | Fase 1 | Blog Engine PRD (sec 4) |
| **FASE 3** | 1 hora | Fase 2 | Blog Engine PRD (sec 3) |
| **FASE 4** | 3-4 horas | Fase 3 | SKILL_REGISTRY.md, MIURA_WORKFLOW_SD.md |
| **FASE 5** | 2-3 horas | Fase 4 | Astro docs |
| **FASE 6** | 1 hora | Fase 5 | Netlify docs |
| **FASE 7** | 2 horas | Fase 6 | pytest docs |
| **FASE 8** | 1 hora | Fase 7 | - |

**Total estimado:** 13-17 horas

---

## 🚀 PRÓXIMOS PASOS INMEDIATOS

Para empezar AHORA:

1. **Leer documentos existentes:**
   - `skills/SKILL_REGISTRY.md`
   - `Docs/MIURA_WORKFLOW_SD.md`
   - `MiuraForge_BlogEngine_PRD.md`

2. **Decidir:** ¿Empezamos con Fase 1 (Gentleman AI) o preferís saltear y empezar directo con Fase 2 (Astro)?

3. **Si empezamos con Gentleman:** Ejecutar instalación en PowerShell

4. **Si empezamos directo:** Crear proyecto Astro

---

## 📁 ARCHIVOS CREADOS/ACTUALIZADOS

**Nuevos:**
- `PLAN_TRABAJO_BLOG.md` (este documento)
- `core/forge_blog.py` (Fase 4)
- `tools/forge_blog.py` (Fase 4)
- `src/content.config.ts` (Fase 5)
- `Docs/BLOG_ENGINE_GUIDE.md` (Fase 8)

**Actualizados:**
- `skills/SKILL_REGISTRY.md` - Agregar skill de blog
- `core/database.py` - Verificar lectura de nueva hoja

---

**Versión:** 1.0  
**Autor:** Gran Visir  
**Basado en:** SDD Workflow (9 fases) + PRD MF-003  
**Estado:** LISTO_PARA_FORJAR
