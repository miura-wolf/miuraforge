# ⚔️ Miura Forge Engine — Control Central

**Miura Forge Engine** es un ecosistema avanzado de inteligencia artificial diseñado para la creación automatizada de contenido de alto impacto para YouTube Shorts, bajo la doctrina de **"Disciplina en Acero"**. Este motor no solo genera texto; forja narrativas de activación física mediante una integración profunda de ingeniería mental, mitología industrial y automatización técnica.

---

## 🏛️ Filosofía: Disciplina en Acero
El motor opera bajo una ley inquebrantable:
- **No humilla, no consuela, no dramatiza.**
- **Revela, Diagnostica y Ordena.**
- Ataca la mentira interna (autoengaño) del hombre para reconstruir su responsabilidad mediante acciones físicas concretas.

---

## 🏗️ Arquitectura del Sistema

La forja está compuesta por módulos especializados que trabajan en cadena:

### 1. 🔍 Researcher (El Explorador OSINT)
- **Radar Multi-Plataforma:** Escanea Reddit, X, YouTube, Quora, Medium y Substack.
- **Detección de Pulso:** Capacidad de descubrir tendencias semanales de forma autónoma sin temas predefinidos.
- **Análisis Psicológico Real:** Utiliza LLMs para validar testimonios humanos genuinos y detectar "Dolores Estructurales".
- **Ranking de Dolor:** Clasifica hallazgos en una escala del 1-4 y detecta frases potentes de alta carga emocional.
- **Trazabilidad Total:** Registro optimizado de fuentes con IDs únicos y metadatos de engagement.

### 2. 🔮 El Oráculo Semanal (`weekly_oracle.py`)
- **Descubrimiento Autónomo:** Escaneo táctico de comunidades masculinas para identificar los 3 temas más críticos de la semana.
- **Infiltración Profunda:** Ejecuta investigaciones OSINT automáticas por cada tendencia detectada.
- **Ingeniería Competitiva:** Extrae Títulos Maestros y Hooks de apertura de contenido viral exitoso para alimentar el Arsenal.

### 3. ⚗️ Alchemist (La Alquimia Digital)
- **Transmutación Táctica:** Convierte el dolor crudo en una estructura estratégica de 3 fases (Estabilidad, Inestabilidad, Reconfiguración).
- **Algoritmo de 30 Títulos Virales:** Basado en 6 plantillas narrativas, genera 30 variantes de alto impacto.

### 4. 📐 Architect (Andrés - La Voz)
- **Motor:** Impulsado por `gemini-2.0-pro` o modelos NVIDIA-Compatible calibrados para redacción quirúrgica.
- **Inyección de Carbono (Directiva Suprema):** Bloqueo total de verbos de duda. Actúa como una prensa hidráulica.
- **Inyección de Doctrina:** Uso de manuales (PDFs) para coherencia filosófica absoluta.

### 5. 🎙️ Voice & Visual Directors
- **Visual Director:** Genera prompts cinematográficos vinculados al dolor estructural.
- **Motor de Imágenes Triple (image_forge.py):** Sistema de cascada inteligente (NVIDIA -> Nebius -> Replicate) para generar frames WebP de alta calidad a bajo costo ($0.003/img).
- **Voice Director:** Generación de voces estoicas y autoritarias vía ElevenLabs con identidad de marca "Andrés".

---

## 🛡️ Características de Élite

*   **Forja Infinita (Rotación de 10 Keys):** Sistema de autogestión de cuota que rota automáticamente entre 10 API Keys de Gemini ante errores 429 (Resource Exhausted).
*   **Resiliencia Total:** Implementación de `tenacity` para retries exponenciales en todas las llamadas a APIs.
*   **Radar de Tendencias:** Actualización automática de la frecuencia de dolores en Sheets, permitiendo ver qué temas están "quemando" la red semana tras semana.
*   **Memoria Global:** Prevención de repetición de metáforas registradas en la pestaña `MEMORIA`.

---

## 📊 Database (El Puente de Mando)

Sincronización bidireccional perfecta con **Google Sheets**.
- **Tablas Críticas:**
    - `FUENTES`: Registro A-J (ID_Sesion, Plataforma, Origen, URL, Autor, Engagement, Fecha, Query, Fecha_Extraccion).
    - `INVESTIGACION_PSICOLOGICA`: Almacén de análisis emocional y frases potentes de testimonios reales.
    - `ARSENAL_GANCHOS`: Repositorio de hooks estratégicos y títulos de competencia.
    - `DOLORES_MASCULINOS`: Seguimiento numérico de la frecuencia de cada dolor detectado.

---

## 🛠️ Requisitos Técnicos

- **Python 3.10+**
- **APIs:** Google Gemini (10 Keys), NVIDIA AI (DeepSeek), Replicate (Flux Schnell), Nebius (Flux Dev), Tavily (Research), ElevenLabs (Voz).
- **Librerías:** `google-genai`, `replicate`, `requests`, `gspread`, `rich`, `tenacity`.

---

## 🛠️ Mantenimiento y Auditoría

El motor incluye un kit de herramientas para asegurar la salud del Puente de Mando (Google Sheets):

- **Generación Visual:** Motor para crear imágenes y prompts duales masivamente.
  ```bash
  python tools/mass_visual_forge.py  # Genera prompts en Sheets
  python tools/image_forge.py        # Genera imágenes físicas
  ```
- **Inspección de Salud:** Analiza si las tablas y columnas están alineadas con el código.
  ```bash
  python tools/inspeccionar_imperio.py
  ```

---

## ⚔️ Ejecución

**Ritual Semanal (Cada Domingo):**
```bash
python weekly_oracle.py
```

**Producción de Guiones:**
```bash
python main.py
```

"El acero no se oxida con orgullo; se templa con trabajo implacable."

