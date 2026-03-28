# 🎭 SKILL REGISTRY - Miura Forge

> Biblioteca de patrones y skills reutilizables para el pipeline de producción

---

## 📋 ÍNDICE DE SKILLS

### SDD Skills (Workflow de Producción)
1. [SDD-EXPLORE: Investigación de Tendencias](#sdd-explore)
2. [SDD-PROPOSE: Propuesta de Contenido](#sdd-propose)
3. [SDD-SPEC: Redacción de Guiones](#sdd-spec)
4. [SDD-DESIGN: Creación de Assets](#sdd-design)
5. [SDD-IMPLEMENT: Generación de Video](#sdd-implement)
6. [SDD-VERIFY: Auditoría de Calidad](#sdd-verify)
7. [SDD-SEO: Optimización YouTube](#sdd-seo)
8. [SDD-DEPLOY: Publicación](#sdd-deploy)
9. [SDD-ARCHIVE: Memoria y Documentación](#sdd-archive)

### Foundation Skills
10. [AUDIT-GUION: Validación Doctrinal](#audit-guion)
11. [CRAFT-PROMPT: Creación de Prompts Visuales](#craft-prompt)
12. [META-AI: Uso de Meta AI para Animación](#meta-ai)
13. [YOUTUBE-SEO: Optimización de Metadatos](#youtube-seo)

---

## SDD-EXPLORE
**ID:** `sdd-explore`  
**Descripción:** Investigar tendencias y dolor masculino en comunidades  
**Cuándo usar:** Inicio de cada semana o cuando se necesita nuevo contenido

### Inputs
- Tema específico (opcional)
- Fuentes: Reddit, X, YouTube, Quora, Medium, Substack

### Outputs
- Tabla INVESTIGACION_PSICOLOGICA actualizada
- Hallazgos validados con score de intensidad
- Frases potentes para arsenal

### Prompt Template
```
Actúa como Investigador OSINT especializado en comunidades masculinas.
Tu objetivo: detectar el dolor REAL, no el superficial.

Busca en {plataforma} testimonios genuinos sobre {tema}.

CRITERIOS DE VALIDACIÓN:
1. ¿Es un testimonio personal real (no genérico)?
2. ¿Muestra vulnerabilidad genuina?
3. ¿Hay frases de alto impacto emocional?
4. ¿Identifica creencias limitantes?

FORMATO DE SALIDA:
- Dolor principal: [categoría]
- Problema raíz: [diagnóstico]
- Frases potentes: [lista]
- Creencias: [lista]
- Plataforma: {plataforma}
- URL: {url}
- Autor: {autor}
- Engagement: {métricas}

SCORE DE DOLOR (1-4): 
4 = Testimonio transformador con frases memorables
```

### Ejemplo de Uso
```bash
python main.py --fase explore --tema "procrastinacion"
python tools/weekly_oracle.py
```

---

## SDD-PROPOSE
**ID:** `sdd-propose`  
**Descripción:** Transformar dolor en estructura narrativa con 30 títulos  
**Cuándo usar:** Después de EXPLORE, antes de SPEC

### Inputs
- Datos de investigación validados
- Contexto de hallazgos
- Memoria global (metáforas prohibidas)

### Outputs
- Estructura de 3 fases
- 30 títulos virales
- Categoría temática
- Hooks estratégicos

### Prompt Template
```
Actúa como Alquimista de Contenido.
TRANSFORMA el dolor detectado en estructura viral.

CONTEXTO:
{hallazgos_validados}

METÁFORAS PROHIBIDAS (nunca usar):
{memoria_global.metáforas_usadas}

PROCESO:
1. Analiza el dolor estructural detectado
2. Identifica el autoengaño principal
3. Diseña 30 títulos usando estas plantillas:
   - Plantilla 1: "Si [acción], eres [diagnóstico]"
   - Plantilla 2: "La verdad que nadie te dice sobre [tema]"
   - Plantilla 3: "El momento en que [revelación]"
   - Plantilla 4: "Por qué [creencia común] es mentira"
   - Plantilla 5: "El precio de [evitar acción]"
   - Plantilla 6: "Lo que [figura de autoridad] no te dijo"

ESTRUCTURA DE 3 FASES:
- Fase 1 (Estabilidad): {diagnóstico del problema}
- Fase 2 (Inestabilidad): {revelación incómoda}
- Fase 3 (Reconfiguración): {acción concreta}

FORMATO JSON:
{
  "categoria": "string",
  "estructura_3fases": {
    "fase1": "string",
    "fase2": "string", 
    "fase3": "string"
  },
  "titulos_virales": {
    "plantilla1": ["string", "string", "string", "string", "string"],
    "plantilla2": [...],
    ...
  },
  "dolor_estructural": "string"
}
```

---

## SDD-SPEC
**ID:** `sdd-spec`  
**Descripción:** Redactar guion MASTER completo  
**Cuándo usar:** Después de PROPOSE, con propuesta aprobada

### Inputs
- Propuesta con estructura de 3 fases
- Doctrina industrial (referencias)
- Directivas de tono

### Outputs
- Guion MASTER (130-150 palabras)
- Metáfora seleccionada (nueva)
- Puntos de inflexión marcados
- CTA definido

### Constraints
- Duración: 50-60 segundos
- Palabras: 130-150
- Tono: "Inyección de Carbono" (bloqueo de dudas)
- Estructura: 1 problema → 1 verdad → 1 acción

### Prompt Template
```
Actúa como Andrés, la voz de Disciplina en Acero.

DOCTRINA (leyes inquebrantables):
1. NO consueles, NO humilles, NO dramatizes
2. REVELA el autoengaño, DIAGNOSTICA el problema, ORDENA la acción
3. Bloqueo absoluto de verbos de duda ("quizás", "podrías", "tal vez")
4. Actúa como prensa hidráulica: presión constante hacia la acción
5. Metáfora industrial: acero, forja, herrero, fragua

CONTEXTO:
- Tema: {tema}
- Dolor estructural: {dolor}
- Estructura 3 fases: {estructura}
- Metáfora a usar: {nueva_metáfora}

FORMATO DE GUION MASTER:
```
**FASE 1 - Estabilidad:**
[Diagnóstico quirúrgico del problema. 2-3 oraciones. Sin adornos.]

**FASE 2 - Inestabilidad:**
[Revelación incómoda. El momento de verdad. 2-3 oraciones. Impacto emocional.]

**FASE 3 - Reconfiguración:**
[La acción concreta. El camino. 2-3 oraciones. Imperativo absoluto.]

**CTA:**
[1 oración. Acción específica. Sin opciones.]
```

RESTRICCIONES:
- 130-150 palabras exactas
- 0 verbos de duda
- Metáfora {metáfora} en Fase 2
- CTA accionable y físico
- Tono: Autoridad calmada, no gritos

VALIDACIÓN ANTES DE ENTREGAR:
[ ] ¿Tiene verbos de duda? → Reescribir
[ ] ¿Consuela? → Reescribir
[ ] ¿Humilla? → Reescribir
[ ] ¿Es accionable el CTA? → Reescribir
```

---

## SDD-DESIGN
**ID:** `sdd-design`  
**Descripción:** Crear prompts visuales y audio  
**Cuándo usar:** Después de SPEC con guion aprobado

### Sub-skills
- **DESIGN-VISUAL:** Prompts para imágenes
- **DESIGN-AUDIO:** Síntesis de voz con Andrés

### Prompt Visual Template
```
Cinematographic prompt for image generation.

STYLE: {cinematic_style}
- Cinematic photography
- {color_palette}
- {lighting}
- Aspect ratio: 9:16 (752x1392)

SCENE DESCRIPTION:
{descripcion_basada_en_fase_del_guion}

REFERENCES:
- Blade Runner 2049
- Dune (2021)
- Industrial brutalist architecture
- Metallic textures
- Dramatic shadows

TECHNICAL:
- 8K resolution
- Photorealistic
- No text, no watermarks
- Sharp focus

ENHANCED PROMPT:
```

---

## SDD-IMPLEMENT
**ID:** `sdd-implement`  
**Descripción:** Generar video animado y ensamblar  
**Cuándo usar:** Después de DESIGN con assets listos

### Sub-fases
1. **MOTION:** Animar imágenes con Meta AI
2. **ASSEMBLY:** Unir clips, audio, subtítulos

### Consideraciones Técnicas
- Rotación de cuentas Meta AI cada 4 clips
- Sistema de 3 capas de descarga
- Fallback a Replicate

---

## SDD-VERIFY
**ID:** `sdd-verify`  
**Descripción:** Validar calidad doctrinal y técnica  
**Cuándo usar:** Después de IMPLEMENT

### Checklist de Validación
```
✓ DOCTRINA
  [ ] No consuela ni humilla
  [ ] Revela, diagnostica y ordena
  [ ] Ataca autoengaño, no persona

✓ INTENSIDAD (1-10)
  [ ] Problema claramente definido
  [ ] Verdad impactante y constructiva
  [ ] Acción física y concreta

✓ RITMO
  [ ] Estructura 3 fases visible
  [ ] Punto de inflexión marcado
  [ ] CTA memorable

✓ COHERENCIA
  [ ] Mensaje consistente visual/auditivo
  [ ] Metáfora mantenida

✓ TÉCNICO
  [ ] Duración exacta del audio
  [ ] Subtítulos sincronizados
  [ ] Calidad 1080x1920
```

---

## SDD-SEO
**ID:** `sdd-seo`  
**Descripción:** Optimizar metadatos YouTube  
**Cuándo usar:** Después de VERIFY

### Prompt Template
```
SEO Specialist for YouTube Shorts.

INPUT:
- Guion: {guion}
- Tema: {tema}
- Títulos generados: {titulos_30}

OUTPUTS:
1. Título optimizado (max 60 caracteres)
   - Hook emocional + keyword de búsqueda
   - Ejemplo: "Si procrastinas, eres cobarde | Disciplina en Acero"

2. Descripción (primera línea crucial)
   - Resumen con hook
   - Timestamps si aplica
   - Hashtags

3. Hashtags (3-5 relevantes)
   - #DisciplinaEnAcero
   - #[TemaPrincipal]
   - #[Nicho]
   - #[Motivación]
   - #[Masculinidad]

4. Tags del video
   - procrastinación masculina
   - disciplina vs motivación
   - desarrollo personal hombres
   - etc.

RESTRICCIONES:
- No clickbait excesivo
- Mantener integridad doctrinal
- Keywords de búsqueda reales
```

---

## SDD-DEPLOY
**ID:** `sdd-deploy`  
**Descripción:** Subir video a YouTube  
**Cuándo usar:** Después de SEO

### Consideraciones
- Delay entre uploads: 45-90 segundos
- Modo borrador (no público inmediato)
- Máximo 10 videos por sesión
- Anti-detection con Playwright

---

## SDD-ARCHIVE
**ID:** `sdd-archive`  
**Descripción:** Guardar lecciones en memoria global  
**Cuándo usar:** Después de DEPLOY

### Template de Registro
```json
{
  "id_sesion": "PROD_YYYYMMDD_HHMM",
  "tema": "nombre_tema",
  "fases_completadas": ["explore", "propose", "spec", "design", "implement", "verify", "seo", "deploy"],
  "metáfora_usada": "string",
  "titulo_seleccionado": "string",
  "score_auditoria": 0-100,
  "lecciones_aprendidas": [
    "Qué funcionó bien",
    "Qué se podría mejorar",
    "Decisiones importantes tomadas"
  ],
  "bugs_encontrados": [
    "Problemas técnicos y soluciones"
  ],
  "métricas": {
    "duracion_final": "00:00:52",
    "tokens_usados": 0,
    "costo_aproximado": 0.00
  },
  "proximos_pasos_sugeridos": [
    "Tema relacionado para próxima sesión"
  ]
}
```

---

## AUDIT-GUION
**ID:** `audit-guion`  
**Descripción:** Validación doctrinal de guiones

### Prompt
```
Auditor de Disciplina en Acero.

Valida el siguiente guion contra la doctrina:

DOCTRINA:
1. No consolar ni humillar
2. Revelar, diagnosticar, ordenar
3. Bloquear verbos de duda
4. Inyección de carbono (presión constante)
5. Acción física concreta

GUION A AUDITAR:
{guion}

ANALIZA:
- Verbosity score (0-100)
- Uso de verbos prohibidos
- Intensidad emocional
- Claridad del CTA
- Coherencia con Doctrina

OUTPUT:
{
  "aprobado": true/false,
  "score": 0-100,
  "problemas": ["lista"],
  "sugerencias": ["lista"],
  "fallas_doctrinales": ["lista"]
}
```

---

## CRAFT-PROMPT
**ID:** `craft-prompt`  
**Descripción:** Crear prompts cinematográficos

### Template Base
```
Cinematographic scene:

ELEMENTS:
- Subject: {sujeto_principal}
- Action: {accion}
- Environment: {entorno}
- Lighting: {iluminacion}
- Mood: {atmosfera}
- Style: {estilo_cinematografico}

TECHNICAL:
- 9:16 aspect ratio
- 8K photorealistic
- Film grain: subtle
- Color grading: {palette}

REFERENCES: {peliculas_referencia}

ENHANCED:
[Prompt completo generado]
```

---

## META-AI
**ID:** `meta-ai`  
**Descripción:** Uso optimizado de Meta AI para animación

### Mejores Prácticas
1. **Prompts de animación:**
   - "Slow zoom in, cinematic movement"
   - "Gentle parallax, professional"
   - "Atmospheric lighting change"
   
2. **Manejo de bloqueos:**
   - Rotar cuenta cada 4 clips
   - Esperar 20-40 segundos entre shorts
   - Usar force=True en clicks
   
3. **Fallback:**
   - Si Meta bloquea → usar Replicate
   - Minimax video-01: $0.04/video
   - LTX Video: $0.003/video

---

## YOUTUBE-SEO
**ID:** `youtube-seo`  
**Descripción:** Optimización completa para YouTube

### Checklist
```
ANTES DE SUBIR:
□ Título optimizado (hook + keyword)
□ Descripción con timestamps
□ 3-5 hashtags relevantes
□ Tags de video completados
□ Thumbnail sugerida (opcional)

CONFIGURACIÓN:
□ Privado (borrador) inicialmente
□ Permitir comentarios: Sí
□ Permitir reacciones: Sí
□ Categoría: Educación / Desarrollo Personal

METADATOS:
□ Idioma: Español
□ Grabación: Pantalla
□ Licencia: Standard YouTube
```

---

## 🔄 CÓMO USAR LOS SKILLS

### En Código Python
```python
from core.memory_manager import MemoryManager

# Cargar skill específico
skill = memory_manager.cargar_skill("sdd-spec")

# Aplicar template
prompt = skill.template.format(
    tema="procrastinacion",
    dolor="miedo al exito",
    estructura={...}
)
```

### En Prompts
```
/apply skill:sdd-spec
 tema: procrastinacion
 metáfora: herrero_y_yunque
```

---

## 📝 AÑADIR NUEVOS SKILLS

1. Crear archivo en `skills/{nombre}.md`
2. Seguir formato: ID, Descripción, Inputs, Outputs, Template
3. Registrar en este archivo
4. Actualizar skill registry: `python tools/update_skill_registry.py`

---

**Última actualización:** Marzo 2026  
**Versión:** 1.0  
**Total skills:** 13
