# ⚔️ DOCTRINA DE MARKETING - Miura Forge

> Inspirado en ai-marketing-claude (referencia, no adaptación)  
> **Stack:** NVIDIA + Gemini + Python + Sheets  
> **Integración:** Directa al Factory

---

## 🎯 PRINCIPIO DIRECTOR

**NO** adaptamos código de Claude Code.  
**SÍ** extraemos metodología y construimos versiones propias.

Nuestro motor es diferente: rotación de 10 APIs NVIDIA + Gemini + Python + Sheets.

---

## 📊 1. SCORING RUBRICS SEO (0-100)

### Dimensión: Content & Messaging (25%)

| Criterio | Peso | Qué Medimos | Score |
|----------|------|-------------|-------|
| Headline | 5% | ¿Ganchos en primera línea? | 0-100 |
| Value Prop | 5% | ¿Diferenciador claro? | 0-100 |
| Copy Quality | 10% | ¿Tono alineado doctrina? | 0-100 |
| CTAs | 5% | ¿Acciones físicas concretas? | 0-100 |

### Dimensión: Conversion Optimization (20%)

| Criterio | Peso | Qué Medimos | Score |
|----------|------|-------------|-------|
| Lead Capture | 5% | ¿Formulario funcional? | 0-100 |
| Funnel | 5% | ¿Flujo lógico? | 0-100 |
| Social Proof | 5% | ¿Testimonios/pruebas? | 0-100 |
| Friction | 5% | ¿Sin barreras? | 0-100 |

### Dimensión: SEO & Discoverability (20%)

| Criterio | Peso | Qué Medimos | Score |
|----------|------|-------------|-------|
| Keywords | 5% | ¿Palabras clave presentes? | 0-100 |
| Meta Tags | 5% | ¿Title/description optimizados? | 0-100 |
| Structure | 5% | ¿H1, H2, headings? | 0-100 |
| Performance | 5% | ¿Velocidad de carga? | 0-100 |

**Implementación:**
```python
# skills/marketing/seo_auditor.py
class SEOAuditor:
    def __init__(self):
        self.brain = LLMFactory.get_brain("marketing")
    
    def auditar_contenido(self, url: str) -> dict:
        # 6 dimensiones, scoring 0-100
        pass
```

---

## 📧 2. SECUENCIAS DE EMAIL

### Funnel Disciplina en Acero

**Lead → Ebook Gratis → Ebook Pagado ($9) → Protocolo 30D ($17) → Bundle Libro + Protocolo ($27)**

#### Secuencia 1: Welcome (Día 0)
**Objetivo:** Entregar ebook, establecer tono

```
Asunto: Tu diagnóstico está listo (y es incómodo)

Hola [Nombre],

Acá está tu diagnóstico gratuito: [LINK]

Una advertencia: esto va a doler.

No porque te humille. Porque revela algo que elegiste ignorar.

Te veo del otro lado,
Andrés

P.D.: Si esto te resuena, el libro completo está disponible por $9.
```

#### Secuencia 2: Nurture (Días 1-6)
**Objetivo:** Construir confianza, educar, vender ebook

| Día | Tema | CTA |
|-----|------|-----|
| 1 | El problema no es la falta de tiempo | Leer diagnóstico |
| 2 | Por qué la motivación te está matando | Ver video |
| 3 | Caso: De 0 a 100 en 30 días | Comprar ebook ($9) |
| 4 | La mentira del "cuando esté listo" | Leer capítulo gratis |
| 5 | Ejercicio: 2 minutos de verdad | Descargar worksheet |
| 6 | ¿Por qué fallaste antes? (y cómo evitarlo) | Comprar ebook ($9) |

#### Secuencia 3: Post-Compra (Inmediato)
**Objetivo:** Entregar ebook, upsell Protocolo 30D

```
Asunto: Acá está tu libro. Y una pregunta incómoda.

Hola [Nombre],

Tu ebook "El Hombre que Dejó de Mentirse": [LINK]

Lee el capítulo 3 primero. Es el más duro.

Ahora, la pregunta incómoda:

¿Vas a ejecutar?

O es otra cosa que "vas a hacer mañana"?

Si querés asegurarte de seguir adelante, hay un Protocolo.

30 días de ejercicios estructurados. Sin escapatorias.

$17. Decidís si lo hacés.

[VER PROTOCOLO 30D]

Andrés
```

**Implementación:**
```python
# skills/marketing/email_sequences.py
class EmailSequences:
    def __init__(self):
        self.brain = LLMFactory.get_brain("emissary")
    
    def generar_secuencia(self, tipo: str, leads: list) -> list:
        # welcome, nurture, post_compra
        pass
```

---

## 🔄 3. FRAMEWORK ANÁLISIS DE FUNNEL

### Funnel Actual (V1):
```
YouTube Shorts
    ↓
Link en bio
    ↓
Landing Page
    ↓
Lead Magnet (Ebook Gratis)
    ↓
Email (Brevo)
    ↓
Secuencia Nurture
    ↓
Ebook Pagado ($9) → $17
        ↓
Protocolo 30D ($17)
        ↓
Bundle Libro + Protocolo ($27)
```

### Análisis por Etapa:

| Etapa | Métrica | Objetivo | Problema Común |
|-------|---------|----------|----------------|
| YouTube | CTR (views) | >5% | Thumbnail genérico |
| Landing | Bounce rate | <60% | No hook claro |
| Lead | Conversion | >10% | Formulario complejo |
| Email | Open rate | >30% | Asuntos genéricos |
| Venta | Conversion | >5% | Sin urgencia |

**Puntos de Fricción:**
1. YouTube → Landing (link no visible)
2. Landing → Lead (formulario largo)
3. Email → Venta (falta urgencia)

**Optimizaciones:**
- Thumbnail diferenciado (texto grande)
- Landing sin distracciones (solo formulario)
- Email con CTA único (no múltiples)
- Urgencia: precio sube en X días

---

## 🛠️ 4. IMPLEMENTACIÓN EN NUESTRO STACK

### Arquitectura:
```
skills/marketing/
├── __init__.py
├── seo_auditor.py          # Auditoría contenido
├── email_sequences.py       # Secuencias funnel
├── funnel_analyzer.py       # Análisis embudo
└── launch_playbook.py       # Lanzamientos
```

### Integración Factory:
```python
# En llm/factory.py
elif task_name == "marketing":
    return ResilientProvider(tiers=[
        NvidiaProvider(model_name="mistralai/mistral-large-3"),
        GeminiProvider()
    ])
```

### Uso:
```python
from skills.marketing.seo_auditor import SEOAuditor

auditor = SEOAuditor()
resultado = auditor.auditar_contenido("disciplinaenacero.com/blog/post-1")
# Devuelve: score 0-100, recomendaciones
```

---

## 📋 5. CHECKLIST MARKETING

### Pre-Launch:
- [ ] SEO auditoría: Score >70
- [ ] Email sequences: 3 listas (welcome, nurture, post)
- [ ] Funnel testeado: flujo completo
- [ ] Links afiliados Amazon: configurados
- [ ] Precios: Ebook $9, Comunidad $19

### Post-Launch:
- [ ] Métricas: CTR, conversion, open rates
- [ ] A/B testing: thumbnails, subject lines
- [ ] Optimización: scoring semanal
- [ ] Reporte: PDF mensual

---

## 💰 6. ENLACES DE AFILIADOS (Amazon)

### Libros a Reseñar (Ejemplos):
1. **"Atomic Habits"** - James Clear
2. **"Can't Hurt Me"** - David Goggins
3. **"Deep Work"** - Cal Newport
4. **"The Psychology of Money"** - Morgan Housel
5. **"Discipline Equals Freedom"** - Jocko Willink

### Categoría: Reseñas de Desarrollo Personal
- Comisión: ~4-8%
- Precio promedio: $15-25
- Ingreso por venta: $0.60-2.00

### Integración Blog:
- Botón "Comprar en Amazon"
- Disclaimer: "Enlace afiliado"
- Tracking: UTM tags

---

## 🎯 PRIORIDADES INMEDIATAS

1. **SEO Auditor:** Para blog posts (FASE 3)
2. **Email Sequences:** Para funnel (FASE 2)
3. **Funnel Analyzer:** Para optimización
4. **Enlaces Afiliados:** Configurar Amazon

**Libro propio:** Aún no disponible. Primero: terreno (blog + tráfico).

---

**Documento creado:** Marzo 2026  
**Basado en:** ai-marketing-claude (metodología, no código)  
**Próxima acción:** Implementar skills marketing

---

*"No copiamos. Extraemos principios y forjamos armas propias."*
