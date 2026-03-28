# ⚔️ SKILL REGISTRY - Miura Forge (SDD Edition)

> Biblioteca de skills organizadas por Fases SDD (Spec-Driven Development)
> **Versión:** 2.0 | **Estructura:** 9 Fases + Metadatos

---

## 📊 MAPA DE FASES SDD

```
FASE 1 (EXPLORE) → FASE 2 (PROPOSE) → FASE 3 (SPEC) → FASE 4 (DESIGN)
      ↓                  ↓                 ↓               ↓
   Investigación    Propuesta         Especificación    Diseño
   del dolor        de contenido      del guion         de assets

FASE 5 (IMPLEMENT) → FASE 6 (VERIFY) → FASE 7 (SEO) → FASE 8 (DEPLOY) → FASE 9 (ARCHIVE)
      ↓                   ↓               ↓              ↓                 ↓
   Generación        Auditoría         Optimización   Publicación       Memoria
   de video          de calidad        SEO            en YouTube        persistente
```

---

# ⚔️ FASE 1: EXPLORE (Investigación)

## SKILL-F1-001: `sdd-explore`

**Descripción:** Investigación OSINT de tendencias y dolor masculino en comunidades

**INPUTS:**
| Campo | Tipo | Requerido | Descripción |
|-------|------|-----------|-------------|
| tema | string | Opcional | Tema específico a investigar |
| fuentes | list | Opcional | Reddit, X, YouTube, Quora, Medium, Substack |
| profundidad | enum | Opcional | rapida (default) / exhaustiva |

**OUTPUTS:**
| Campo | Tipo | Descripción |
|-------|------|-------------|
| hallazgos | list[dict] | Testimonios validados con score de intensidad |
| frases_potentes | list | Frases memorables extraídas |
| dolor_principal | string | Categoría del dolor detectado |
| tabla_destino | string | INVESTIGACION_PSICOLOGICA (Sheets) |

**Invocación:**
```python
from tools.weekly_oracle import run_weekly_oracle
from core.researcher import Researcher

# Modo automático
run_weekly_oracle()

# Modo específico
researcher = Researcher()
hallazgos = researcher.buscar_dolor(tema="procrastinacion")
```

**Archivo:** `tools/weekly_oracle.py`, `core/researcher.py`

**Estado:** ✅ Implementado

---

# ⚔️ FASE 2: PROPOSE (Propuesta de Contenido)

## SKILL-F2-001: `sdd-propose`

**Descripción:** Transformar dolor investigado en estructura narrativa con 30 títulos virales

**INPUTS:**
| Campo | Tipo | Requerido | Descripción |
|-------|------|-----------|-------------|
| hallazgos_validados | list[dict] | Sí | Resultado de EXPLORE |
| tema | string | Sí | Tema central del contenido |
| metáforas_prohibidas | list | Sí | De memoria global (evitar repetición) |
| contexto | string | Sí | Texto consolidado de testimonios |

**OUTPUTS:**
| Campo | Tipo | Descripción |
|-------|------|-------------|
| categoria | string | Clasificación temática |
| estructura_3fases | dict | Fase1, Fase2, Fase3 definidas |
| titulos_virales | dict | 30 títulos (6 plantillas × 5 variantes) |
| dolor_estructural | string | Diagnóstico del problema raíz |
| gancho_principal | string | Hook emocional central |

**Invocación:**
```python
from core.alchemist import Alchemist
from core.database import Database

db = Database()
alchemist = Alchemist()
memoria_global = db.obtener_memoria_global()

plan = alchemist.transmutar_dolor(
    tema="procrastinacion",
    context=texto_consolidado,
    banned_metaphors=memoria_global
)
```

**Archivo:** `core/alchemist.py`

**Estado:** ✅ Implementado

---

# ⚔️ FASE 3: SPEC (Especificación)

## SKILL-F3-001: `sdd-spec`

**Descripción:** Redacción del guion MASTER completo siguiendo doctrina Disciplina en Acero

**INPUTS:**
| Campo | Tipo | Requerido | Descripción |
|-------|------|-----------|-------------|
| estructura_3fases | dict | Sí | De PROPOSE |
| tema | string | Sí | Tema del contenido |
| dolor | string | Sí | Dolor estructural detectado |
| metáfora | string | Sí | Metáfora industrial a usar |
| palabras_objetivo | int | No | 130-150 (default) |

**OUTPUTS:**
| Campo | Tipo | Descripción |
|-------|------|-------------|
| guion_master | string | Texto completo 3 fases + CTA |
| metáfora_usada | string | Metáfora seleccionada |
| puntos_inflexion | list | Momentos clave del guion |
| cta | string | Call to action definido |
| duracion_estimada | string | 50-60 segundos |

**Constraints:**
- Duración: 50-60 segundos
- Palabras: 130-150 exactas
- Tono: "Inyección de Carbono" (bloqueo verbos duda)
- Estructura: 1 problema → 1 verdad → 1 acción

**Invocación:**
```python
from core.architect import Architect

architect = Architect(db_manager=db)
guion = architect.redactar_guion_completo(
    tema_global=tema,
    timestamp=timestamp,
    data_estrategica=plan
)
```

**Archivo:** `core/architect.py`

**Estado:** ✅ Implementado

---

# ⚔️ FASE 4: DESIGN (Diseño)

## SKILL-F4-001: `sdd-design-visual`

**Descripción:** Creación de prompts visuales cinematográficos duales

**INPUTS:**
| Campo | Tipo | Requerido | Descripción |
|-------|------|-----------|-------------|
| guion_master | string | Sí | Texto completo del guion |
| tema | string | Sí | Tema del video |
| estilo | string | No | cinematic, industrial, estoico |
| ratio | string | No | 9:16 (default) |

**OUTPUTS:**
| Campo | Tipo | Descripción |
|-------|------|-------------|
| prompts_visuales | list[str] | 4-5 prompts para cada clip |
| estilo_definido | string | Paleta de colores y referencias |
| animaciones | list[str] | Directivas de movimiento |
| referencias_cinematograficas | list | Blade Runner, Dune, etc. |

**Invocación:**
```python
from core.visual_director import VisualDirector

director = VisualDirector(db_manager=db)
visual_ia = director.diseñar_estetica(guion_master, tema_global=tema)
```

**Archivo:** `core/visual_director.py`, `tools/mass_visual_forge.py`

**Estado:** ✅ Implementado

## SKILL-F4-002: `sdd-design-audio`

**Descripción:** Síntesis de voz con Andrés (ElevenLabs)

**INPUTS:**
| Campo | Tipo | Requerido | Descripción |
|-------|------|-----------|-------------|
| guion_master | string | Sí | Texto a vocalizar |
| timestamp | string | Sí | ID de sesión |
| velocidad | float | No | 1.0 (normal) / 0.9 (lento) |

**OUTPUTS:**
| Campo | Tipo | Descripción |
|-------|------|-------------|
| archivo_audio | string | Ruta al .wav generado |
| duracion | float | Segundos de audio |
| calidad | string | Configuración usada |

**Invocación:**
```python
from core.voice_director import VoiceDirector

andres = VoiceDirector()
andres.generar_voz(guion_master, archivo_salida)
```

**Archivo:** `core/voice_director.py`

**Estado:** ✅ Implementado

---

# ⚔️ FASE 5: IMPLEMENT (Implementación)

## SKILL-F5-001: `sdd-implement-motion`

**Descripción:** Animación de imágenes con Meta AI (Motion Forge)

**INPUTS:**
| Campo | Tipo | Requerido | Descripción |
|-------|------|-----------|-------------|
| imagenes | list[str] | Sí | Rutas a clip_1.png, clip_2.png... |
| prompts_animacion | list[str] | Sí | Directivas de movimiento |
| timestamp | string | Sí | ID de sesión |
| max_clips | int | No | 4 (rotación de cuentas) |

**OUTPUTS:**
| Campo | Tipo | Descripción |
|-------|------|-------------|
| clips_animados | list[str] | Rutas a .mp4 generados |
| duracion_total | float | Suma de duraciones |
| estado_proceso | dict | Log de rotación de cuentas |

**Consideraciones Técnicas:**
- Rotación de cuentas Meta AI cada 4 clips
- Sistema de 3 capas de descarga
- Fallback a Replicate si Meta bloquea

**Invocación:**
```python
from motion_forge.motion_forge_playwright import MotionForgePlaywright

mf = MotionForgePlaywright()
mf.procesar_cola()
```

**Archivo:** `motion_forge/motion_forge_playwright.py`

**Estado:** ✅ Implementado

## SKILL-F5-002: `sdd-implement-assembly`

**Descripción:** Ensamblaje final del video (clips + audio + subtítulos)

**INPUTS:**
| Campo | Tipo | Requerido | Descripción |
|-------|------|-----------|-------------|
| clips_mp4 | list[str] | Sí | Videos animados |
| audio_wav | string | Sí | Audio de voz |
| subtitulos | dict | Sí | Timestamps y texto |
| timestamp | string | Sí | ID de sesión |
| config | dict | No | Zoom, pan, marca de agua |

**OUTPUTS:**
| Campo | Tipo | Descripción |
|-------|------|-------------|
| video_final | string | Ruta al .mp4 final (1080x1920) |
| subtitulos_srt | string | Ruta al archivo .srt |
| duracion_final | float | Segundos exactos |
| calidad | string | 1080p 60fps |

**Invocación:**
```python
from motion_forge.short_assembler import modo_masivo

modo_masivo()
```

**Archivo:** `motion_forge/short_assembler.py`

**Estado:** ✅ Implementado

---

# ⚔️ FASE 6: VERIFY (Verificación)

## SKILL-F6-001: `sdd-verify`

**Descripción:** Auditoría de calidad doctrinal y técnica

**INPUTS:**
| Campo | Tipo | Requerido | Descripción |
|-------|------|-----------|-------------|
| guion_master | string | Sí | Guion a auditar |
| video_final | string | No | Path al video (opcional) |
| timestamp | string | Sí | ID de sesión |
| modo | enum | No | automatico / manual |

**OUTPUTS:**
| Campo | Tipo | Descripción |
|-------|------|-------------|
| score_doctrina | int | 0-100 puntos |
| score_tecnico | int | 0-100 puntos |
| aprobado | bool | Pasa/no pasa |
| problemas | list[str] | Lista de fallas encontradas |
| sugerencias | list[str] | Mejoras recomendadas |

**Checklist de Validación:**
- [ ] No consuela ni humilla
- [ ] Revela, diagnostica y ordena
- [ ] Ataca autoengaño, no persona
- [ ] Estructura 3 fases visible
- [ ] CTA memorable
- [ ] Sin verbos de duda

**Invocación:**
```python
# Automático
subprocess.run([sys.executable, "auditoria/miura_auditor_bunker.py", "--id", timestamp])

# Manual
from auditoria.miura_auditor_bunker import auditor_manual
resultado = auditor_manual(guion)
```

**Archivo:** `auditoria/miura_auditor_bunker.py`

**Estado:** ✅ Implementado

---

# ⚔️ FASE 7: SEO (Optimización)

## SKILL-F7-001: `sdd-seo`

**Descripción:** Generación de metadatos optimizados para YouTube

**INPUTS:**
| Campo | Tipo | Requerido | Descripción |
|-------|------|-----------|-------------|
| guion_master | string | Sí | Contenido del video |
| tema | string | Sí | Tema principal |
| titulos_30 | dict | Sí | De PROPOSE |
| timestamp | string | Sí | ID de sesión |

**OUTPUTS:**
| Campo | Tipo | Descripción |
|-------|------|-------------|
| titulo_final | string | Optimizado SEO + CTR (< 60 chars) |
| descripcion | string | Con timestamps y CTAs |
| hashtags | list[str] | 3-5 hashtags estratégicos |
| tags | list[str] | Tags de video completos |
| thumbnail_sugerencia | string | Prompt para miniatura |

**Criterios SEO:**
- Título: Hook + keyword + marca
- Descripción: Primera línea crucial (hook)
- Hashtags: Relevantes, no saturar
- CTAs: Al principio y final

**Invocación:**
```python
from tools.youtube_forge import modo_masivo, leer_doctrina_youtube, get_brain

doctrina = leer_doctrina_youtube()
brain = get_brain()
modo_masivo(brain, doctrina, target_id=timestamp)
```

**Archivo:** `tools/youtube_forge.py`

**Estado:** ✅ Implementado

---

# ⚔️ FASE 8: DEPLOY (Despliegue)

## SKILL-F8-001: `sdd-deploy`

**Descripción:** Publicación de video en YouTube como borrador

**INPUTS:**
| Campo | Tipo | Requerido | Descripción |
|-------|------|-----------|-------------|
| video_final | string | Sí | Ruta al .mp4 |
| metadatos | dict | Sí | Título, descripción, tags, hashtags |
| timestamp | string | Sí | ID de sesión |
| max_uploads | int | No | 10 (default) |

**OUTPUTS:**
| Campo | Tipo | Descripción |
|-------|------|-------------|
| video_id | string | ID de YouTube (si exitoso) |
| estado | string | BORRADOR / ERROR |
| url_borrador | string | URL del video en Studio |
| log_proceso | dict | Detalles del upload |

**Consideraciones:**
- Delay entre uploads: 45-90 segundos
- Modo borrador (no público inmediato)
- Anti-detection con Playwright Stealth
- Máximo 10 videos por sesión

**Invocación:**
```python
import subprocess
subprocess.run([sys.executable, "youtube_publisher/youtube_publisher.py", "--max", "10"])
```

**Archivo:** `youtube_publisher/youtube_publisher.py`

**Estado:** ✅ Implementado

---

# ⚔️ FASE 9: ARCHIVE (Archivo)

## SKILL-F9-001: `sdd-archive`

**Descripción:** Persistencia de lecciones y actualización de memoria global

**INPUTS:**
| Campo | Tipo | Requerido | Descripción |
|-------|------|-----------|-------------|
| id_sesion | string | Sí | ID timestamp de la sesión |
| fases_completadas | list | Sí | Qué fases se ejecutaron |
| metadatos | dict | Sí | Título, metáfora, score, etc. |

**OUTPUTS:**
| Campo | Tipo | Descripción |
|-------|------|-------------|
| memoria_actualizada | bool | Éxito de la operación |
| tabla_memoria | string | Tabla MEMORIA en Sheets |
| lecciones_guardadas | int | Cantidad de lecciones |

**Registros a Guardar:**
- Metáforas usadas (evitar repetición)
- Decisiones clave tomadas
- Bugs encontrados y soluciones
- Métricas de performance

**Invocación:**
```python
from core.memory_manager import MemoryManager

memoria = MemoryManager()
memoria.archivar_sesion(id_sesion, datos)
```

**Archivo:** `core/memory_manager.py`

**Estado:** ⚠️ Parcialmente implementado

---

# 🛠️ FOUNDATION SKILLS (Transversales)

## SKILL-X-001: `audit-guion`

**INPUTS:** Guion, Modo  
**OUTPUTS:** Score, problemas, sugerencias  
**Archivo:** Auditor en cada fase

## SKILL-X-002: `craft-prompt`

**INPUTS:** Elementos visuales, estilo  
**OUTPUTS:** Prompt cinematográfico mejorado  
**Archivo:** Usado en FASE 4

## SKILL-X-003: `meta-ai-handler`

**INPUTS:** Imágenes, prompts animación  
**OUTPUTS:** Clips MP4  
**Archivo:** `motion_forge/motion_forge_playwright.py`

## SKILL-X-004: `youtube-seo-refiner`

**INPUTS:** Metadatos brutos  
**OUTPUTS:** Metadatos optimizados  
**Archivo:** `tools/youtube_forge.py`

---

# 🔄 FLUJO DE INVOCACIÓN (Orquestador)

```python
# main.py - Modo Orquestador SDD

def workflow_sdd(opcion_fase):
    """Ejecuta una fase específica del pipeline SDD."""
    
    db = Database(spreadsheet_name="BD_MiuraForge_Engine")
    
    if opcion_fase == "1":  # EXPLORE
        skill = cargar_skill("sdd-explore")
        return skill.ejecutar(tema=input("Tema: "))
    
    elif opcion_fase == "2":  # PROPOSE
        skill = cargar_skill("sdd-propose")
        hallazgos = db.obtener_ultimos_hallazgos()
        return skill.ejecutar(hallazgos=hallazgos)
    
    elif opcion_fase == "3":  # SPEC
        skill = cargar_skill("sdd-spec")
        propuesta = db.obtener_ultima_propuesta()
        return skill.ejecutar(propuesta=propuesta)
    
    # ... continúa para cada fase

# Menú Orquestador:
# 1. EXPLORE - Investigación
# 2. PROPOSE - Propuesta de contenido
# 3. SPEC - Especificación del guion
# 4. DESIGN - Diseño de assets
# 5. IMPLEMENT - Generación de video
# 6. VERIFY - Auditoría de calidad
# 7. SEO - Optimización
# 8. DEPLOY - Publicación
# 9. ARCHIVE - Memoria
# 10. FORJA TOTAL - Pipeline completo
```

---

# 📊 RESUMEN DE IMPLEMENTACIÓN

| Fase | Estado | Archivos Principales |
|------|--------|---------------------|
| EXPLORE | ✅ | `core/researcher.py`, `tools/weekly_oracle.py` |
| PROPOSE | ✅ | `core/alchemist.py` |
| SPEC | ✅ | `core/architect.py` |
| DESIGN | ✅ | `core/visual_director.py`, `core/voice_director.py` |
| IMPLEMENT | ✅ | `motion_forge/motion_forge_playwright.py`, `motion_forge/short_assembler.py` |
| VERIFY | ✅ | `auditoria/miura_auditor_bunker.py` |
| SEO | ✅ | `tools/youtube_forge.py` |
| DEPLOY | ✅ | `youtube_publisher/youtube_publisher.py` |
| ARCHIVE | ⚠️ | `core/memory_manager.py` (parcial) |

---

**Versión:** 2.0 - SDD Edition  
**Última actualización:** Marzo 2026  
**Total Skills:** 9 Fases + 4 Foundation  
**Integrado con:** main.py (Orquestador)
