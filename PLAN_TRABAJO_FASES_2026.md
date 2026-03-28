# ⚔️ PLAN DE TRABAJO POR FASES - MIURA FORGE ENGINE

> **Versión:** 1.0  
> **Fecha:** Marzo 2026  
> **Estrategia:** De herramientas a negocio  
> **Stack:** Netlify + Astro + Google Sheets + Python  
> **Base de Datos:** Google Sheets (NO SQLite necesario)

---

## 🎯 VISIÓN GENERAL

**Objetivo:** Transformar Miura Forge de "máquina de contenido" a "máquina de negocio".

**Flujo de Trabajo:**
```
YouTube Shorts → Website (Astro) → Lead Magnet → Email → Producto
```

**Stack Confirmado:**
- ✅ **Hosting:** Netlify (Build Hooks disponibles)
- ✅ **Web:** Astro + Content Collections
- ✅ **Database:** Google Sheets (BLOG_CONTENIDO)
- ✅ **Backend:** Python (forge_blog.py existente)
- ✅ **Email:** ImprovMX + Brevo
- ✅ **Pagos:** PayPal

---

## 📋 RESUMEN DE FASES

| Fase | Nombre | Duración | Objetivo | Impacto |
|------|--------|----------|----------|---------|
| **FASE A** | Cimientos de Negocio | Semana 1 | Conectar embudo de ventas | 🔥🔥🔥 CRÍTICO |
| **FASE B** | Diferenciación | Semanas 2-3 | Marca única en YouTube | 🔥🔥🔥 ALTO |
| **FASE C** | Expansión Digital | Semanas 4-6 | Blog Engine + Astro | 🔥🔥 MEDIO |
| **FASE D** | Profesionalización | Semanas 7-8 | Tests + CI/CD | 🔥 BAJO |

**Total:** 8 semanas / ~85 horas

---

## ⚔️ FASE A: CIMIENTOS DE NEGOCIO

### Semana 1 - 15 horas | IMPACTO: CRÍTICO

**Objetivo:** Generar ingresos inmediatos conectando el embudo.

#### Día 1 - Configuración Base (3 horas)

**Tarea A1.1: ImprovMX (Email con dominio propio)**
```
✅ Ir a https://improvmx.com
✅ Agregar dominio: disciplinaenacero.com
✅ Crear alias: contacto@ → tu Gmail
✅ En registrador de dominio: agregar MX records de ImprovMX
✅ Verificar con email de prueba

OUTPUT: contacto@disciplinaenacero.com funcionando
```

**Tarea A1.2: Brevo (Email Marketing)**
```
✅ Ir a https://www.brevo.com (gratuito hasta 300 emails/día)
✅ Crear cuenta
✅ Verificar dominio ( SPF/DKIM )
✅ Crear lista: "Leads - Ebook Gratis"
✅ Obtener API Key para conectar con web

OUTPUT: API Key guardada en .env como BREVO_API_KEY
```

**Tarea A1.3: Variables de entorno**
```bash
# Agregar a .env:
NETLIFY_BUILD_HOOK=https://api.netlify.com/build_hooks/TU_ID
BREVO_API_KEY=xkeysib-TU_API_KEY
PAYPAL_CLIENT_ID=TU_CLIENT_ID
PAYPAL_CLIENT_SECRET=TU_SECRET
```

#### Día 2 - Lead Capture (4 horas)

**Tarea A2.1: Formulario en Website**

Editar `disciplinaenacero/index.html`:
```html
<!-- Sección Lead Magnet -->
<section id="lead-magnet">
  <h2>El Diagnóstico Gratuito</h2>
  <p>Descubre por qué sigues procrastinando (y cómo detenerlo hoy)</p>
  
  <form id="leadForm" action="/api/capture" method="POST">
    <input type="email" name="email" placeholder="tu@email.com" required>
    <button type="submit">Quiero el diagnóstico</button>
  </form>
</section>
```

**Tarea A2.2: Script de captura (backend simple)**

Crear `tools/capture_lead.py`:
```python
"""
Capture lead desde formulario web
Guarda en Google Sheets tabla LEADS
Envía ebook por Brevo
"""
import os
import sys
from datetime import datetime
sys.path.append('.')
from core.database import Database

def capture_lead(email: str, fuente: str = "website"):
    db = Database()
    
    # Guardar en Sheets
    db.leads.append_row([
        datetime.now().isoformat(),
        email,
        fuente,
        "nuevo"
    ])
    
    # Enviar email con Brevo (implementar)
    # send_ebook_brevo(email)
    
    return True
```

**OUTPUT:** Formulario web conectado a Sheets

#### Día 3 - PayPal (3 horas)

**Tarea A3.1: Configurar PayPal**
```
✅ Ir a https://developer.paypal.com
✅ Crear app "Disciplina en Acero - Ebook"
✅ Obtener Client ID y Secret
✅ Modo: Sandbox → Producción (cuando listo)
✅ Crear botón "Buy Now" 
✅ Precio: $9 USD
✅ Producto digital: "El Hombre que Dejó de Mentirse - Ebook"
```

**Tarea A3.2: Página de ventas**

Editar `disciplinaenacero/pages/ebook.html`:
```html
<h1>El Hombre que Dejó de Mentirse</h1>
<p>El sistema operativo mental para hombres que están cansados de prometerse cambios que nunca cumplen.</p>

<div class="precio">$9 USD</div>

<!-- Botón PayPal -->
<div id="paypal-button-container"></div>
<script>
  paypal.Buttons({
    createOrder: function(data, actions) {
      return actions.order.create({
        purchase_units: [{
          amount: { value: '9.00' }
        }]
      });
    }
  }).render('#paypal-button-container');
</script>
```

#### Día 4 - YouTube CTA (3 horas)

**Tarea A4.1: Actualizar bio YouTube**
```
Nueva bio:
"Diagnóstico quirúrgico del autoengaño masculino.
No te motivamos. Te mostramos por qué fallas.

📥 Descarga el diagnóstico gratuito:
🔗 disciplinaenacero.com

📕 Ebook: El Hombre que Dejó de Mentirse"
```

**Tarea A4.2: Script CTA para videos**

Agregar a `core/architect.py` (en redactar_guion_completo):
```python
CTA_ESTANDAR = """
Si esto te duele, no porque te humille. 
Porque revela algo que elegiste ignorar.

Descarga el diagnóstico gratuito. 
Link en la descripción.
"""

# Agregar al final de cada guion_master
guion_master += "\n\n" + CTA_ESTANDAR
```

#### Día 5 - Testing (2 horas)

**Tarea A5.1: Testear flujo completo**
```
✅ Enviar email de prueba desde formulario
✅ Verificar llega a Sheets
✅ Verificar llega a Brevo
✅ Testear compra PayPal (modo sandbox)
✅ Testear descarga ebook
✅ Testear CTA en video de prueba
```

### Checklist FASE A

- [ ] ImprovMX configurado
- [ ] Brevo configurado
- [ ] Formulario web capturando leads
- [ ] PayPal configurado
- [ ] Bio YouTube actualizada
- [ ] CTA en scripts de guion
- [ ] Testeado y funcionando

**OUTPUT:** Embudo funcional (YouTube → Web → Lead → Email)

---

## ⚔️ FASE B: DIFERENCIACIÓN DE MARCA

### Semanas 2-3 - 20 horas | IMPACTO: ALTO

**Objetivo:** Diferenciar "Disciplina en Acero" del montón de canales de masculinidad.

#### Semana 2 - Identidad Visual (10 horas)

**Tarea B2.1: Thumbnails únicos**

Crear template de thumbnail en Canva:
```
Especificaciones:
- Tamaño: 1280x720px (YouTube)
- Colores: Negro + Naranja quemado + Acero metálico
- Tipografía: Bebas Neue o similar (bold, industrial)
- Elementos: Texto grande + cara expresiva + metáfora visual
- Estilo: Blade Runner meets industrial

Formato texto:
"TE CONVENCISTE DE QUE..."
"[verdad incómoda]"

Ejemplo:
"TE CONVENCISTE DE QUE"
"MAÑANA SERÁ DIFERENTE"
```

**Tarea B2.2: Branding consistente**
```
Crear kit de marca:
✅ Logo simplificado (icono de acero/forja)
✅ Paleta de colores oficial
✅ Tipografías: Industrial/sans-serif
✅ Estilo visual: Cinematográfico, oscuro, serio
✅ Assets: Marco de video, lower thirds, transiciones
```

#### Semana 3 - Contenido Diferenciado (10 horas)

**Tarea B3.1: Serie "El Diagnóstico"**

Nuevo formato de videos (shorts largos 60-90s):
```
Estructura "El Diagnóstico":

0-5s: Hook agresivo
"Te convenciste de que eres productivo."
"La verdad: eres un cobarde organizado."

5-20s: Caso real (testimonio)
"Un hombre de 32 años me escribió..."
"...lleva 5 años 'planeando' su negocio"

20-40s: Diagnóstico
"No es falta de tiempo."
"Es terror al resultado real."
"Si empiezas y fallas, ya no puedes soñar."

40-55s: Sentencia
"El problema no es el plan."
"Es que prefieres la fantasía a la prueba."

55-60s: CTA
"Descarga el diagnóstico completo."
"Link en la descripción."
```

**Tarea B3.2: Tagline único**

Nuevo tagline para todos los materiales:
```
ANTES:
"Disciplina en Acero - Desarrollo Personal Masculino"

DESPUÉS:
"Disciplina en Acero - Diagnóstico Quirúrgico del Fracaso Masculino"

Tagline secundario:
"No te motivamos. Te mostramos por qué fallas."
```

**Tarea B3.3: Calendario editorial**

Crear plan de 4 videos/semana:
```
Lunes: "El Diagnóstico" (caso real)
Miércoles: "La Verdad" (concepto filosófico)
Viernes: "La Forja" (acción práctica)
Domingo: "Preguntas" (respuestas comunidad)
```

### Checklist FASE B

- [ ] Template de thumbnails creado
- [ ] Kit de marca definido
- [ ] Serie "El Diagnóstico" (4 videos)
- [ ] Tagline actualizado en todas partes
- [ ] Calendario editorial activo

**OUTPUT:** Canal diferenciado con identidad única

---

## ⚔️ FASE C: EXPANSIÓN DIGITAL (Blog Engine)

### Semanas 4-6 - 30 horas | IMPACTO: MEDIO

**Objetivo:** Implementar Blog Engine con Astro + Netlify.

**Nota:** `forge_blog.py` ya existe y está completo (347 líneas). Solo necesitamos integrarlo.

#### Semana 4 - Migración a Astro (10 horas)

**Tarea C4.1: Inicializar Astro**

```bash
cd D:\YT\MiuraForge
npm create astro@latest disciplinaenacero-astro -- --template blog
cd disciplinaenacero-astro
npx astro add netlify
npx astro add tailwind
```

**Tarea C4.2: Migrar contenido HTML**

Copiar de `disciplinaenacero/` a nuevo proyecto:
```
disciplinaenacero-astro/
├── src/
│   ├── pages/
│   │   ├── index.astro      (migrar de index.html)
│   │   ├── about.astro      (migrar de pages/about.html)
│   │   └── ebook.astro      (migrar de pages/ebook.html)
│   └── content/
│       └── blog/            (posts generados)
```

**Tarea C4.3: Content Collections**

Configurar `src/content.config.ts`:
```typescript
import { defineCollection, z } from 'astro:content';

const blogCollection = defineCollection({
  type: 'content',
  schema: z.object({
    title: z.string(),
    description: z.string(),
    pubDate: z.coerce.date(),
    image: z.string(),
    category: z.string(),
    tags: z.array(z.string()),
    readTime: z.number(),
    featured: z.boolean(),
    amazon_link: z.string(),
  }),
});

export const collections = {
  'blog': blogCollection,
};
```

#### Semana 5 - Integrar forge_blog.py (12 horas)

**Tarea C5.1: Configurar Sheets**

En hoja existente "BD_MiuraForge_Engine":
1. Crear pestaña "BLOG_CONTENIDO"
2. Agregar headers (14 columnas):
   - ID | Estado | Título | Slug | Fecha | Descripción | Keywords | Categoría | Imagen_URL | Enlace_Afiliado_Amazon | Cuerpo_Raw | Tags | ReadTime_Min | Featured

**Tarea C5.2: Probar forge_blog.py**

```bash
# Modo simulación (dry-run)
python disciplinaenacero/forge_blog.py --dry-run

# Procesar un ID específico
python disciplinaenacero/forge_blog.py --id 1

# Procesar todos los pendientes
python disciplinaenacero/forge_blog.py
```

**Tarea C5.3: Automatizar con GitHub Actions (opcional)**

Crear `.github/workflows/blog.yml`:
```yaml
name: Blog Engine
on:
  schedule:
    - cron: '0 */6 * * *'  # Cada 6 horas
  workflow_dispatch:

jobs:
  forjar:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      - run: pip install -r requirements.txt
      - run: python disciplinaenacero/forge_blog.py
      - uses: stefanzweifel/git-auto-commit-action@v4
        with:
          commit_message: "Nuevos posts del blog"
```

#### Semana 6 - Componentes y Deploy (8 horas)

**Tarea C6.1: Componentes Astro**

Crear `src/components/`:
```astro
---
// ResenaCard.astro
const { post } = Astro.props;
---
<article class="bg-gray-900 p-6 rounded-lg">
  <img src={post.image} alt={post.title} />
  <h2>{post.title}</h2>
  <p>{post.description}</p>
  <span>{post.readTime} min de lectura</span>
  <a href={`/blog/${post.slug}`}>Leer →</a>
</article>
```

**Tarea C6.2: Página de blog**

Crear `src/pages/blog.astro`:
```astro
---
import { getCollection } from 'astro:content';
import ResenaCard from '../components/ResenaCard.astro';

const posts = await getCollection('blog');
---

<h1>Reseñas de Acero</h1>
<div class="grid">
  {posts.map(post => <ResenaCard post={post} />)}
</div>
```

**Tarea C6.3: Deploy**

```bash
# Build
npm run build

# Netlify deploy
npx netlify-cli deploy --prod --dir=dist
```

### Checklist FASE C

- [ ] Proyecto Astro creado
- [ ] Netlify configurado
- [ ] Sheets pestaña BLOG_CONTENIDO creada
- [ ] forge_blog.py funcionando
- [ ] Componentes Astro creados
- [ ] Deploy automático funcionando

**OUTPUT:** Blog automatizado generando posts desde Sheets

---

## ⚔️ FASE D: PROFESIONALIZACIÓN

### Semanas 7-8 - 20 horas | IMPACTO: BAJO

**Objetivo:** Tests, CI/CD y refactorización.

#### Semana 7 - Testing (10 horas)

**Tarea D7.1: Tests unitarios**

Crear `tests/`:
```python
# tests/test_alchemist.py
import pytest
from core.alchemist import Alchemist

def test_transmutar_dolor():
    alchemist = Alchemist()
    resultado = alchemist.transmutar_dolor("procrastinacion", context="test")
    assert resultado is not None
    assert isinstance(resultado, str)
```

**Tarea D7.2: Tests de integración**

```python
# tests/test_pipeline.py
def test_pipeline_completo():
    # Testear flujo: EXPLORE → PROPOSE → SPEC
    pass
```

**Tarea D7.3: Configurar pytest**

```bash
pip install pytest pytest-cov
pytest --cov=core tests/
```

#### Semana 8 - CI/CD y Refactor (10 horas)

**Tarea D8.1: GitHub Actions**

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

**Tarea D8.2: Refactorización**
- Unificar paths hardcodeados
- Agregar type hints
- Mejorar manejo de errores
- Documentar funciones faltantes

**Tarea D8.3: Limpieza**
- Eliminar credenciales legacy de raíz
- Mover archivos temporales
- Actualizar README

### Checklist FASE D

- [ ] Tests unitarios para core/
- [ ] Tests de integración
- [ ] CI/CD funcionando
- [ ] Credenciales legacy eliminadas
- [ ] Código refactorizado
- [ ] Documentación actualizada

**OUTPUT:** Código profesional, testeado y automatizado

---

## 💰 PROYECCIÓN DE INGRESOS

### Modelo Conservador (6 meses)

**Supuestos:**
- YouTube: 10k → 50k suscriptores
- Conversión leads: 2% de viewers
- Conversión ventas: 10% de leads
- Precio ebook: $9 USD

**Proyección:**
```
Mes 1-2: 100 leads/mes × 10% × $9 = $90/mes
Mes 3-4: 300 leads/mes × 10% × $9 = $270/mes  
Mes 5-6: 500 leads/mes × 10% × $9 = $450/mes

Total 6 meses: ~$1,200 USD
```

**Con upsells:**
- Ebook: $9 (entry)
- Comunidad Discord: $19/mes
- Mentoría 1:1: $97

**Proyección optimista:** $3,000-5,000 USD en 6 meses

---

## 📊 MÉTRICAS DE ÉXITO

### KPIs por Fase

**FASE A (Fin Semana 1):**
- Embudo funcional: SÍ/NO
- Leads capturados: >10
- Primeras ventas: >0

**FASE B (Fin Semana 3):**
- Thumbnails nuevos: >20
- Videos "El Diagnóstico": >4
- Engagement rate: >5%

**FASE C (Fin Semana 6):**
- Blog posts generados: >10
- Tráfico orgánico: >100 visitas/mes
- Tiempo carga: <3s

**FASE D (Fin Semana 8):**
- Cobertura tests: >70%
- Errores en CI: 0
- Deuda técnica: Baja

---

## 🛠️ DECISIONES TÉCNICAS

### ¿Por qué NO SQLite?

**Sheets es mejor porque:**
1. ✅ Andrés escribe directamente (interfaz familiar)
2. ✅ Ya configurado y funcionando
3. ✅ No hay que sincronizar nada
4. ✅ Backup automático en Google Drive
5. ✅ Acceso desde cualquier dispositivo

**Cuándo considerar SQLite:**
- Si necesitas queries complejas (JOINs, aggregations)
- Si el volumen supera 100k registros
- Si necesitas transacciones ACID

**Por ahora: Sheets es perfecto.**

### ¿Por qué Netlify?

**Ventajas para este proyecto:**
1. ✅ Build hooks (automatización desde Python)
2. ✅ Astro integrado nativamente
3. ✅ HTTPS gratuito
4. ✅ CDN global
5. ✅ Form handling (para leads)
6. ✅ Functions serverless (opcional)

### ¿Por qué Astro?

1. ✅ Content Collections (perfecto para blog)
2. ✅ Zero JS por defecto (velocidad)
3. ✅ Integración Netlify nativa
4. ✅ SEO optimizado
5. ✅ Markdown como base de datos

---

## 📎 RECURSOS NECESARIOS

### Herramientas (gratuitas/iniciales)

| Servicio | Costo | Propósito |
|----------|-------|-----------|
| Netlify | Gratis | Hosting web |
| Google Sheets | Gratis | Base de datos |
| ImprovMX | Gratis | Email dominio |
| Brevo | Gratis (300/día) | Email marketing |
| PayPal | % transacción | Pagos |
| GitHub | Gratis | Repositorio + CI/CD |
| Canva | Gratis | Thumbnails |

### Presupuesto Mensual (escalando)

- Mes 1-3: $0 (todo gratis)
- Mes 4-6: $19 (Brevo 10k emails)
- Mes 7+: $49 (Brevo + herramientas premium)

---

## ✅ CHECKLIST FINAL

### Antes de empezar:
- [ ] Leer AUDITORIA_COMPLETA_2026.md
- [ ] Confirmar acceso a dominio disciplinaenacero.com
- [ ] Verificar credenciales Sheets funcionan
- [ ] Backup de archivos importantes

### Después de cada fase:
- [ ] Testear todo
- [ ] Documentar lecciones en Engram
- [ ] Celebrar victorias 🎉

---

## 🚀 PRÓXIMOS PASOS INMEDIATOS

**Esta semana (FASE A - Día 1):**
1. ✅ Configurar ImprovMX (30 min)
2. ✅ Configurar Brevo (30 min)
3. ✅ Actualizar .env con API keys
4. ✅ Crear tabla LEADS en Sheets
5. ✅ Testear envío de email

**¿Listo para empezar?**

---

**Documento creado:** 26 de Marzo 2026  
**Versión:** 1.0  
**Próxima actualización:** Después de FASE A  
**Estado:** LISTO_PARA_EJECUTAR

---

*"El plan está listo. Las herramientas están forjadas. Es hora de conquistar."*
