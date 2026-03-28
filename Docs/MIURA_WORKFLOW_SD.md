# ⚔️ MIURA FORGE - Workflow SDD (Spec-Driven Development)

> Adaptado de Gentleman AI para el pipeline de producción de contenido

---

## 📋 LAS 9 FASES DEL PIPELINE

### Fase 1: EXPLORE (Investigación)
**Objetivo:** Descubrir tendencias y dolor masculino en comunidades
**Herramienta:** `tools/weekly_oracle.py` / `core/researcher.py`

**Inputs:**
- Tema opcional o autodetección de tendencias
- Fuentes: Reddit, X, YouTube, Quora, Medium, Substack

**Outputs:**
- Tabla INVESTIGACION_PSICOLOGICA en Sheets
- Frases potentes extraídas
- Ranking de dolor (1-4)
- Fuentes con trazabilidad

**Observaciones clave a guardar:**
- ¿Qué comunidades tuvieron mayor engagement?
- ¿Qué tipo de dolor predomina esta semana?
- Frases virales detectadas
- Patrones de comportamiento masculino

**Validación antes de pasar:**
- [ ] ¿Se encontraron testimonios humanos válidos?
- [ ] ¿Hay al menos 5 fuentes de alta intensidad?
- [ ] ¿El dolor detectado es estructural (no superficial)?

---

### Fase 2: PROPOSE (Propuesta de Contenido)
**Objetivo:** Definir el enfoque narrativo y estratégico
**Herramienta:** `core/alchemist.py`

**Inputs:**
- Datos de investigación
- Contexto de hallazgos validados
- Memoria global (metáforas prohibidas)

**Outputs:**
- Estructura de 3 fases (Estabilidad → Inestabilidad → Reconfiguración)
- 30 títulos virales (6 plantillas × 5 variantes)
- Categoría temática
- Hooks estratégicos

**Decisiones a documentar:**
- ¿Por qué se eligió este ángulo narrativo?
- ¿Qué competencia se identificó?
- ¿Cuál es el gancho principal?
- ¿Qué se aprendió de investigaciones anteriores similares?

**Validación:**
- [ ] ¿Los títulos siguen la doctrina (no consuelan, revelan)?
- [ ] ¿Hay variedad en las plantillas usadas?
- [ ] ¿Se evitaron las metáforas de la memoria global?

---

### Fase 3: SPEC (Especificación del Guion)
**Objetivo:** Crear la estructura narrativa detallada
**Herramienta:** `core/architect.py`

**Inputs:**
- Propuesta aprobada
- Doctrina industrial (PDFs de referencia)
- Directivas de tono

**Outputs:**
- Guion MASTER completo
- Estructura de 3 fases detallada
- Puntos de inflexión marcados
- CTA (Call to Action) definido

**Especificaciones técnicas:**
- Duración objetivo: 50-60 segundos
- Palabras objetivo: 130-150 palabras
- Tono: "Inyección de Carbono" (bloqueo de verbos de duda)
- Jerarquía: 1 problema → 1 verdad → 1 acción

**Decisiones arquitectónicas:**
- ¿Qué metáfora se usará (nueva)?
- ¿Cuál es el momento de mayor impacto emocional?
- ¿Cómo se cierra el arco narrativo?

**Validación:**
- [ ] ¿El guion pasa la validación de verbos prohibidos?
- [ ] ¿Tiene la longitud correcta?
- [ ] ¿Sigue la estructura de 3 fases?
- [ ] ¿El CTA es accionable y concreto?

---

### Fase 4: DESIGN (Diseño Visual y Auditivo)
**Objetivo:** Crear los activos multimedia
**Herramientas:** 
- `core/visual_director.py` (prompts visuales)
- `tools/image_forge.py` (generación de imágenes)
- `core/voice_director.py` (síntesis de voz)

**Sub-fases:**

#### 4a. Visual Design
**Inputs:**
- Guion MASTER
- Tema y categoría

**Outputs:**
- Prompts duales para imágenes
- Directivas de animación
- Estilo cinematográfico definido

**Especificaciones visuales:**
- Ratio: 9:16 (752x1392px)
- Estilo: Cinematic, estoico, monocromático o metalizado
- Referencias: Blade Runner, Dune, arquitectura brutalista

#### 4b. Audio Design
**Inputs:**
- Guion MASTER aprobado

**Outputs:**
- Archivo .wav (Andrés - ElevenLabs)
- Velocidad: Normal o -10% para énfasis
- Post-procesado: Compresión ligera

**Validación:**
- [ ] ¿Los prompts visuales coinciden con el dolor estructural?
- [ ] ¿Las imágenes pasan el filtro de doctrina visual?
- [ ] ¿El audio tiene la duración correcta para el video?
- [ ] ¿La voz tiene el tono "Andrés" correcto?

---

### Fase 5: IMPLEMENT (Generación de Video)
**Objetivo:** Animar imágenes y ensamblar el video
**Herramientas:**
- `motion_forge/motion_forge_playwright.py` (Meta AI)
- `motion_forge/short_assembler.py` (MovieLite/FFMPEG)

**Sub-fases:**

#### 5a. Motion Generation (Meta AI)
**Inputs:**
- Imágenes generadas (clip_1.png, clip_2.png, etc.)
- Prompts de animación

**Outputs:**
- Clips MP4 animados (4-5 clips por video)
- Duración: 1.5s - 5s por clip

**Consideraciones técnicas:**
- Rotación de cuentas cada 4 clips
- Sistema de 3 capas de descarga
- Fallback a Replicate si Meta bloquea

#### 5b. Assembly (Ensamblaje)
**Inputs:**
- Clips MP4
- Audio .wav
- Configuración de subtítulos

**Outputs:**
- Video final .mp4 (9:16, 60s)
- Subtítulos estilo "Hormozi"
- Marca de agua ("SUSCRÍBETE")
- Outro (Final.mp4)

**Validación:**
- [ ] ¿El video tiene exactamente la duración del audio?
- [ ] ¿Los subtítulos están sincronizados?
- [ ] ¿La calidad visual es 1080x1920?
- [ ] ¿El zoom y pan están aplicados correctamente?

---

### Fase 6: VERIFY (Auditoría de Calidad)
**Objetivo:** Validar que el contenido cumple estándares Miura
**Herramientas:**
- `auditoria/miura_auditor_bunker.py`
- Validación manual del Soberano

**Criterios de validación:**

#### A. Doctrina (ADN)
- [ ] ¿No consuela ni humilla?
- [ ] ¿Revela, diagnostica y ordena?
- [ ] ¿Ataca el autoengaño, no al hombre?

#### B. Intensidad (0-10)
- [ ] ¿El problema está claramente definido?
- [ ] ¿La verdad es impactante pero constructiva?
- [ ] ¿La acción es física y concreta?

#### C. Ritmo
- [ ] ¿La estructura de 3 fases es clara?
- [ ] ¿Hay un punto de inflexión marcado?
- [ ] ¿El CTA es memorable?

#### D. Coherencia
- [ ] ¿El mensaje es consistente visual y auditivamente?
- [ ] ¿La metáfora se mantiene durante todo el video?

**Outputs:**
- Score de calidad (0-100)
- Observaciones de auditoría
- Registro en tabla AUDITORIA

**Si falla la auditoría:**
- Regresar a Fase 3 (SPEC) para reescritura
- O rechazar el contenido

---

### Fase 7: SEO (Metadatos YouTube)
**Objetivo:** Optimizar para algoritmo de YouTube
**Herramienta:** `tools/youtube_forge.py`

**Inputs:**
- Guion MASTER
- Tema y categoría
- Títulos virales generados

**Outputs:**
- Título optimizado (SEO + CTR)
- Descripción con timestamps
- Hashtags estratégicos
- Tags de video
- Miniatura sugerida

**Criterios SEO:**
- Título: Máximo 60 caracteres, hook fuerte
- Descripción: Primeras 150 caracteres visibles
- Hashtags: 3-5 relevantes, no saturar
- CTAs: Al principio y al final

**Validación:**
- [ ] ¿El título tiene palabras clave de búsqueda?
- [ ] ¿La descripción incluye timestamps?
- [ ] ¿Los hashtags son relevantes al nicho?

---

### Fase 8: DEPLOY (Publicación)
**Objetivo:** Subir a YouTube como borrador
**Herramienta:** `youtube_publisher/youtube_publisher.py`

**Inputs:**
- Video final .mp4
- Metadatos SEO
- Estado: PENDIENTE en tabla DESPLIEGUE

**Proceso:**
1. Filtrar videos marcados como PENDIENTE
2. Subir máximo 10 videos por sesión
3. Modo borrador (no público aún)
4. Mover MP4 a carpeta "Ya Publicado"
5. Actualizar estado a BORRADOR

**Consideraciones:**
- Delay entre uploads: 45-90 segundos
- User agent humanizado
- Anti-detection con Playwright Stealth

**Validación:**
- [ ] ¿El video subió correctamente?
- [ ] ¿Está en modo borrador?
- [ ] ¿Los metadatos se aplicaron bien?

---

### Fase 9: ARCHIVE (Documentación y Memoria)
**Objetivo:** Guardar lecciones aprendidas y actualizar memoria
**Herramientas:**
- Google Sheets (tabla MEMORIA)
- `core/memory_manager.py`

**Registros a guardar:**
1. **Metáforas usadas** (para evitar repetición)
2. **Decisiones tomadas** (¿por qué funcionó/no funcionó?)
3. **Bugs/Problemas encontrados**
4. **Métricas de performance** (si están disponibles)

**Formato de registro:**
```json
{
  "id_sesion": "PROD_20260325_1430",
  "tema": "procrastinacion_masculina",
  "metáfora_usada": "herrero_y_yunque",
  "dolor_principal": "falta_disciplina",
  "lecciones": [
    "El hook sobre 'mañana' funcionó mejor que el de 'nunca'",
    "Meta AI tuvo problemas con animación de fuego"
  ],
  "bugs": [
    "Replicate más estable que Meta para animaciones complejas"
  ],
  "decisiones": [
    "Se usó Sonet para SPEC en lugar de Gemini - mejor output"
  ],
  "fecha": "2026-03-25"
}
```

**Validación:**
- [ ] ¿Se guardaron las metáforas en MEMORIA?
- [ ] ¿Se documentaron las lecciones aprendidas?
- [ ] ¿La memoria está accesible para futuras sesiones?

---

## 🔄 FLUJO COMPLETO VISUAL

```
┌─────────────────────────────────────────────────────────────────┐
│                         FASE 1: EXPLORE                        │
│                    [Researcher + Weekly Oracle]                 │
│                    Detectar dolor en comunidades                │
└───────────────────────────┬─────────────────────────────────────┘
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                         FASE 2: PROPOSE                        │
│                         [Alchemist]                            │
│            Transformar dolor en estructura narrativa            │
└───────────────────────────┬─────────────────────────────────────┘
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                         FASE 3: SPEC                           │
│                         [Architect]                            │
│               Redactar guion completo (MASTER)                │
└───────────────────────────┬─────────────────────────────────────┘
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                         FASE 4: DESIGN                         │
│               [Visual Director + Voice Director]               │
│            Crear prompts visuales y audio (Andrés)            │
└───────────────────────────┬─────────────────────────────────────┘
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                        FASE 5: IMPLEMENT                       │
│           [Motion Forge + Short Assembler]                   │
│           Animar imágenes y ensamblar video final             │
└───────────────────────────┬─────────────────────────────────────┘
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                        FASE 6: VERIFY                          │
│                       [Auditor Bunker]                          │
│              Validar calidad doctrinal y técnica              │
└───────────────────────────┬─────────────────────────────────────┘
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                         FASE 7: SEO                            │
│                        [YouTube Forge]                          │
│             Generar títulos, descripciones, hashtags           │
└───────────────────────────┬─────────────────────────────────────┘
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                        FASE 8: DEPLOY                          │
│                     [YouTube Publisher]                        │
│              Subir a YouTube como borrador                     │
└───────────────────────────┬─────────────────────────────────────┘
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                       FASE 9: ARCHIVE                          │
│                     [Memory Manager]                           │
│           Guardar lecciones y actualizar memoria              │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📊 DOCUMENTACIÓN DE DECISIONES

### Template para Decisiones

**ID de Decisión:** `DEC_20260325_001`
**Fase:** SPEC
**Contexto:** 
**Opciones consideradas:**
1. Opción A
2. Opción B
**Decisión tomada:** Opción A
**Justificación:** 
**Consecuencias:**
- Positivas:
- Negativas:
**Fecha:** 2026-03-25
**Tomada por:** [Soberano / Sistema]

---

## 🎭 HUMAN-IN-THE-LOOP INTELIGENTE

### Puntos de Intervención Recomendados:

1. **POST-EXPLORE:** Aprobar tema antes de generar guiones
2. **POST-SPEC:** Revisar guion MASTER antes de generar visuales
3. **POST-VERIFY:** Aprobar video antes de generar SEO
4. **PRE-DEPLOY:** Aprobación final antes de subir

### Implementación Automática con Opción Humana:

```python
# En cada punto de decisión:
aprobacion = console.input(
    "\n[bold yellow]¿Aprobar y continuar?[/]\n"
    "[1] Aprobar automáticamente\n"
    "[2] Revisar manualmente\n"
    "[3] Modificar y reintentar\n"
    "[4] Abortar\n\n"
    "Soberano, dicte: "
)

if aprobacion == "1":
    # Modo automático - guardar decisión en MEMORIA
    db.guardar_decision(id_sesion, "auto_aprobado", fase_actual)
elif aprobacion == "2":
    # Mostrar para revisión
    mostrar_resultado_para_revision()
    input("Presiona ENTER cuando termines de revisar...")
```

---

## 💾 SISTEMA DE MEMORIA POR FASE

### Estructura de Memoria Global

**Tabla MEMORIA en Sheets:**
- `metáforas_usadas`: Lista de metáforas para evitar repetición
- `decisiones_clave`: JSON de decisiones importantes
- `bugs_conocidos`: Problemas técnicos y soluciones
- `lecciones_aprendidas`: Insights de cada sesión
- `tendencias_detectadas`: Temas recurrentes

### Retrieval Inteligente (inspirado en Engram)

1. **Capa 1 (Proyecto):** Buscar en metáforas específicas del proyecto actual
2. **Capa 2 (Tipo):** Buscar decisiones similares por tipo de contenido
3. **Capa 3 (Global):** Buscar en todo el historial si es necesario

---

## ⚡ OPTIMIZACIÓN DE TOKENS

### Estrategia Gentleman Adaptada:

1. **Subagentes por Fase:** Cada fase corre en un proceso separado
   - Ventaja: Cada uno tiene ventana de contexto limpia
   - Implementación: Usar `subprocess` para aislar cada fase

2. **Contexto Selectivo:** Solo pasar información necesaria
   - De EXPLORE → PROPOSE: Solo pasar hallazgos validados, no raw data
   - De SPEC → DESIGN: Solo pasar guion MASTER, no el proceso completo

3. **Skills de Contexto:** Cargar solo prompts necesarios
   - Ejemplo: Para "crear guion", cargar skill de "guion_base.txt"
   - No cargar skills de "youtube_seo.txt" hasta Fase 7

4. **Resumen Inteligente:** Antes de pasar a siguiente fase
   - Comprimir información manteniendo puntos clave
   - Usar LLM para crear "executive summary" entre fases

---

## 🚀 COMANDOS RÁPIDOS

```bash
# Ejecutar fase específica
python main.py --fase explore --tema "procrastinacion"
python main.py --fase spec --id PROD_20260325_1430
python main.py --fase implement --id PROD_20260325_1430

# Forja total (todas las fases automáticas)
python main.py --forja-total --auto-approve

# Ver workflow actual
python main.py --estado-workflow --id PROD_20260325_1430
```

---

**Versión:** 1.0  
**Última actualización:** Marzo 2026  
**Basado en:** SDD de Gentleman AI adaptado para Miura Forge
