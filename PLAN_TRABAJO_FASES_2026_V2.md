# ⚔️ PLAN DE TRABAJO POR FASES V2 - MIURA FORGE ENGINE

> **Versión:** 2.0 - Reestructurado  
> **Fecha:** Marzo 2026  
> **Prioridad:** App → Canal → Web  
> **Stack:** Netlify + Astro + Google Sheets + Python

---

## 🎯 NUEVA ESTRATEGIA: App Primero, Web Después

**Fases reordenadas:**
1. **FASE 1:** Pulir App (YouTube/Shorts) - URGENTE
2. **FASE 2:** Mejorar Canal (contenido + branding) - ALTA
3. **FASE 3:** Sitio Web Completo (blog + todo) - MEDIA
4. **FASE 4:** Profesionalización (tests + CI/CD) - BAJA

**Razón:** La app genera contenido AHORA. El web puede esperar.

---

## ⚔️ FASE 1: PULIR LA APP (YouTube/Shorts)

### Semanas 1-2 - 25 horas | IMPACTO: URGENTE

**Objetivo:** Corregir errores LSP, unificar código, optimizar para próxima investigación.

#### Día 1-2: Corrección Errores LSP (8 horas)

**Tarea 1.1: core/database.py (3 horas)**

Errores a corregir: 15+
```python
# ANTES (error):
self.produccion.get_all_records()  # produccion puede ser None

# DESPUÉS (correcto):
if not self.produccion:
    print("⚠️ [Database] PRODUCCION no disponible")
    return []
all_values = self.produccion.get_all_records()
```

Archivos prioritarios:
- [ ] core/database.py - Agregar guard clauses en todos los métodos
- [ ] core/architect.py - Verificar info_csv antes de usar
- [ ] core/researcher.py - Agregar import Database
- [ ] motion_forge/motion_forge_playwright.py - Corregir import

**Tarea 1.2: Revisar correcciones (2 horas)**

```bash
# Verificar que no queden errores críticos
python -c "from core.database import Database; print('OK')"
python -c "from core.architect import Architect; print('OK')"
python -c "from core.researcher import Researcher; print('OK')"
```

#### Día 3-4: Mejoras de Código (8 horas)

**Tarea 1.3: Validador de Acciones Físicas**

Crear `core/accion_validator.py`:
```python
"""
Validador de CTAs - Verifica que sean acciones físicas concretas
"""

VERBOS_FISICOS = [
    "abre", "escribe", "bloquea", "elimina", 
    "calcula", "levanta", "corre", "llama",
    "mira", "apunta", "cierra", "empieza"
]

VERBOS_PROHIBIDOS = [
    "piensa", "considera", "evalúa", "planea",
    "podrías", "quizás", "tal vez", "intenta"
]

def validar_cta(cta: str) -> tuple[bool, list[str]]:
    """
    Valida que el CTA sea físico y concreto.
    Retorna: (es_valido, problemas)
    """
    problemas = []
    cta_lower = cta.lower()
    
    # Verificar verbos prohibidos
    for verbo in VERBOS_PROHIBIDOS:
        if verbo in cta_lower:
            problemas.append(f"Verbo prohibido: '{verbo}'")
    
    # Verificar verbos físicos
    tiene_verbo_fisico = any(v in cta_lower for v in VERBOS_FISICOS)
    if not tiene_verbo_fisico:
        problemas.append("No contiene verbo físico concreto")
    
    return len(problemas) == 0, problemas
```

**Tarea 1.4: Sistema Anti-Repetición**

Mejorar `llm/memory_manager.py`:
```python
def get_metaphoras_prohibidas(self, sesion_id: str) -> list[str]:
    """
    Retorna metáforas usadas en la sesión actual
    para evitar repetición entre fases.
    """
    # Implementar lógica de tracking de metáforas
    pass
```

#### Día 5: Testing Manual (5 horas)

**Tarea 1.5: Prueba de integración**

```bash
# Testear flujo completo
python main_orquestador.py

# Seleccionar opción 1 (EXPLORE)
# Verificar que no hay errores

# Testear generación de guion
# Verificar validación de CTA
```

**Tarea 1.6: Documentar cambios**

Actualizar `Docs/CAMBIOS_FASE_1.md` con:
- Qué errores se corrigieron
- Qué mejoras se agregaron
- Cómo validar que funciona

### Checklist FASE 1

- [x] Errores LSP corregidos en core/database.py
- [x] Errores LSP corregidos en core/architect.py
- [x] Errores LSP corregidos en core/researcher.py
- [x] Import corregido en motion_forge_playwright.py
- [x] Validador de acciones físicas implementado
- [x] Sistema anti-repetición mejorado
- [x] Pruebas manuales pasan
- [x] Documentación actualizada

**OUTPUT:** App pulida y lista para investigación

---

## ⚔️ FASE 2: MEJORAR EL CANAL (YouTube)

### Semanas 3-4 - 20 horas | IMPACTO: ALTO

**Objetivo:** Diferenciar contenido, mejorar branding, aumentar conversión.

#### Semana 3 - Branding y Contenido (12 horas)

**Tarea 2.1: Thumbnails Diferenciados**

Especificaciones técnicas:
```
Tamaño: 1280x720px (YouTube Shorts thumbnail)
Colores: 
  - Fondo: Negro profundo (#0a0a0a)
  - Acento: Naranja quemado (#d4561a)
  - Texto: Blanco o acero (#c0c0c0)
Tipografía: Bebas Neue (bold, industrial)
Elementos:
  - Texto grande (máx 5-6 palabras)
  - Cara expresiva (emoción fuerte)
  - Fondo cinemático (blurred industrial)

Formato texto:
"TE CONVENCISTE DE QUE"
"[verdad incómoda en 2-3 palabras]"

Ejemplo: "TE CONVENCISTE DE QUE MAÑANA SERÁ DIFERENTE"
```

**Tarea 2.2: Serie "El Diagnóstico"**

Nuevo formato de videos 60-90s:
```
Estructura "El Diagnóstico":

0-5s: HOOK AGRESIVO
"Te convenciste de que eres productivo."
"La verdad: eres un cobarde organizado."
"Sigo."

5-20s: CASO REAL (anónimo)
"Un hombre de 32 años me escribió..."
"...lleva 5 años 'planeando' su negocio"
"...nunca empezó."

20-40s: DIAGNÓSTICO
"No es falta de tiempo."
"Es terror al resultado real."
"Si empiezas y fallas, pierdes la fantasía."
"Y prefieres soñar a probar."

40-55s: SENTENCIA FINAL
"El problema no es el plan."
"Es que elegiste la ilusión sobre la prueba."

55-60s: CTA
"Descarga el diagnóstico completo."
"Link en la descripción."
```

**Tarea 2.3: Actualizar Tagline**

```
ANTES:
"Disciplina en Acero - Desarrollo Personal Masculino"

DESPUÉS:
"Disciplina en Acero - Diagnóstico Quirúrgico del Fracaso Masculino"

Tagline secundario:
"No te motivamos. Te mostramos por qué fallas."
```

**Tarea 2.4: Calendario Editorial**

4 videos/semana:
```
Lunes: "El Diagnóstico" (caso real + análisis)
Miércoles: "La Verdad" (concepto filosófico corto)
Viernes: "La Forja" (acción práctica, ejercicio)
Domingo: "Preguntas" (respuestas a comentarios)
```

#### Semana 4 - Optimización Canal (8 horas)

**Tarea 2.5: Mejorar CTA Videos**

Agregar a `core/architect.py`:
```python
CTA_NUEVO = """
Si esto duele, no porque te humille.
Porque revela una verdad que elegiste ignorar.

Descarga el diagnóstico gratuito.
Link en la descripción.
"""
```

**Tarea 2.6: Bio YouTube Actualizada**

```
Diagnóstico quirúrgico del autoengaño masculino.
No te motivamos. Te mostramos por qué fallas.

📥 Diagnóstico gratuito:
🔗 disciplinaenacero.com

📕 Ebook: El Hombre que Dejó de Mentirse
💰 $9 USD
```

**Tarea 2.7: Análisis Competencia**

Investigar 5 canales competencia:
- Andrew Tate (qué NO hacer)
- Hamza (qué mejorar)
- Improvement Pill (diferenciación)
- The Roommates (nicho)
- Better Ideas (contenido)

Extraer:
- Thumbnails más virales
- Estructura de sus mejores videos
- Cómo capturan leads
- Cómo monetizan

### Checklist FASE 2

- [ ] Template thumbnails creado (Canva)
- [ ] Serie "El Diagnóstico" grabada (4 videos)
- [ ] Tagline actualizado en todas partes
- [ ] Bio YouTube actualizada
- [ ] CTA mejorado en scripts
- [ ] Calendario editorial publicado
- [ ] Análisis competencia completado

**OUTPUT:** Canal diferenciado con identidad única

---

## ⚔️ FASE 3: SITIO WEB COMPLETO

### Semanas 5-8 - 40 horas | IMPACTO: MEDIA

**Nota:** Esta fase puede esperar. El web es importante pero NO urgente.

#### Semana 5: Preparación (8 horas)

**Tarea 3.1: Instalar Astro**

```bash
# Prerequisitos: Node.js instalado
node --version  # Debe ser v18+

# Crear proyecto Astro
cd D:\YT\MiuraForge
npm create astro@latest disciplinaenacero-astro -- --template blog

# Configurar
cd disciplinaenacero-astro
npx astro add netlify
npx astro add tailwind

# Instalar dependencias
npm install
```

**Tarea 3.2: Configurar Git**

```bash
# Inicializar repositorio
cd disciplinaenacero-astro
git init

# Crear .gitignore
cat > .gitignore << EOF
node_modules/
dist/
.env
.DS_Store
*.log
EOF

# Primer commit
git add .
git commit -m "Initial commit - Astro + Netlify"

# Conectar a GitHub (opcional)
git remote add origin https://github.com/usuario/disciplinaenacero.git
git push -u origin main
```

#### Semana 6: Blog Engine (12 horas)

**Tarea 3.3: Configurar Sheets**

En hoja "BD_MiuraForge_Engine":
1. Crear pestaña "BLOG_CONTENIDO"
2. Headers (14 columnas):
```
ID | Estado | Título | Slug | Fecha | Descripción | Keywords | Categoría | Imagen_URL | Enlace_Afiliado_Amazon | Cuerpo_Raw | Tags | ReadTime_Min | Featured
```

**Tarea 3.4: Integrar forge_blog.py**

El archivo ya existe: `disciplinaenacero/forge_blog.py` (347 líneas, COMPLETO)

```bash
# Probar funcionamiento
python disciplinaenacero/forge_blog.py --dry-run

# Procesar un post de prueba
python disciplinaenacero/forge_blog.py --id 1

# Verificar generación
ls disciplinaenacero-astro/src/content/blog/
```

**Tarea 3.5: Content Collections**

Configurar `src/content.config.ts`:
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

#### Semana 7: Diseño Web (12 horas)

**Tarea 3.6: Migrar HTML a Astro**

```
Migrar:
- index.html → src/pages/index.astro
- pages/about.html → src/pages/about.astro
- pages/ebook.html → src/pages/ebook.astro

Nuevo:
- src/pages/blog/index.astro (listado)
- src/pages/blog/[slug].astro (post individual)
```

**Tarea 3.7: Componentes Astro**

Crear `src/components/`:
- `ResenaCard.astro` - Card para listado
- `CTA_Acero.astro` - Call to action
- `Header.astro` - Navegación
- `Footer.astro` - Pie de página

**Tarea 3.8: Lead Capture Web**

Integrar formulario:
```html
<!-- En landing page -->
<form id="leadForm">
  <input type="email" name="email" required>
  <button type="submit">Quiero el diagnóstico</button>
</form>
```

Backend: `tools/capture_lead.py` (usar Brevo API)

#### Semana 8: Deploy y Automatización (8 horas)

**Tarea 3.9: Deploy en Netlify**

```bash
# Build
npm run build

# Deploy manual inicial
npx netlify-cli deploy --prod --dir=dist

# Configurar dominio personalizado
# Netlify Dashboard → Domain settings → Add custom domain
```

**Tarea 3.10: Build Hook Automatizado**

Ya configurado en `.env`:
```bash
NETLIFY_BUILD_HOOK=https://api.netlify.com/build_hooks/TU_ID
```

Usar en `forge_blog.py`:
```python
import requests
requests.post(NETLIFY_BUILD_HOOK)
```

**Tarea 3.11: GitHub Actions (opcional)**

Crear `.github/workflows/deploy.yml`:
```yaml
name: Deploy
on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
      - run: npm install
      - run: npm run build
      - uses: netlify/actions/cli@master
        with:
          args: deploy --prod --dir=dist
        env:
          NETLIFY_AUTH_TOKEN: ${{ secrets.NETLIFY_AUTH_TOKEN }}
          NETLIFY_SITE_ID: ${{ secrets.NETLIFY_SITE_ID }}
```

### Checklist FASE 3

- [ ] Astro instalado y configurado
- [ ] Git inicializado
- [ ] Sheets pestaña BLOG_CONTENIDO creada
- [ ] forge_blog.py probado
- [ ] Content Collections configurado
- [ ] HTML migrado a Astro
- [ ] Componentes creados
- [ ] Lead capture integrado
- [ ] Netlify deploy funcionando
- [ ] Build hook automatizado

**OUTPUT:** Sitio web completo con blog automatizado

---

## ⚔️ FASE 4: PROFESIONALIZACIÓN

### Semanas 9-10 - 20 horas | IMPACTO: BAJA

**Objetivo:** Tests, CI/CD, documentación final.

#### Semana 9: Testing (10 horas)

**Tarea 4.1: Tests Unitarios**

Crear `tests/`:
```python
# tests/test_alchemist.py
import pytest
from core.alchemist import Alchemist

def test_transmutar_dolor():
    alchemist = Alchemist()
    resultado = alchemist.transmutar_dolor("procrastinacion", context="test")
    assert resultado is not None
```

**Tarea 4.2: Configurar pytest**

```bash
pip install pytest pytest-cov
pytest --cov=core tests/
```

#### Semana 10: CI/CD (10 horas)

**Tarea 4.3: GitHub Actions**

Crear `.github/workflows/ci.yml`:
```yaml
name: CI
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
      - run: pip install -r requirements.txt
      - run: pytest
      - run: black --check .
      - run: ruff check .
```

**Tarea 4.4: Documentación Final**

Crear documentación completa:
- `README.md` actualizado
- `Docs/ARQUITECTURA.md`
- `Docs/API.md`
- `Docs/DEPLOY.md`

### Checklist FASE 4

- [ ] Tests unitarios creados
- [ ] pytest configurado
- [ ] CI/CD funcionando
- [ ] Documentación completa

**OUTPUT:** Proyecto profesional, testeado y documentado

---

## 📊 CRONOGRAMA RESUMIDO

| Semana | Fase | Horas | Prioridad |
|--------|------|-------|-----------|
| 1-2 | Pulir App | 25h | 🔴 URGENTE |
| 3-4 | Mejorar Canal | 20h | 🔴 ALTO |
| 5-8 | Sitio Web | 40h | 🟡 MEDIA |
| 9-10 | Profesionalización | 20h | 🟢 BAJA |

**Total:** 10 semanas / ~105 horas

---

## 💰 PROYECCIÓN DE INGRESOS

**Modelo Conservador (6 meses post-FASE 2):**

Con el canal mejorado (FASE 2):
- Mes 1-2: $90/mes (10 ventas)
- Mes 3-4: $270/mes (30 ventas)
- Mes 5-6: $450/mes (50 ventas)

**Total 6 meses:** ~$1,200 USD

Con sitio web (FASE 3 completa):
- SEO orgánico → +50% tráfico
- Blog posts → +30% leads
- **Total proyectado:** $2,000-3,000 USD

---

## 🎯 DECISIONES TÉCNICAS

### ¿Por qué SQLite NO es necesario?

**Sheets es mejor:**
- ✅ Andrés escribe directamente
- ✅ Ya configurado
- ✅ No sincronización
- ✅ Backup automático
- ✅ Acceso universal

**SQLite solo si:**
- Volumen >100k registros
- Queries complejas necesarias
- Transacciones ACID críticas

### ¿Por qué Netlify?

- ✅ Build hooks (automatización)
- ✅ HTTPS gratuito
- ✅ CDN global
- ✅ Astro integrado

### ¿Por qué Astro?

- ✅ Content Collections
- ✅ Zero JS (velocidad)
- ✅ SEO optimizado
- ✅ Markdown nativo

---

## 📎 RECURSOS

### Herramientas (gratuitas)

| Servicio | Costo | Propósito |
|----------|-------|-----------|
| Netlify | Gratis | Hosting |
| Google Sheets | Gratis | Database |
| ImprovMX | Gratis | Email |
| Brevo | Gratis (300/día) | Email marketing |
| PayPal | % transacción | Pagos |
| GitHub | Gratis | Repo + CI/CD |
| Canva | Gratis | Thumbnails |
| Astro | Gratis | Framework |

### Presupuesto Mensual

- Mes 1-3: $0
- Mes 4-6: $19 (Brevo 10k)
- Mes 7+: $49 (Brevo + premium)

---

## ✅ CHECKLIST FINAL

### Antes de empezar:
- [ ] Leer AUDITORIA_ERRORES_LSP.md
- [ ] Verificar credenciales funcionan
- [ ] Backup de archivos importantes

### Progreso:
- [x] FASE 1 completada
- [ ] FASE 2 completada
- [ ] FASE 3 completada
- [ ] FASE 4 completada

---

## 🚀 PRÓXIMOS PASOS

**Esta semana (FASE 1 - Día 1):**
1. Corregir errores LSP en core/database.py
2. Corregir errores LSP en core/architect.py
3. Corregir errores LSP en core/researcher.py
4. Testear que la app funciona

**¿Listo para empezar?**

---

**Documento creado:** Marzo 2026  
**Versión:** 2.0 - Reestructurado  
**Próxima revisión:** Después de FASE 1  
**Estado:** LISTO_PARA_EJECUTAR

---

*"App primero, web después. El contenido genera el negocio."*
