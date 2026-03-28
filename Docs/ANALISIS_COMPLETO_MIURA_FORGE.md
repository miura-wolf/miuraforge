# ⚔️ ANÁLISIS COMPLETO: MIURA FORGE ENGINE

**Fecha:** 2026-03-20
**Versión:** 2.2.0
**Autor:** Antigravity AI
**Estado:** Documentación Actualizada (Fase Replicate + Triple Motor)

---

## 📊 ÍNDICE EJECUTIVO

1. [Arquitectura General](#arquitectura-general)
2. [Árbol de Directorios](#árbol-de-directorios)
3. [Módulos Principales](#módulos-principales)
4. [Flujo de Trabajo](#flujo-de-trabajo)
5. [Sistema de IA y Resiliencia](#sistema-de-ia-y-resiliencia)
6. [Base de Datos (Google Sheets)](#base-de-datos-google-sheets)
7. [Scripts de Mantenimiento](#scripts-de-mantenimiento)
8. [Doctrina y Configuración](#doctrina-y-configuración)
9. [Puntos de Entrada](#puntos-de-entrada)
10. [Tecnologías y Dependencias](#tecnologías-y-dependencias)

---

## 🏗️ ARQUITECTURA GENERAL

Miura Forge Engine es un **ecosistema avanzado de inteligencia artificial** diseñado para la creación automatizada de contenido de alto impacto para YouTube Shorts, operando bajo la filosofía de **"Disciplina en Acero"**.

### Filosofía Central
- **No humilla, no consuela, no dramatiza**
- **Revela, Diagnostica y Ordena**
- Ataca la mentira interna (autoengaño) del hombre para reconstruir su responsabilidad mediante acciones físicas concretas

### Patrón Arquitectónico
Sistema modular con **arquitectura en capas** y **resiliencia multi-tier**:
```
┌─────────────────────────────────────────────┐
│           Control Central (main.py)          │
├─────────────────────────────────────────────┤
│   Módulos de Generación (Core)              │
│   ├── Researcher (OSINT)                    │
│   ├── Alchemist (Transmutación)             │
│   ├── Architect (Redacción)                 │
│   ├── VisualDirector (Cine)                 │
│   └── VoiceDirector (Audio)                 │
├─────────────────────────────────────────────┤
│   Sistema de IA (Factory + Providers)       │
│   ├── NVIDIA/DeepSeek (Tier 1)              │
│   ├── Replicate/Flux (Tier 2 - Económico)   │
│   ├── Nebius/Flux (Tier 3 - Respaldo)       │
│   └── Gemini (Tier 4 - Multimodal)          │
├─────────────────────────────────────────────┤
│   Persistencia (Google Sheets)              │
│   └── Database (13 tablas)                  │
├─────────────────────────────────────────────┤
│   Herramientas (Tools/Utils)                │
│   └── Emisario (Email Automation)          │
└─────────────────────────────────────────────┘
```

---

## 📁 ÁRBOL DE DIRECTORIOS

```
MiuraForge/
├── .env                              # Variables de entorno (NO en git)
├── .gitignore                        # Exclusiones Git
├── README.md                         # Documentación principal
├── DOCUMENTACION_MAESTRA.md          # Códice de Guerra (arquitectura detallada)
├── main.py                           # ⚙️ PUNTO DE ENTRADA PRINCIPAL
├── weekly_oracle.py                  # 🔮 Oráculo Semanal (planificación automática)
├── analizar_libro.py                 # 📖 Extractor de ADN doctrinal de PDFs
├── visual_lab.py                     # 🎨 Laboratorio de experimentación visual
├── test_groq_simple.py               # 🧪 Test de Groq Compound
│
├── core/                             # 🧠 NÚCLEO DEL SISTEMA
│   ├── __pycache__/
│   ├── researcher.py                # Radar OSINT + Validación Psicológica
│   ├── alchemist.py                 # Transmutación de dolor → estructura 3 fases
│   ├── architect.py                 # Redacción de guiones (Andrés)
│   ├── visual_director.py           # Generación de prompts cinematográficos
│   ├── voice_director.py            # Síntesis de voz (ElevenLabs)
│   ├── database.py                  # Puente de Mando (Google Sheets)
│   ├── clusterizador.py             # Agrupación de dolores (Directiva 1)
│   ├── tendencias.py                # Radar de tendencias (Directiva 2)
│   ├── extractor_frases.py          # Arsenal de frases virales (Directiva 3)
│   ├── logger.py                    # Sistema de logging dual (terminal + archivo)
│   ├── doctrina_industrial.json     # Glosario: palabras prohibidas/permitidas
│   ├── doctrina_industrial.txt      # Formato lista (duplicado)
│   ├── doctrina_prohibida.json      # Lista de palabras veto
│   └── doctrina_prohibida.txt       # Formato lista
│
├── llm/                              # 🧠 SISTEMA DE IA MULTI-PROVEEDOR
│   ├── __pycache__/
│   ├── factory.py                   # Factory Pattern + ResilientProvider
│   ├── providers.py                 # Implementaciones: Gemini, NVIDIA, Groq
│   └── memory_manager.py            # Memoria global de metáforas ( Sheets + local)
│
├── tools/                            # 🛠️ HERRAMIENTAS DE PRODUCCIÓN Y MANTENIMIENTO
│   ├── image_forge.py               # 🖼️ MOTOR DE IMAGEN TRIPLE (NVIDIA/Rep/Neb)
│   ├── mass_visual_forge.py          # ⚔️ GENERADOR DE PROMPTS DUALES (Sheets)
│   ├── apertura_full_forge.py       # 🚀 Workflow de videos de apertura
│   ├── inspeccionar_imperio.py      # Auditoría de estructura de Sheets
│   └── alinear_imperio.py           # Restauración de cabeceras
│
├── utils/                            # 📦 UTILIDADES
│   └── excel_inspector.py           # Inspección de Excel (legacy?)
│
├── deployer/                         # 🚀 DESPLIEGUE
│   └── miura_deployer.py            # Generador de metadata para publicación
│
├── emisario/                         # 📧 AUTOMATIZACIÓN DE EMAIL
│   ├── emissary.py                  # Motor principal (3 secuencias)
│   ├── emissary1.py                 # Variante (experimental?)
│   ├── emissary2.py                 # Variante (experimental?)
│   └── emissary3.py                 # Variante (experimental?)
│
├── prompts/                          # 📋 INSTRUCCIONES PARA LLMs
│   ├── arquitecto.txt               # Prompt: Andrés redacta guiones
│   ├── alquimia.txt                 # Prompt: Alquimista transmuta dolor
│   ├── visual.txt                   # Prompt: Director Visual (estética industrial)
│   ├── deployer.txt                 # Prompt: Estratega de metadata
│   ├── auditoria.txt                # Prompt: Auditor optimiza guiones
│   ├── purificador.txt              # ¿Filtro de contenido?
│   ├── dolores_loader.py            # Carga de dolores a Sheets
│   ├── ganchos_loader.py            # Carga de ganchos a Sheets
│   ├── territorio_loader.py         # Carga de territorios doctrinales
│   └── libro1_adn.txt               # ADN doctrinal extraído del libro (JSON)
│
├── doctrina/                         # 📚 LIBROS Y SABIDURÍA
│   ├── libro1_adn.txt               # ADN doctrinal del "Hombre que Dejó de Mentirse"
│   ├── FUNDAMENTO.pdf               # PDFFundación de la doctrina
│   ├── PARALISIS.pdf                # PDF Análisis de parálisis masculina
│   └── ESTRATEGIA.pdf               # PDF Estrategia de intervención
│
├── knowledge/                        # 🗃️ CONOCIMIENTO EXTERNO (¿PDFs adicionales?)
│
├── Libro/                           # 📦 ALMACÉN DE LIBROS (respaldos)
│
├── output/                          # 📤 RESULTADOS Y LOGS
│   ├── logs/                        # Registros de combate (logs del sistema)
│   ├── sesion_YYYYMMDD_HHMM/        # Sesiones individuales organizadas
│   │   ├── registro_combate.log     # Log completo de la sesión
│   │   ├── fase_1_completa.txt      # Guion Fase 1
│   │   ├── fase_2_completa.txt      # Guion Fase 2
│   │   ├── fase_3_completa.txt      # Guion Fase 3
│   │   ├── YYYYMMDD_HHMM_MASTER.txt # Guion MASTER aprobado
│   │   ├── YYYYMMDD_HHMM_MASTER_voz.mp3  # Audio generado
│   │   ├── fase_X_voz.mp3           # Audio por fase
│   │   └── prompts_img/             # Prompts visuales generados
│   ├── ENTREGA_YYYYMMDD_HHMM/       # Paquetes listos para editor
│   │   ├── INFO_ENTREGA.txt         # Metadatos de entrega
│   │   ├── YYYYMMDD_HHMM_MASTER.txt
│   │   └── YYYYMMDD_HHMM_MASTER_voz.mp3
│   ├── DEPLOY_YYYYMMDD_HHMM/        # Metadata de despliegue (YouTube/TikTok)
│   │   └── metadata_despliegue.json
│   ├── LAB_VISUAL_*.txt             # Experimentos del Visual Lab
│   ├── prompts_img/                 # (¿quizás respaldo de prompts?)
│   └── scripts/ scripts0/          # (posibles logs de ejecución)
│
├──disciplinaenacero/                 # 🌐 SITIO WEB (Netlify)
│   ├── netlify.toml
│   ├── README_DEPLOY.md
│   ├── css/
│   ├── js/
│   └── pages/
│
├── knowledge/                        # (duplicado? ya apareció arriba)
│
├── merch/                           # 🎁 PRODUCTOS FÍSICOS (¿diseños?)
│
├── tmp/                             # 🗑️ Temporales
│
├── venv/                            # 🐍 Entorno virtual Python (NO en git)
├── credentials.json                 # Google Service Account (NO en git)
├── client_secrets.json              # OAuth credentials (NO en git)
├── .env.example o env.txt           # Plantilla de variables de entorno
└── requirements.txt                 # Dependencias Python (68 paquetes)
```

---

## 🧩 MÓDULOS PRINCIPALES

### 1. RESEARCHER (core/researcher.py)

**Responsabilidad:** Inteligencia OSINT + Validación Psicológica

**Funciones clave:**
- `buscar_dolor(tema)` → Pipeline completo OSINT
- `buscar_fuentes_web(tema)` → Tavily + Queries inteligentes (Reddit, X, Quora, Medium/Substack)
- `buscar_youtube_dolor(tema)` → YouTube API (comentarios de videos)
- `analizar_psicologia(texto)` → LLM valida testimonios reales y extrae:
  - `problema_principal`
  - `emociones`, `creencias`, `síntomas`
  - `frases_potentes` (keywords: "I feel", "no puedo", "odio", etc.)
  - `nivel_dolor` (1-4)
  - `solucion_miura` (recomendación táctica)
  - `engagement_estimado` (1-1000)
- `clasificar_dolor(analisis)` → Mapeo a 12 Dolores Estructurales:
  1. Propósito perdido
  2. Falta disciplina
  3. Dopamina (adicciones)
  4. Soledad estructural
  5. Relaciones tóxicas
  6. Identidad perdida
  7. Vergüenza/fracaso
  8. Inestabilidad económica
  9. Vacío espiritual
  10. Falta de respeto
  11. Miedo al futuro
  12. Parálisis por análisis
- `detectar_pulso_semanal()` → Oráculo: escanea tendencias semanales
- `extraer_ganchos_virales(url)` → Ingeniería competitiva (extrae título, hook, plantilla, intensidad)

**API Keys utilizadas:**
- `TAVILY_API_KEY` (búsqueda web)
- `YOUTUBE_API_KEY` (comentarios)
- LLM via LLMFactory (Tier 1-3)

**Resiliencia:** `@retry` de tenacity (3 intentos, backoff exponencial)

---

### 2. ALCHEMIST (core/alchemist.py)

**Responsabilidad:** Transmutar dolor en estructura de 3 fases + 30 títulos virales

**Entradas:**
- `tema_investigacion` (string)
- `context` (testimonios reales concatenados)
- `banned_metaphors` (metáforas recientes, de memoria global)

**Proceso:**
1. Carga doctrina desde `prompts/alquimia.txt`
2. Inyecta **Glosario Doctrinal** (ley de lenguaje Miura):
   - Prohibido: palabras suaves ("sanar", "compartir", "vibrar")
   - Obligatorio: lenguaje industrial ("forjar", "quemar", "engranaje", "motor", "combustión")
3. Llama a Gemini (model: `ACTIVE_MODEL` del .env)
4. Espera JSON estructurado:
```json
{
  "categoria": "Falta de propósito",
  "fases": [
    {"fase": 1, "titulo": "Estabilidad: Rompe la mentira", "dolor_accion": "...", "frase_impacto": "..."},
    {"fase": 2, "titulo": "Inestabilidad: El golpe del martillo", "dolor_accion": "...", "frase_impacto": "..."},
    {"fase": 3, "titulo": "Reconfiguración: El nuevo orden", "dolor_accion": "...", "frase_impacto": "..."}
  ],
  "titulos_virales": {
    "VERDAD_INCOMODa": ["...", "..."],
    "REVELACION": [...],
    "CONFESION": [...],
    "ERROR_CRITICO": [...],
    "DESPERTAR": [...],
    "TRAMPA": [...]
  }
}
```

**Métodos:**
- `generar_ideas_backlog(insight)` → 10 títulos por insight (modo backlog)

---

### 3. ARCHITECT (core/architect.py)

**Responsabilidad:** Forjar el **GUION MASTER** completo en una sola transacción

**Brain:** NVIDIA DeepSeek o GPT-OSS (asignado por factory para arquitecto)

**Fuentes de Inteligencia:**
1. CSV base: `Investigacion.csv` (columnas: "Eje Temático", "Frase Representativa", "Por qué Paraliza", etc.)
2. Sheets reciente: `INVESTIGACION_PSICOLOGICA`
3. Doctrina: 3 PDFs (`FUNDAMENTO.pdf`, `PARALISIS.pdf`, `ESTRATEGIA.pdf`)
4. ADN: `doctrina/libro1_adn.txt`
5. Prompt base: `prompts/arquitecto.txt` (tono Andrés)

**Prompt final:**
```
{instrucciones_andres}

--- ADN DOCTRINAL (LIBRO 1) ---
{adn_doctrinal}

TEMA PRINCIPAL: {tema_global}
{contexto_real}
{data_estrategica}

REGLA DE ORO: Genera el guion completo (Fase 1, 2 y 3) de forma percusiva.
No repitas la misma metáfora en todas las fases. Evoluciona el golpe.
Límite total: 150 palabras.
```

**Estructura Obligatoria (Arquitecto):**
```
FASE 1 — EL GOLPE
Rompe una creencia errónea.
Máximo 40 palabras. Prohibido dar órdenes.

FASE 2 — EL MARTILLO
Explica el mecanismo mental.
Máximo 50 palabras.

FASE 3 — EL NUEVO ORDEN
Solo órdenes físicas ejecutables.
Verbos permitidos: Escribe, Bloquea, Ejecuta, Corta, Calcula, Mide, Construye.
Máximo 50 palabras.
```

**Salida:**
- Guarda en `PRODUCCION` (Sheets) como `MASTER`, estado `pendiente`
- Espera aprobación humana (S=aprobar, N=rechazar/reforjar, E=editar manualmente, A=auditar)
- Si se aprueba → genera prompt visual + opcionalmente despliegue

**Metáforas:** Extrae 3 metáforas clave del guion y las envía a `MEMORIA` (local + Sheets)

---

### 4. VISUAL DIRECTOR (core/visual_director.py)

**Brain:** NVIDIA DeepSeek / Gemini (vía LLMFactory)

**Sistema Triple Motor de Imagen (Integrado en image_forge.py):**
La generación de clips ya no depende de un solo proveedor, sino de una cascada inteligente para maximizar ahorro y calidad:
1.  **NVIDIA (Flux 2 Klein):** Nuestra primera línea. Rápida y **Gratuita**.
2.  **Nebius (Flux Dev/Schnell):** Segunda línea. Usa saldo actual para **Calidad Premium**.
3.  **Replicate (Flux Schnell):** Tercera línea/Reserva. **Ultra-Económica** ($0.003/img) y resiliente.

**Cálculo dinámico:**
- `duracion = palabras / 155 (ppm)`
- `num_clips = max(6, round(duracion / 6))`

**Caché Avanzada:** `output/visual_cache.json` (hash MD5 para evitar pagar dos veces por el mismo guion).

**Estética base (`prompts/visual.txt`):**
- Paleta: Negro (#0A0A0A), Carbón (#111111), Acero (#2A2A2A), Dorado Miura (#C8A96E), Rojo Forja (#8B1A1A)
- Texturas: metal, polvo, óxido, humo sutil
- Movimientos de cámara:
  - Fase 1 (20%): Slow dolly-in
  - Fase 2 (60%): Orbit shot, cinematic realistic
  - Fase 3 (20%): Tracking shot, handheld, motion blur

**Prohibiciones:**
- No usar colores fuera de paleta
- No "warrior silhouette", "lone wolf", "motivational sunset"
- No adjetivos vacíos: "epic", "cinematic", "masterpiece" (pero sí descriptores técnicos)
- No rostros humanos como foco

**Salida:** Exactamente `num_clips` prompts en inglés, cada uno con:
```
Scene: (Realistic industrial scene)
Camera Movement: (...)
Lighting: (...)
Texture: (...)
Composition: (...)
Atmosphere: (...)
Lens/Perspective: (...)
```

---

### 5. VOICE DIRECTOR (core/voice_director.py)

**Responsabilidad:** Síntesis de voz "Andrés" (ElevenLabs)

**Config:**
- `ELEVENLABS_API_KEY`
- `VOICE_ID` (voice ID específico)
- URL: `https://api.elevenlabs.io/v1/text-to-speech/{voice_id}`

**Voice Settings:**
```json
{
  "stability": 0.6,
  "similarity_boost": 0.8,
  "style": 0.0,
  "use_speaker_boost": true
}
```

**Modelo:** `eleven_multilingual_v2` (español latam)

**Resiliencia:** `@retry` (3 intentos)

**Salida:** `.mp3` en carpeta `output/sesion_{timestamp}/`

---

### 6. DATABASE (core/database.py)

**Responsabilidad:** **Puente de Mando** → Google Sheets

**Autenticación:** Service Account → `credentials.json` (json keyfile)

**Scope:** Spreadsheets + Drive API

**Tablas gestionadas (13):**

| Tabla | Propósito | Columnas (estructura sagrada) |
|-------|-----------|------------------------------|
| **LOGISTICA** | Seguimiento de sesiones | ID_Sesion, Tema, Fecha, Estado, Métricas |
| **PRODUCCION** | Guiones por fase | ID_Sesion, Fase, Guion, Prompt_Visual, Voz_Status, Estado |
| **MEMORIA** | Metáforas prohibidas | Metafora |
| **AUDITORIA** | Control calidad | ID_Master, Guion_Original, Guion_Optimizado, Intensidad, Ritmo, Coherencia, ADN, Fallas, Ajustes, Fecha |
| **FUENTES** | Trazabilidad OSINT | ID, ID_SESION, PLATAFORMA, ORIGEN, URL, AUTOR, ENGAGEMENT, FECHA, QUERY, FECHA_EXTRACCION |
| **INVESTIGACION_PSICOLOGICA** | Análisis profundo | ID_SEMANA, TEMA, DOLOR_PRINCIPAL, PROBLEMA_RAIZ, FRASES_POTENTES, CREENCIAS, SOLUCION_MIURA, PLATAFORMA, FECHA |
| **DOLORES_MASCULINOS** | Radar de frecuencia | ID_DOLOR, CATEGORIA, DESCRIPCION, CREENCIAS, VERDAD, INTENSIDAD, FRECUENCIA, EJEMPLO |
| **ARSENAL_GANCHOS** | Hooks de competencia | GANCHO, PLANTILLA, INTENSIDAD, ID_SESION, FECHA |
| **CLUSTERS_DOLOR** | Agrupación inteligente | cluster_id, nombre_cluster, frecuencia, temas_relacionados, frase_dominante, ultima_actualizacion, freq_7d, freq_30d, tendencia_estado |
| **FRASES_VIRALES** | Arsenal de frases | id_frase, frase, dolor_asociado, plataforma, tema |
| **DESPLIEGUE** | Metadata de publicación | ID_MASTER, TITULO_GOLPE, SUBTITULO_REFUERZO, DESCRIPCION_ACERO, HASHTAGS_TACTICOS, GANCHO_VISUAL_0_3, CTA_PRINCIPAL, TERRITORIO_DOCTRINAL, HORA_LANZAMIENTO, ESTADO_DESPLIEGUE |
| **LEADS** (solo Emisario) | Email marketing | NOMBRE, EMAIL, MOTIVACION, DOLOR, ESTADO, FECHA |
| **CONTENIDO_PUBLICADO** (solo Emisario) | Alertas de video | TITULO, URL_YOUTUBE, DESCRIPCION, ESTADO, EMAIL_ENVIADO |

**Escudo de Estructura (Fase IMP):**
- `_activar_escudo_estructura()` → verifica/crea TODAS las tablas necesarias al conectar
- Si falta una columna → la restaura automáticamente
- Evita que el usuario rompa la estructura

**Métodos principales:**
- `registrar_hallazgos()` → FUENTES
- `registrar_investigacion_psicológica()` → INVESTIGACION_PSICOLOGICA
- `actualizar_dolor()` → DOLORES_MASCULINOS (incrementa contador)
- `registrar_ganchos()` → ARSENAL_GANCHOS
- `guardar_fase()` → PRODUCCION (upsert inteligente)
- `obtener_*()` → Recuperación con detección flexible de columnas
- `registrar_auditoria_inicial()` + `actualizar_resultados_auditoria()`
- ` agregar_a_memoria_global()` → MEMORIA (append fila)

**Resiliencia:** `@retry` (3 intentos, backoff exponencial)

**Cache:** `urls_cache` en FUENTES para evitar duplicados por URL

---

### 7. CLUSTERIZADOR (core/clusterizador.py)

**Directiva 1:** Agrupación de insights por dolor principal

**Input:** `INVESTIGACION_PSICOLOGICA` → todos los registros

**Proceso:**
1. Agrupa por `DOLOR_PRINCIPAL` (lowercase)
2. Para cada cluster:
   - `frecuencia` (count)
   - `frases` (top 2 frases potentes por registro)
   - `temas` (set de TEMA)
3. Calcula métricas temporales:
   - `freq_7d` (última semana)
   - `freq_30d` (último mes)
   - `ratio = freq_7d / (freq_30d / 4)` (normalizado a 4 semanas)
   - `tendencia`:
     - `🔥 EMERGENTE` si ratio ≥ 3
     - `📈 CRECIENDO` si ratio ≥ 1.5
     - `➡️ ESTABLE` en otro caso
4. **Sobrescribe** CLUSTERS_DOLOR completo (clear + append)

**Output:** Tabla CLUSTERS_DOLOR (usable por `seleccionar_inteligencia_sheets()` en main.py)

---

### 8. RADAR TENDENCIA (core/tendencias.py)

**Directiva 2:** Detección de dolores emergentes (ya está integrado en Clusterizador, pero separado para futuras extensiones)

**Cálculo idéntico al Clusterizador** pero actualiza solo columnas `freq_7d`, `freq_30d`, `tendencia_estado` en CLUSTERS_DOLOR.

---

### 9. EXTRACTOR FRASES (core/extractor_frases.py)

**Directiva 3:** Arsenal de frases virales

**Input:** `INVESTIGACION_PSICOLOGICA` → columna `FRASES_POTENTES` (separadas por `|`)

**Filtro de calidad:**
- Longitud 3-15 palabras
- `frases_detectadas` → lista de dicts: `{frase, dolor, tema, plataforma}`

**Output:** Tabla `FRASES_VIRALES` (top 50 frases, overwrite completo)
- `id_frase`, `frase`, `dolor_asociado`, `plataforma`, `tema`

---

### 10. ORÁCULO SEMANAL (weekly_oracle.py)

**Responsabilidad:** Planificación autónoma semanal (cada Domingo)

**Pipeline:**
1. `researcher.detectar_pulso_semanal()` → 3 tendencias (queries + razones)
2. Para cada tendencia:
   - `buscar_dolor(query_profunda)` → hallazgos + validación
   - `registrar_hallazgos()` + `registrar_investigacion_psicológica()`
   - `researcher.extraer_ganchos_virales()` (top 2 fuentes) → `ARSENAL_GANCHOS`
   - `actualizar_dolor()` → radar de frecuencia
3. Post-proceso:
   - `ClusterizadorDolores.clusterizar_dolores()`
   - `RadarTendencia.calcular_tendencias()`
   - `ExtractorFrases.extraer_frases_memorables()`

**ID de sesión:** `SEMANA_YYYYWW` (año + número de semana ISO)

**Resultado:** Backlog de 90 días alimentado + Arsenal actualizado

---

## 🔄 FLUJO DE TRABAJO

### Modo 1: Investigación (Flujo Completo)

```
┌──────────────────────────────────────────────────────────┐
│  USUARIO: python main.py → Opción 1 ó 3                  │
└─────────────────────┬────────────────────────────────────┘
                      │
                      ▼
          ┌─────────────────────┐
          │  RESEARCHER         │
          │  buscar_dolor(tema) │
          └─────────┬───────────┘
                    │
       ┌────────────┴────────────────┐
       ▼                             ▼
   Tavily                     YouTube API
   (20 fuentes max)           (3 videos × 3 comentarios)
       │                             │
       └────────────┬────────────────┘
                    ▼
          ┌─────────────────────┐
          │  analizar_psicologia│
          │  (validación LLM)   │ ← Filtro: solo testimonios reales
          └─────────┬───────────┘
                    │
                    ▼
          ┌─────────────────────┐
          │  clasificar_dolor   │ → 12 categorías
          └─────────┬───────────┘
                    │
                    ▼
          ┌─────────────────────┐
          │  DATABASE           │
          │  registrar_hallazgos│ → FUENTES
          │  registrar_inv_psic│ → INVESTIGACION_PSICOLOGICA
          │  actualizar_dolor   │ → DOLORES_MASCULINOS
          └─────────┬───────────┘
                    │
                    ▼
          ┌─────────────────────┐
          │  Clusterizador      │ → CLUSTERS_DOLOR
          │  RadarTendencia     │ → actualiza tendencias
          │  ExtractorFrases    │ → FRASES_VIRALES
          └─────────┬───────────┘
                    │
                    ▼
          ┌─────────────────────┐
          │  ALCHEMIST          │
          │  transmutar_dolor() │ → JSON: {categoria, fases, titulos_virales}
          └─────────┬───────────┘
                    │
                    ▼
          ┌─────────────────────┐
          │  registrar_ganchos()│ → ARSENAL_GANCHOS
          │  registrar_sesion() │ → LOGISTICA
          └─────────┬───────────┘
                    │
                    ▼
          ✅  INVESTIGACIÓN COMPLETADA
          ID_Sesion generado (timestamp)
```

**Output:** Carpeta `output/sesion_{timestamp}/` con `registro_combate.log`

---

### Modo 2: Redacción (Flujo 2)

```
┌──────────────────────────────────────────────────────────┐
│  USUARIO: python main.py → Opción 2                       │
│  (o automático si vino de Opción 3)                      │
└─────────────────────┬────────────────────────────────────┘
                      │
                      ▼
          ┌─────────────────────┐
          │  ARCHITECT           │
          │  redactar_guion()   │
          └─────────┬───────────┘
                    │
       ┌────────────┴───────────────────────────┐
       ▼                                         ▼
   Cargar inteligencia                     Cargar doctrina:
   - CSVInvestigacion.csv                   - 3 PDFs (FUNDAMENTO, PARALISIS, ESTRATEGIA)
   - Sheets reciente                        - ADN (libro1_adn.txt)
   - prompts/arquitecto.txt                 ← Tono Andrés
                    │
                    ▼
          ┌─────────────────────┐
          │  LLM (NVIDIA)       │
          │  Contexto + Prompt  │ → Guion MASTER (≤150 palabras)
          └─────────┬───────────┘
                    │
                    ▼
          ┌─────────────────────┐
          │  guardar_fase()     │ → PRODUCCION (MASTER, estado=pendiente)
          │  _aprender_metáforas│ → MEMORIA (local + Sheets)
          └─────────┬───────────┘
                    │
                    ▼
          ┌─────────────────────┐
          │  CONTROL HUMANO:     │
          │  - S: Aprobar       │ → Visual + Voz
          │  - N: Rechazar      │ → Reforjar (repetir)
          │  - E: Editar manual│ → modificar PRODUCCION
          │  - A: Auditor       │ → ejecuta auditoria/miura_auditor_bunker.py
          └─────────┬───────────┘
                    │
                    ▼
          Si aprobado → Visual Director → Voice Director → Empaquetar
```

**Edición manual:** Abre archivo temporal `output/temp/EDIT_{timestamp}.txt` con app nativa del SO

---

### Modo 3: Voice Only

`flujo_voz(timestamp)` → Recupera MASTER aprobado o fases 1-3 de Sheets → genera MP3s

---

## 🤖 SISTEMA DE IA Y RESILIENCIA

### LLMFactory (llm/factory.py)

**Patrón Factory + Chain of Responsibility**

```python
LLMFactory.get_brain(task_name) → ResilientProvider(tiers=[...])
```

**Asignación por tarea:**

| Tarea | Provider | Modelo | Misión |
|-------|----------|--------|--------|
| `research` | ResilientProvider | Tier1: NVIDIA DeepSeek-V3 → Tier2: Gemini → Tier3: Groq | OSINT + validación psicológica |
| `pdf_reader` | GeminiProvider | ACTIVE_MODEL | Leer PDFs doctrinales |
| `architect` | NvidiaProvider | mistral-large-3 | Redacción de guiones |
| `visual` | ResilientProvider | NVIDIA DeepSeek-V3 / Gemini | Prompts cinematográficos |
| `image_gen` | image_forge | NVIDIA / Replicate / Nebius | Generación de WebP/PNG |

### Providers (llm/providers.py)

#### 1. GeminiProvider
- **API:** `google-genai`
- **Keys:** Lee `GEMINI_API_KEY` de `.env` (soporta múltiples keys = forja infinita)
- **Rotación:** `_rotate_key()` ante error 429 → rota entre 10 keys automáticamente
- **Retry:** 12 intentos (suficiente para rotar todas las llaves)
- **Contexto:** Soporta subida de archivos (PDFs) → `client.files.upload()`

#### 2. NvidiaProvider
- **API:** OpenAI-compatible endpoint
- **URL:** `https://integrate.api.nvidia.com/v1/chat/completions`
- **Key:** `OPENAI_API_KEY` (NVIDIA)
- **Modelos:**
  - `deepseek-ai/deepseek-v3.1` (investigación)
  - `openai/gpt-oss-20b` (arquitecto)
  - `openai/gpt-oss-120b` (deployer)
- **Parámetros soportados:** `temperature`, `frequency_penalty`, `top_p`, `reasoning_effort`

#### 3. GroqProvider
- **API:** `groq` SDK
- **Compound Mode:** `tools: ["web_search", "code_interpreter", "visit_website"]`
- **Keys:** `GROQ_API_KEY` (múltiples keys soportadas)
- **Uso principal:** Investigación profunda con búsqueda web integrada (no requiere Tavily)

#### 4. ResilientProvider
- **Lógica:** Itera secuencialmente por tiers hasta éxito
- **Filtro errores:** Solo hace fallover en errores de cuota (429, quota, exhausted, limit, rate_limit)
- **Si error no-cuota:** lanza excepción inmediatamente (no enmascara bugs)

### MemoryManager (llm/memory_manager.py)

**Doble fuente de memoria:**
1. Local: `output/metaphor_memory.json` → `recent_metaphors[]`
2. Global (Sheets): `MEMORIA` → `obtener_memoria_global()`

**Función:** Prevenir repetición de metáforas en guiones consecutivos

**Update:** `update_metaphors(new_metaphors)` → local + Sheets (append)

---

## 📊 GOOGLE SHEETS: EL PUENTE DE MANDO

### Conexión
- **Service Account:** `credentials.json` (no va en git)
- **Scope:** Spreadsheets + Drive
- **Spreadsheet ID:** `BD_MiuraForge_Engine` (hardcoded? o configurable)

### Escudo de Estructura (Database._activar_escudo_estructura)

**Mapa maestro** (columns顺序 fijo):
```python
{
  "LOGISTICA": ["ID_Sesion", "Tema", "Fecha", "Estado", "Metricas"],
  "PRODUCCION": ["ID_Sesion", "Fase", "Guion", "Prompt_Visual", "Voz_Status", "Estado"],
  "MEMORIA": ["Metafora"],
  "AUDITORIA": ["ID_Master", "Guion_Original", "Guion_Optimizado", "Intensidad", "Ritmo", "Coherencia", "ADN", "Fallas", "Ajustes", "Fecha"],
  "FUENTES": ["ID", "ID_SESION", "PLATAFORMA", "ORIGEN", "URL", "AUTOR", "ENGAGEMENT", "FECHA", "QUERY", "FECHA_EXTRACCION"],
  "INVESTIGACION_PSICOLOGICA": ["ID_SEMANA", "TEMA", "DOLOR_PRINCIPAL", "PROBLEMA_RAIZ", "FRASES_POTENTES", "CREENCIAS", "SOLUCION_MIURA", "PLATAFORMA", "FECHA"],
  "DOLORES_MASCULINOS": ["ID_DOLOR", "CATEGORIA", "DESCRIPCION", "CREENCIAS", "VERDAD", "INTENSIDAD", "FRECUENCIA", "EJEMPLO"],
  "ARSENAL_GANCHOS": ["GANCHO", "PLANTILLA", "INTENSIDAD", "ID_SESION", "FECHA"],
  "CLUSTERS_DOLOR": ["cluster_id", "nombre_cluster", "frecuencia", "temas_relacionados", "frase_dominante", "ultima_actualizacion", "freq_7d", "freq_30d", "tendencia_estado"],
  "FRASES_VIRALES": ["id_frase", "frase", "dolor_asociado", "plataforma", "tema"],
  "DESPLIEGUE": ["ID_MASTER", "TITULO_GOLPE", "SUBTITULO_REFUERZO", "DESCRIPCION_ACERO", "HASHTAGS_TACTICOS", "GANCHO_VISUAL_0_3", "CTA_PRINCIPAL", "TERRITORIO_DOCTRINAL", "HORA_LANZAMIENTO", "ESTADO_DESPLIEGUE"]
}
```

**Al conectarse:**
- Si tabla NO existe → la crea con headers correctos
- Si tabla existe pero headers ≠ esperados → la reemplaza (⚠️ borra datos!)
- Excepto tablas con datos (FUENTES, INVESTIGACION) → solo reemplaza si headers vacíos o inconsistentes

**Panel de control:** `inspeccionar_imperio.py` muestra estado de salud

---

## 🔧 SCRIPTS DE MANTENIMIENTO

### `tools/inspeccionar_imperio.py`

**Uso:** `python tools/inspeccionar_imperio.py`

**Output:** Tabla Rich con:
- Tabla (hoja)
- Headers detectados
- Estado: ✅ ÓPTIMA o ⚠️ CRÍTICA (faltantes)

### `tools/alinear_imperio.py`

**Uso:** `python tools/alinear_imperio.py`

**Acción:** Restaura headers de todas las tablas al mapa maestro (sobrescribe fila 1)

---

## 📜 DOCTRINA Y CONFIGURACIÓN

### Prompts (Directivas de Comportamiento)

**`arquitecto.txt`** → Andrés (tono, estructura 3 fases, prohibiciones)
**`alquimia.txt`** → Alquimista (clasificación, transmutación)
**`visual.txt`** → Visual Director (paleta, movimientos, formato)
**`deployer.txt`** → Estratega metadata (títulos, gancho, descripción, hashtags)
**`auditoria.txt`** → Auditor (criterios de calidad, optimización)

### Doctrina Industrial (core/doctrina_industrial.json)

**Palabras OBLIGATORIAS** (metáforas mecánicas):
`acero, forja, óxido, motor, combustión, martillo, estructura, fricción, presión, hidráulico, pistón, aceite, caldera, temple, fragua, yunque, torsión, soldadura, carburante, chasis, engranaje, biela, cigüeñal, prensa, soplete, metal, aleación`

**Glosario Prohibido:**
(implícito en el prompt, no en JSON)

**Uso:** Inyectado en prompt del Alquimist para transformar lenguaje emocional → lenguaje industrial

---

## 🚀 PUNTOS DE ENTRADA

### 1. `main.py` (Control Central)

**Menú:**
```
1) INICIAR INVESTIGACIÓN (Explorador + Alquimia)
2) REDACTAR GUIONES (Pausa Táctica en Sheets)
3) FLUJO COMPLETO (De la Idea al Archivo Final)
4) SOLO VOZ (Generar MP3 desde Sesión)
5) FORJA MASIVA (Del Backlog al Guion Auditado)
6) MOTOR DE PROMPTS DUALES (Visual + Animación)
7) MOTOR DE IMÁGENES (NVIDIA + Replicate + Nebius)
8) SALIR
```

**Funciones:**
- `mostrar_menu()` → Rich table
- `flujo_investigacion()` → modo 1 + opción backlog (200 ideas) o estándar (30 ganchos)
- `flujo_redaccion()` → modo 2 + selector inteligente desde CLUSTERS_DOLOR
- `main()` → loop infinito + logger dual

**Logging:** `iniciar_registro_combate(ruta)` → `CombatLogger` (escribe en terminal + `registro_combate.log`)

### 2. `weekly_oracle.py`

**Uso:** `python weekly_oracle.py` (cada Domingo)

**Output:** Backlog poblado, clusters generados

### 3. `analizar_libro.py`

**Uso:** `python analizar_libro.py`

**Input:** PDF `Libro/ElHombreQueDejoDeMentirse_v2.pdf`

**Output:** `doctrina/libro1_adn.txt` (JSON con dolores maestros, frases de acero, metáforas visuales)

### 4. `visual_lab.py`

**Laboratorio independiente** para experimentar con estilos visuales

**Modos de entrada:**
1. Pegar texto manual
2. Cargar desde .txt
3. Cargar desde Google Sheets (últimos MASTERs)

**Estilos:**
0. Industrial Base
1. Cyberpunk Industrial
2. Cinematic Noir
3. Abstracto/Simbólico
4. Letras de Canción
5. Personalizado

**Output:** Prompt generado + opción guardar en `output/LAB_VISUAL_*.txt`

### 5. `deployer/miura_deployer.py`

**Uso:** `python deployer/miura_deployer.py --id TIMESTAMP` o `--file ruta.txt`

**Función:** Generar paquete de metadata para publicar en YouTube/TikTok

**Output:**
- Consola: títulos, gancho, descripción, hashtags, CTA, territorio
- Sheets: `DESPLIEGUE` (append)
- JSON: `output/DEPLOY_{id}/metadata_despliegue.json`

### 6. `emisario/emissary.py`

**Sistema de email marketing automatizado (Brevo API)**

**Secuencias:**

#### BIENVENIDA (3 correos)
- Día 1: Entrega del Fundamento
- Día 3: Verificación de temperatura (¿bloqueaste notificaciones?)
- Día 7: Diagnóstico completo (El Hombre que Dejó de Mentirse)

#### ALERTA_VIDEO
-当 video marcado `PUBLICADO` en `CONTENIDO_PUBLICADO` y `EMAIL_ENVIADO != SI`
- Envía a todos los leads activos
- Marca `EMAIL_ENVIADO = SI`

#### LANZAMIENTO (3 fases)
- Fase 1 (Lunes): "Precio $9, la semana que viene $17"
- Fase 2 (Jueves): Presión ("El lunes sube a $17")
- Fase 3 (Domingo): Última llamada ("Hoy medianoche")

**Personalización IA:**
- Prioridad: NVIDIA NIM (openai/gpt-oss-120b)
- Fallback: Gemini
- Una frase personalizada por lead (basada en `MOTIVACION`)

**Límite diario:** `LIMITE_DIARIO_EMAILS` (default 30, calentamiento de dominio)

**Tablas Sheets requeridas:**
- `LEADS`: NOMBRE, EMAIL, MOTIVACION, DOLOR, ESTADO, FECHA
- `CONTENIDO_PUBLICADO`: TITULO, URL_YOUTUBE, DESCRIPCION, ESTADO, EMAIL_ENVIADO

---

## 📦 TECNOLOGÍAS Y DEPENDENCIAS

### Core Packages

| Paquete | Versión | Uso |
|---------|---------|-----|
| `google-genai` | 1.65.0 | Gemini API (oficial) |
| `google-generativeai` | 0.8.6 | Gemini legacy (¿dual?) |
| `gspread` | 6.2.1 | Google Sheets |
| `oauth2client` | 4.1.3 | Auth Service Account |
| `tavily-python` | 0.7.22 | OSINT web search |
| `groq` | 0.18.0 | Groq Compound (web search + visit) |
| `openai` | 2.24.0 | NVIDIA NIM (OpenAI-compatible) |
| `requests` | 2.32.5 | HTTP genérico |
| `pandas` | 3.0.1 | CSV + análisis |
| `tenacity` | 9.1.4 | Retry exponencial |
| `rich` | 14.3.3 | Terminal UI (tablas, paneles, progreso) |
| `python-dotenv` | 1.2.1 | Variables de entorno |
| `numpy` | 2.4.2 | Cálculos vectoriales (¿dónde?) |

### Proveedores Externos

| Servicio | API Key | Uso en el sistema |
|----------|---------|-------------------|
| Google Gemini | `GEMINI_API_KEY` (×10 keys) | Tier 1: Research, PDF reading |
| NVIDIA NIM | `OPENAI_API_KEY` | Tier 2: Architect, Visual, Deployer, Emisario (personalización) |
| Groq | `GROQ_API_KEY` | Tier 3: Research (Compound con web search) |
| Tavily | `TAVILY_API_KEY` | Research: búsqueda web OSINT |
| YouTube Data v3 | `YOUTUBE_API_KEY` | Research: comentarios |
| ElevenLabs | `ELEVENLABS_API_KEY` + `VOICE_ID` | Voice Director |
| Brevo (Sendinblue) | `BREVO_API_KEY` | Emisario: email transactional |
| Google Sheets | `credentials.json` | Database: persistencia |

---

## 📁 ARCHIVOS DE CONFIGURACIÓN

### `.env` (NO en git)

**Variables típicas:**
```bash
# Gemini (10 keys soportadas, separadas por ; o líneas)
GEMINI_API_KEY=AIzaSy...1
# (otras 9 líneas GEMINI_API_KEY=...)

ACTIVE_MODEL=gemini-2.0-flash  # o gemini-1.5-pro

# NVIDIA (OpenAI-compatible)
OPENAI_API_KEY=nvapi-...
OPENAI_BASE_URL=https://integrate.api.nvidia.com/v1
OPENAI_MODEL=openai/gpt-oss-20b  # o deepseek-ai/deepseek-v3.1

# Groq
GROQ_API_KEY=gsk_...

# Tavily
TAVILY_API_KEY=tvly-...

# YouTube
YOUTUBE_API_KEY=AIzaSy...

# ElevenLabs
ELEVENLABS_API_KEY=...
VOICE_ID=21m00Tcm4TlvDq8ikWAM

# Brevo (email)
BREVO_API_KEY=xsmtp-...

# Google Sheets (opcional si credentials.json tiene scope)
GOOGLE_SHEETS_ID=1aBcD...  # ID del spreadsheet
GOOGLE_CREDENTIALS_PATH=credentials.json

# Limites
LIMITE_DIARIO_EMAILS=30
```

### `credentials.json` (Service Account)

- **Project ID:** miura-forge
- **Email service account:** miura-forge@appspot.gserviceaccount.com
- **Sheets compartido** con este email (Editor)

---

## 🔍 ANÁLISIS DE FLUJOS ESPECÍFICOS

### Pipeline OSINT → Validación → Clasificación

**Researcher.buscar_dolor(tema):**
1. `generar_queries_inteligentes(tema)` → 4 queries (Reddit, X, Quora, Blogs)
2. Para cada query:
   - `tavily.search(search_depth="advanced", max_results=5)` → 20 resultados max
   - Filtro idioma `_es_contenido_hispanohablante()`:
     - Blacklist de subreddits no hispanos
     - Ratio de palabras no-hispano > 0.12 → descartar
   - `extraer_autor_desde_url()` → autor legible (limpia dominios)
3. `analizar_psicologia(h['content'])` para cada fuente:
   - LLM evalúa si es testimonio REAL (no spam, no moda, no entretenimiento)
   - Extrae JSON con 10 campos
   - Si falla `json.loads` → busca primer `{.*}` con regex
4. `clasificar_dolor(analisis)` → mapeo por keywords a 12 Dolores Estructurales
5. `extraer_frases_potentes()` → heurística: palabras clave en frases

**Resultado:** `hallazgos_validados` (lista de dicts enriquecidos)

### Transmutación → Redacción Single-Transaction

**Ventaja arquitectónica:** No se genera guion por fases separadas (1, 2, 3) que después hay que fusionar. Se genera **TODO en una sola llamada LLM** → mayor coherencia, ritmo percusivo, metáforas no repetidas.

**Prompt:** 1000+ tokens (doctrina + ADN + contexto OSINT + instrucciones)

**Temperatura:** 0.3 (baja = consistencia)

**Top_p:** 0.9 (diversidad controlada)

---

## 🎵 ESPECIAL: EL HOMBRE QUE DEJÓ DE MENTIRSE (ADN DOCTRINAL)

**Libro:** "El Hombre que Dejó de Mentirse" → `doctrina/libro1_adn.txt` (JSON)

**4 Dolores Maestros:**

| Dolor | Síntoma | Mecanismo | Secuencia Interrupción |
|-------|---------|-----------|----------------------|
| **El Silencio que te Está Matando** | Ruido de fondo permanente, irritabilidad, explosiones, entumecimiento | Creencia: "un hombre fuerte calla" → represión (no procesamiento) | **Acción física como lenguaje**: movimiento, tareas concretas. El cuerpo no miente. |
| **La Máscara que Construiste** | Proyección falsa, sensación de impostor, vergüenza interna | Adaptación: "mostrarte real es peligroso" → ausencia de modelo auténtico | **Construcción de identidad mediante actos repetidos** coherentes con valores. La identidad sigue a la ejecución. |
| **El Vacío no es Depresión** | Anhedonia, "presente sin estar", parálisis por análisis | Sin arquitectura de vida → dopamina secuestrada por scroll/notificaciones | **Instalar dirección**: 1 cosa concreta, 20 min/día, registrar ejecución (no resultado). |
| **El Precio de Ser el Proveedor Invisible** | Fracaso total a pesar de cumplir, soledad del pilar, responsabilidad como condena | Fusión: "valor = producción" → adaptación hedónica, estereotipos | **Responsabilidad como elección** (no condena). Separar valor propio de producción. |

**Frases de Acero (ejemplos):**
- "Callar no es fortaleza. Es deuda diferida."
- "El cuerpo no miente. Cuando el cerebro no puede procesar, el cuerpo lo hace por él."
- "El propósito no se encuentra. Se construye."
- "La identidad sigue a la ejecución. No al revés."

**Metáforas visuales recurrentes:**
- Yunque / Forja / Acero
- Máscara / Caricatura
- Edificio / Cimientos
- Mapa / Brújula
- Pared de cristal
- Pilar
- Tren / Vías
- Deuda / Factura

---

## 🔐 SEGURIDAD Y MEJORES PRÁCTICAS

1. **Nunca commit `credentials.json` ni `.env`** → `.gitignore` los excluye
2. **Service Account** → solo acceso a Sheets, no Drive completo
3. **Límites de API** → tenacity + rotación automática Gemini (10 keys)
4. **Cache visual** → `visual_cache.json` ahorra 1-2 créditos por batch
5. **Filtro de idioma** → researcher descarta no-hispanos
6. **Escudo de estructura** → evita corrupción de cabeceras
7. **URL cache** → evita duplicados en FUENTES
8. **Auditoría** → guarda `Guion_Original` + `Guion_Optimizado` en tabla separada

---

## ⚠️ PUNTOS DE MEJORA / DEUDAS TÉCNICAS

1. **Datos de producción** → TODO el sistema depende de Google Sheets (SPOF)
2. **Error handling** genérico → `except Exception as e: print()` sin cascadear
3. **Hardcodeados**: spreadsheet_name="BD_MiuraForge_Engine" en Database()
4. **Resiliencia inconsistente**: Alchemist no tiene retry (solo GeminiProvider lo implementa)
5. **Naming**: researcher1.py, researcher2.py, researcher3.py, emissary1-3.py → ¿versiones experimentales?
6. **Database.get_all_records()** → puede cargar toda la hoja en memoria (riesgo con >10k filas)
7. **Logger** → `sys.stdout = logger` global → puede romper otros módulos si se anida
8. **CLUSTERS_DOLOR overwrite** → cada clusterización borra datos anteriores (¿histórico?)
9. **Visual Director cache** → hash MD5, pero no limpia cache viejo (puede crecer indefinidamente)
10. **Backlog mode** → genera 10 ideas por insight, pero ¿dónde se usan? Solo registra en Sheets

---

## 📈 ESCALABILIDAD Y FUTURO

### Escala Horizontal Potencial

- **Research** → paralelizable por tema (cada tema = researcher.buscar_dolor())
- **Alquimia** → stateless, puede batch procesar múltiples insights
- **Architect** → único bottleneck (una sesión a la vez)
- **Visual + Voice** → stateless, cache ayuda

### Posibles Mejoras

1. **Base de datos vectorial** para búsqueda semántica de frases (reemplazar `INVESTIGACION_PSICOLOGICA` como CSV)
2. **Workqueue** (Redis/Celery) para procesar múltiples sesiones en paralelo
3. **API REST** (FastAPI) para exponer como servicio
4. **Webhooks** automáticos (Oráculo → Slack/Telegram)
5. **Dashboard** (Streamlit/Gradio) para operar sin CLI
6. **Tests unitarios** (pytest) → 0 tests actuales
7. **CI/CD** → GitHub Actions para lint + test + deploy automático de emisario
8. **Dockerización** → imagen oficial del motor
9. **Monitoring** → métricas (Prometheus) + alertas (cuotas API)
10. **Multi-tenant** → soporte para múltiples marcas/doctrinas

---

## 🎯 CONCLUSIÓN

Miura Forge Engine es un **sistema de producción de contenido de alto rendimiento** con:

✅ **Arquitectura modular** desacoplada (core, llm, tools)
✅ **Resiliencia multi-tier** (Gemini → NVIDIA → Groq)
✅ **Inteligencia contextual** (OSINT + validación psicológica + clusters)
✅ **Doctrina injection** en cada capa (alquimia, arquitecto, visual)
✅ **Persistencia soberana** (Google Sheets como single source of truth)
✅ **Escudo de datos** (estructura blindada contra corrupción)
✅ **Cache inteligente** (visual, memoria de metáforas)
✅ **Automatización completa** (Oráculo semanal, Emisario)
✅ **Flujo humano en el loop** (aprobación Soberana en cada MASTER)

**Debilidades principales:**
- Dependencia monolítica de Google Sheets (sin fallback local)
- Falta de tests y CI/CD
- Hardcodeados y duplicación (researcher1-3, emissary1-3)
- Logging global puede ser frágil

**Oportunidades:**
- Migrar a PostgreSQL + pgvector para búsqueda semántica
- Implementar cola de tareas (Redis) para batch processing
- Exponer API REST para integraciones externas
- Dashboard web para operación sin terminal

---

**"El acero no se oxida con orgullo; se templa con trabajo implacable."** 🔥
