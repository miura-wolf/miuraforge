# 📚 ÍNDICE DE DOCUMENTACIÓN TÉCNICA MIURA FORGE

Este directorio contiene el análisis exhaustivo del sistema Miura Forge Engine.

---

## 📄 Documentos Disponibles

### 1. **ANALISIS_COMPLETO_MIURA_FORGE.md**
**Descripción:** Documento principal con análisis técnico integral (9,500+ palabras)

**Contenido:**
- ✅ Arquitectura general y filosofía
- ✅ Árbol de directorios completo
- ✅ Análisis detallado de cada módulo (10 módulos principales)
- ✅ Flujos de trabajo (Investigación → Redacción → Despliegue)
- ✅ Sistema de IA multi-tier (Gemini → NVIDIA → Groq)
- ✅ Google Sheets (13 tablas, estructura, escudo)
- ✅ Scripts de mantenimiento
- ✅ Doctrina y configuración
- ✅ Puntos de entrada
- ✅ Tecnologías y dependencias
- ✅ ADN Doctrinal (El Hombre que Dejó de Mentirse)
- ✅ Seguridad y deudas técnicas
- ✅ Escalabilidad y mejoras futuras

**Público:** Desarrolladores, arquitectos, DevOps

**Formato:** Markdown (visualización en GitHub/GitLab/VS Code)

---

### 2. **ARBOL_FUNCIONAL_MIURA_FORGE.txt**
**Descripción:** Vista rápida y visual de la estructura y flujos

**Contenido:**
- 📊 Estructura de directorios organizada por función
- 📈 Flujo de datos principal (Flujo Completo Opción 3)
- 🔮 Oráculo Semanal (autónomo)
- 📧 Emisario (3 secuencias de email)
- 🌐 Tablas Google Sheets (13 tablas con columnas)
- 🧩 Mapa de dependencias entre módulos
- ⚙️ Sistema de resiliencia (Chain of Responsibility)
- 🔐 Variables de entorno requeridas
- 📊 Métricas del sistema
- ✅ Checklist de instalación/corrida

**Público:** Operadores, new hires, referencia rápida

**Formato:** Texto plano con emojis/ASCII (imprimir o leer en terminal)

---

---

### 3. **GUIA_VIRTUAL_ENV.md**
**Descripción:** Guía táctica para la administración del entorno virtual de Python.

**Contenido:**
- ✅ Diferencia entre Python Global y Local (venv)
- ✅ Comandos de instalación correctos (`pip install`)
- ✅ Cómo listar herramientas instaladas
- ✅ Instalación de motores Playwright/Chromium
- ✅ Activación opcional del entorno

**Público:** Operadores, Soberano

**Formato:** Markdown (VS Code / Terminal)

---

## 🚀 Cómo Usar Esta Documentación

### Paraunderstanding del sistema (primera vez):
1. Leer **README.md** (5 min) → contexto general
2. Revisar **ARBOL_FUNCIONAL.txt** (10 min) → panorama estructura
3. Sumergirse en **ANALISIS_COMPLETO.md** (30-60 min) → profundidad

### Para desarrollo/modificación:
1. Buscar módulo específico en ANALISIS_COMPLETO.md → Sección 3
2. Consultar flujo correspondiente en ARBOL_FUNCIONAL.txt
3. Revisar código fuente directamente con el contexto

### Para deployment/DevOps:
1. Sección "Tecnologías y Dependencias" → requirements.txt
2. Sección "Google Sheets" → credenciales, Service Account
3. Checklist de instalación en ARBOL_FUNCIONAL.txt
4. Variables de entorno en .env

### Para troubleshooting:
1. Sistema de resiliencia → cómo fallan los tiers
2. Logger → output/logs/registro_combate.log
3. Escudo de estructura → tools/inspeccionar_imperio.py

---

## 📊 Estadísticas del Análisis

- **Archivos Python analizados:** 35+ scripts
- **Líneas de código revisadas:** ~6,000 LOC (sin contar venv)
- **Tablas Sheets:** 13 (estructura detallada)
- **API Integrations:** 7 servicios (Gemini, NVIDIA, Groq, Tavily, YouTube, ElevenLabs, Brevo)
- **Prompt files:** 6 directivas doctrinales
- **PDFs doctrinales:** 3 libros de fundamento

---

## 🔄 Mantenimiento de la Documentación

Esta documentación debe actualizarse cuando:

- [ ] Se agregue un nuevo módulo Python
- [ ] Se modifique una tabla de Google Sheets
- [ ] Se cambie un proveedor de IA o modelo
- [ ] Se añada una nueva secuencia (Ej: nuevo flujo)
- [ ] Se actualicen dependencias (requirements.txt)
- [ ] Se modifique la arquitectura (ej: añadir cache Redis)

**Proceso:**
1. Editar `ANALISIS_COMPLETO_MIURA_FORGE.md`
2. Actualizar `ARBOL_FUNCIONAL_MIURA_FORGE.txt` si cambia estructura/flujos
3. Commit con mensaje: "docs: actualizar análisis tras <cambio>"
4. Opcional: regenerar desde cero con este script si estructura cambia drásticamente

---

## 📞 Glosario

| Término | Significado |
|---------|-------------|
| **Soberano** | El operador humano que aprueba/rechaza guiones |
| **Andrés** | La voz del sistema (Arquitecto, tone of voice) |
| **Forja / Acero** | Metáforas centrales de la doctrina industrial |
| **Maestro / MASTER** | Guion completo aprobado (3 fases en uno) |
| **Alquimia** | Proceso de transmutar dolor en estructura narrativa |
| **OSINT** | Open Source Intelligence (búsqueda en Reddit, X, Quora, etc) |
| **ResilientProvider** | Sistema de 3 tiers con fallover automático |
| **Puente de Mando** | Google Sheets (single source of truth) |
| **Escudo** | Auto-reparación de estructura de tablas |
| **Directivas IMP** | Clusterización, Tendencias, Frases Virales |
| **Disciplina en Acero** | Doctrina/marca del sistema |

---

## 🎯 Públicos Objetivo

| Documento | Devs | Ops | New Hire | Manager | Cliente |
|-----------|------|-----|----------|---------|---------|
| ANALISIS_COMPLETO.md | ✅ | ✅ | ✅ | ⚠️ | ❌ |
| ARBOL_FUNCIONAL.txt | ✅ | ✅ | ✅ | ✅ | ⚠️ |
| README.md | ✅ | ✅ | ✅ | ✅ | ✅ |

---

**"El acero no se oxida con orgullo; se templa con trabajo implacable."**

📅 Última actualización: 2026-03-25
🔧 Generado por: Antigravity (Advanced Agentic Coding - Google Deepmind)
