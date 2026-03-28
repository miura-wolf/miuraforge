# 🛠️ Manual de Herramientas (Tools) — Miura Forge Engine

Esta es la guía operativa de los scripts auxiliares que mantienen la maquinaria en funcionamiento.

## 🚀 Generadores y Procesadores Principales

### [image_forge.py](file:///d:/YT/MiuraForge/tools/image_forge.py)
**Función:** Motor de generación de imágenes triple (NVIDIA / Nebius / Replicate).
- **Uso:** Convierte prompts de Sheets en archivos `.png`. 
- **Modos:** Prueba, Masivo, Reparar y Manual. Ahora soporta el parámetro `--id` para forjar sesiones específicas de forma aislada.

### [mass_visual_forge.py](file:///d:/YT/MiuraForge/tools/mass_visual_forge.py)
**Función:** Generador de prompts duales ([IMAGEN] + [ANIMACIÓN]).
- **Uso:** Lee el guion de Sheets y lo divide en fragmentos visuales narrativos.

### [forja_masiva.py](file:///d:/YT/MiuraForge/tools/forja_masiva.py)
**Función:** Automatización del backlog.
- **Uso:** Toma ideas de la tabla INVESTIGACIÓN y las convierte en registros de PRODUCCIÓN listos para guionizar.

---

## 🔍 Inspección y Auditoría

### [auditar_sheets.py](file:///d:/YT/MiuraForge/tools/auditar_sheets.py)
**Función:** Verificador de integridad de datos en Google Sheets.
- **Uso:** Asegura que no falten cabeceras o registros críticos.

### [inspeccionar_imperio.py](file:///d:/YT/MiuraForge/tools/inspeccionar_imperio.py) / [inspect_prod.py](file:///d:/YT/MiuraForge/tools/inspect_prod.py)
**Función:** Vistas rápidas de la base de datos sin abrir el navegador.
- **Uso:** Muestra resúmenes de producción en la terminal.

### [review_auditoria.py](file:///d:/YT/MiuraForge/tools/review_auditoria.py)
**Función:** Revisión de las sentencias del Auditor Bunker.

---

## 🧹 Mantenimiento y Caché

### [reset_cache_id_robust.py](file:///d:/YT/MiuraForge/tools/reset_cache_id_robust.py)
**Función:** Limpieza selectiva de la caché visual.
- **Uso:** `python tools/reset_cache_id_robust.py --id <ID>` para permitir regenerar prompts de IA sin costo duplicado en otros IDs.

### [incinerador_chatarra.py](file:///d:/YT/MiuraForge/tools/incinerador_chatarra.py)
**Función:** Eliminación de registros fallidos o irrelevantes.

---

## 📈 Inteligencia y Estrategia

### [weekly_oracle.py](file:///d:/YT/MiuraForge/tools/weekly_oracle.py)
**Función:** Radar de tendencias semanales (Radar de Pulso).
- **Uso:** Identifica qué duele en el mundo masculino esta semana.

### [youtube_forge.py](file:///d:/YT/MiuraForge/tools/youtube_forge.py)
**Función:** Generador de metadatos (Títulos, Descripciones, Tags) para YouTube.
- **Uso:** Optimización SEO final previo a la publicación.

---

> [!NOTE]
> Todos los scripts están diseñados para ejecutarse desde la raíz del proyecto para asegurar la carga correcta de variables de entorno y módulos locales.
