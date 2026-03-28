# Walkthrough: Optimización y Auditoría Final (Fase Acero)

Soberano, la nave ha sido reconfigurada para un desempeño máximo. El pipeline ahora es capaz de procesar una idea y llevarla hasta la generación de imágenes finales de forma 100% automatizada.

## ⚔️ Cambios Implementados

### 1. Flujo "FORJA TOTAL" (Opción 8)
- Se ha creado un nuevo punto de entrada en [main.py](file:///d:/YT/MiuraForge/main.py) que orquesta la secuencia completa:
  - **Consultoría al Oráculo Semanal:** Si no defines un tema, el Oráculo sugiere una tendencia basada en el dolor del nicho.
  - **Investigación OSINT** (Tavily + YouTube).
  - **Redacción de Guiones** (Arquitecto sin pausas manuales).
  - **Auditoría de Calidad** (Bunker - Purificación automática).
  - **Prompts Visuales** (Dual: Imagen + Animación).
  - **Generación de Imágenes** (Cascada Triple Motor: NVIDIA -> Nebius -> Replicate).
  - **YouTube SEO Forge:** Generación automática de Títulos, Descripciones, Tags y Hashtags sincronizados con Google Sheets.
- **Voz:** Se ha separado del flujo principal (Opción 4) debido al estado de los créditos de ElevenLabs, evitando que el proceso se detenga por fallos de cuota.

### 2. YouTube Forge Independiente (Opción 7)
- Ahora puedes generar metadatos optimizados para cualquier video existente de forma aislada, asegurando que el SEO esté siempre afilado.

### 3. Estandarización de Imagen (PNG)
- El motor de imágenes ahora utiliza la librería **Pillow** para asegurar que toda salida sea `.png`, independientemente del motor utilizado. 
- **Replicate Integration:** Automáticamente convierte el formato WebP nativo de la API a PNG de alta compatibilidad para Grok, Vheer o Qwen.

### 4. Limpieza de Puente de Mando (Docs)
- La carpeta `Docs` ahora solo contiene los documentos maestros y directivas actuales.
- Se ha creado la carpeta `miura_steel` en la raíz para albergar toda la documentación de legado o no esencial, lista para ser trasladada.

### 4. Manual de Herramientas
- Se ha generado un [manual_tools.md](file:///C:/Users/carja/.gemini/antigravity/brain/86bb25a0-102a-47dc-85f6-04ad26ba3989/manual_tools.md) detallando la función de cada script en la carpeta `tools`.

---

## 🛠️ Cómo Ejecutar el Flujo Total

1. Inicie el puente de mando: `python main.py`.
2. Seleccione la **Opción 7: ⚔️ FORJA TOTAL**.
3. Ingrese el tema de investigación.
4. Observe cómo la IA forja el guion, los prompts y las imágenes sin interrupciones.

**El acero está templado. La forja es suya, Soberano.**
