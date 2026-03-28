# 🤝 Gentleman AI como Coequipero de Desarrollo

> Guía de instalación y uso de Gentleman AI para trabajar EN MiuraForge (no integrarlo)

---

## 📋 RESUMEN EJECUTIVO

**Gentleman AI NO se integra en MiuraForge.** Se instala como **herramienta de desarrollo externa** para ayudarte a:
- Desarrollar código más eficientemente
- Ahorrar tokens con el workflow SDD
- Mantener memoria persistente entre sesiones
- Aprender mientras desarrollas

Es como tener un "pair programming" avanzado que te asiste mientras trabajas en el proyecto.

---

## 🚀 INSTALACIÓN RÁPIDA

### Opción 1: Homebrew (Recomendada - macOS/Linux)

```bash
# Instalar
curl -fsSL https://raw.githubusercontent.com/Gentleman-Programming/gentle-ai/main/scripts/install.sh | bash

# O con Homebrew
brew tap Gentleman-Programming/homebrew-tap
brew install gentle-ai

# Ejecutar configuración
gentle-ai
```

### Opción 2: Windows (PowerShell)

```powershell
# Opción 1: Script automático
irm https://raw.githubusercontent.com/Gentleman-Programming/gentle-ai/main/scripts/install.ps1 | iex

# Opción 2: Descargar release manual
# Ir a: https://github.com/Gentleman-Programming/gentle-ai/releases
# Descargar gentle-ai_windows_amd64.exe
# Agregar al PATH
```

### Opción 3: Go Install

```bash
# Requiere Go 1.24+
go install github.com/gentleman-programming/gentle-ai/cmd/gentle-ai@latest
```

---

## ⚙️ CONFIGURACIÓN PARA MIURA FORGE

### Paso 1: Iniciar Gentleman AI

```bash
gentle-ai
```

### Paso 2: Seleccionar Componentes

```
✅ INSTALAR:
- Engram (memoria persistente)
- SDD (workflow de desarrollo)
- Skills (patrones de código)
- Persona: "Gentleman" o "Neutral"

❌ NO INSTALAR:
- GGA (switcher de proveedores) - Ya tienes tu propio sistema de rotación
- Theme - No necesario para desarrollo
```

### Paso 3: Configurar Agentes Soportados

**Soporta:**
- ✅ Claude Code
- ✅ OpenCode
- ✅ Gemini CLI
- ✅ Codex
- ✅ Cursor
- ✅ VS Code + Copilot
- ✅ Antigravity

**Recomendación:** Usa **Claude Code** o **OpenCode** para MiuraForge.

### Paso 4: Activar Multi-Mode (OpenCode exclusivo)

Si usas OpenCode, puedes asignar modelos diferentes a cada fase:

```
SDD Phase Configuration:
- Explore: Sonnet (rápido, exploración)
- Propose: Gemini 2.5 Flash (buen razonamiento, barato)
- Spec: Gemini 2.5 Flash (documentación)
- Design: Opus (arquitectura compleja)
- Implement: Sonnet (codificación)
- Verify: Codex (detección de bugs)
- Archive: Sonnet (documentación final)
```

---

## 🎯 USO CON MIURA FORGE

### Escenario 1: Desarrollar Nueva Feature

```bash
# 1. Entrar al proyecto
cd D:\YT\MiuraForge

# 2. Abrir tu agente con Gentleman AI activado
# (Claude Code, OpenCode, etc.)
claude
# o
opencode

# 3. El agente ya tiene:
#    - Memoria de sesiones anteriores (Engram)
#    - Skills de Python cargados automáticamente
#    - Workflow SDD disponible
```

**Comandos útiles:**
```
# Iniciar SDD para feature grande
"Implementar feature X usando SDD"

# Ver memoria de sesiones anteriores
"¿Qué estábamos haciendo la última vez?"

# Cargar skill específico
"/apply skill:python-testing"
```

### Escenario 2: Debuggear Código

```bash
# El agente puede:
# - Ver el historial de cambios
# - Recordar bugs anteriores similares
# - Sugerir soluciones basadas en memoria

"Estoy teniendo un error 403 con NVIDIA"
# → El agente recuerda que pasó antes y sugiere verificar el modelo
```

### Escenario 3: Refactorizar

```
"Refactorizar el sistema de credenciales usando SDD"

# El agente iniciará:
# 1. EXPLORE: Analizar codebase actual
# 2. PROPOSE: Sugerir nueva estructura
# 3. SPEC: Diseñar implementación
# 4. DESIGN: Planificar cambios
# 5. IMPLEMENT: Ejecutar refactor
# 6. VERIFY: Validar cambios
# 7. ARCHIVE: Documentar decisiones
```

---

## 💡 BENEFICIOS ESPECÍFICOS PARA MIURA FORGE

### 1. **Memoria entre Sesiones**

**Sin Gentleman:**
```
Tú: "Estaba trabajando en el módulo de autenticación..."
IA: "¿Qué módulo? No tengo contexto"
```

**Con Gentleman + Engram:**
```
Tú: "Continuemos con lo de ayer"
IA: "Veo que estabas refactorizando el sistema de credenciales 
      en core/config.py. Encontraste un issue con la ruta 
      de META_STATE_PATH que posiblemente no está definida. 
      ¿Quieres seguir con eso?"
```

### 2. **Ahorro de Tokens (50-70%)**

Gentleman AI usa un **orquestador principal** que delega a **subagentes**:
- Cada subagente tiene su propia ventana de contexto limpia
- No se acumula ruido de la conversación principal
- Menos compactaciones = menos pérdida de información

### 3. **Skills Automáticos**

Al trabajar en Python, Gentleman carga automáticamente:
- Patrones de testing
- Convenciones de código
- Manejo de errores
- Documentación

### 4. **Workflow SDD Estructurado**

Para tareas complejas, el agente sigue fases explícitas:
1. **Explore:** Investigar antes de actuar
2. **Propose:** Proponer solución antes de implementar
3. **Spec:** Especificar detalles
4. **Design:** Diseñar arquitectura
5. **Implement:** Ejecutar
6. **Verify:** Validar
7. **Archive:** Documentar

---

## 🔄 FLUJO DE TRABAJO RECOMENDADO

### 1. Sesión Diaria de Desarrollo

```bash
# Abrir terminal en D:\YT\MiuraForge
cd D:\YT\MiuraForge

# Iniciar agente con Gentleman
code  # VS Code + Gentleman
# o
claude  # Claude Code + Gentleman
# o
opencode  # OpenCode + Gentleman

# Trabajar normalmente...
# El agente recordará todo automáticamente
```

### 2. Tareas Complejas (SDD)

```
Tú: "Implementar el sistema de migración de credenciales con SDD"

IA:
"Voy a iniciar SDD para esta feature.

**FASE 1 - EXPLORE:**
Primero, exploremos el codebase actual...
[Subagente sdd-explore analiza el proyecto]

**FASE 2 - PROPOSE:**
Basado en el análisis, propongo:
1. Crear script migrar_credenciales.py
2. Actualizar core/config.py
3. Modificar todos los scripts afectados

**FASE 3 - SPEC:**
Especificaciones técnicas...

[Continúa por cada fase...]"
```

### 3. Cierre de Sesión

```
Tú: "Guardar sesión"

IA: "Memoria guardada en Engram. Próxima sesión recordarás:
      - Qué estabas haciendo
      - Decisiones tomadas
      - Bugs encontrados
      - Pendientes"
```

---

## 📚 COMANDOS ÚTILES

### Comandos de Gentleman

```bash
# Ver estado
gentle-ai status

# Actualizar
gentle-ai update

# Ver memoria
gentle-ai engram status

# Resetear memoria (cuidado!)
gentle-ai engram reset
```

### Comandos en el Agente

```
/apply skill:nombre     # Cargar skill específico
/sdd-start              # Iniciar workflow SDD
/sdd-status             # Ver estado del workflow
/engram-save            # Guardar memoria manualmente
/engram-recall          # Recordar contexto anterior
```

---

## ⚠️ IMPORTANTE: Límites y Consideraciones

### ✅ SÍ usar Gentleman para:
- Desarrollar código de MiuraForge
- Debuggear problemas
- Refactorizar módulos
- Escribir documentación
- Crear tests
- Planificar arquitectura

### ❌ NO usar Gentleman para:
- Ejecutar el pipeline de producción de MiuraForge
- Generar videos automáticamente
- Subir contenido a YouTube
- Reemplazar main.py o el motor de producción

### 🔄 Separación Clara:

| Gentleman AI | MiuraForge |
|-------------|------------|
| Desarrollo del código | Ejecución del pipeline |
| Asistencia al programador | Motor de automatización |
| Memoria de desarrollo | Memoria de producción (Google Sheets) |
| SDD para features | Pipeline de 9 fases para videos |

---

## 🔧 INTEGRACIÓN CON TU WORKFLOW ACTUAL

### Opción A: Mantener Separados (Recomendado)

```
Terminal 1: Desarrollo
  └─ Gentleman + Claude Code/OpenCode
  └─ Editar código de MiuraForge

Terminal 2: Producción
  └─ Python venv de MiuraForge
  └─ Ejecutar main.py
  └─ Usar interfaz rica de MiuraForge
```

### Opción B: VS Code + Gentleman

1. Abrir VS Code en D:\YT\MiuraForge
2. Instalar extensión de Gentleman (si existe)
3. Usar Copilot + Gentleman para desarrollo
4. Terminal separada para ejecutar MiuraForge

---

## 📊 COMPARACIÓN: Antes vs Después

### Antes (sin Gentleman)
```
Sesión 1:
Tú: "Estoy trabajando en el sistema de autenticación"
[Desarrollas feature]

Sesión 2 (día siguiente):
Tú: "¿Qué estaba haciendo ayer?"
IA: "No tengo contexto de sesiones anteriores"
Tú: [Tienes que explicar todo de nuevo]
```

### Después (con Gentleman)
```
Sesión 1:
Tú: "Estoy trabajando en el sistema de autenticación"
[Desarrollas feature]
IA: Guarda en Engram automáticamente

Sesión 2:
Tú: "Continuemos"
IA: "Veo que ayer estabas implementando el sistema de 
      autenticación en auth_youtube.py. Te quedaste en 
      validar las credenciales de Meta AI. ¿Quieres 
      seguir con eso?"
Tú: "Sí, exacto"
[Continúas sin perder contexto]
```

---

## 🎯 CONCLUSIÓN

**Gentleman AI es tu asistente de desarrollo**, no una parte de MiuraForge.

**Analogía:**
- MiuraForge = Tu fábrica de contenido
- Gentleman AI = Tu asistente personal que te ayuda a construir/mantener la fábrica

**Instala Gentleman AI** → **Usa tu agente favorito** → **Desarrolla MiuraForge** → **Ejecuta MiuraForge por separado**

---

## 📞 SOPORTE

- **GitHub Gentleman AI:** https://github.com/Gentleman-Programming/gentle-ai
- **Issues:** https://github.com/Gentleman-Programming/gentle-ai/issues
- **Discord Gentleman:** [Buscar en el perfil de Alan](https://github.com/Alan-TheGentleman)

---

**Nota:** Esta guía fue creada específicamente para el equipo de Miura Forge basándose en el tutorial completo del repositorio Gentleman AI.

**Versión:** 1.0  
**Fecha:** Marzo 2026
