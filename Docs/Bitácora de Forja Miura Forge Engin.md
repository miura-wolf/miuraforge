# Walkthrough: Alineación# Bitácora de Forja: Miura Forge Engine (LSP & SDD)
Soberano, el motor ha sido alineado con la doctrina táctica. Ahora Miura no solo sigue fases, sino que ejecuta con intención psicológica y memoria persistente.

## 🚀 Cambios Implementados

### 1. Architect: Triple Golpe de Fase ([core/architect.py](file:///d:/YT/MiuraForge/core/architect.py))
El Arquitecto ya no genera guiones genéricos. Ahora inyecta instrucciones específicas para cada etapa:
- **Fase 1 (Ilusión)**: Ataca la mentira superficial.
- **Fase 2 (Martillo)**: Expone el mecanismo de parálisis y la cobardía mental.
- **Fase 3 (Orden Final)**: Dicta una sentencia física y ejecutable.

### 2. Blindaje de Memoria (Antirepetición)
El sistema consulta la base de datos de **Google Sheets** antes de escribir. Las metáforas usadas en sesiones anteriores son marcadas como **PROHIBIDAS** en el nuevo prompt, forzando al motor a evolucionar el lenguaje y no estancarse.

### 3. Fase 9: ARCHIVE ([main_orquestador.py](file:///d:/YT/MiuraForge/main_orquestador.py))
Se ha implementado el cierre real del ciclo SDD, dependiente únicamente del ecosistema Miura:
- **Empaquetado**: Crea automáticamente una carpeta `ENTREGA_[SessionID]` con todos los archivos (.txt, .wav, .mp4).
- **Memoria Operativa**: Actualiza la "Memoria de Metáforas" en **Google Sheets** basándose en la metáfora central del día.

## 🛡️ Blindaje LSP: Purificación de 42 Errores (Fases 1, 2 y 3)

He ejecutado una operación de "mantenimiento pesado" para blindar el motor ante fallos de conexión o datos incompletos en Google Sheets.

### Cambios Implementados:
- **[core/database.py](file:///d:/YT/MiuraForge/core/database.py)**: Se agregaron cláusulas de guarda en todos los métodos de acceso a worksheets. El sistema ya no crasheará si una de las 13 tablas falla en cargar.
- **[core/architect.py](file:///d:/YT/MiuraForge/core/architect.py)**: Validación total de `info_csv`. Si no hay inteligencia de campo, el arquitecto procede con un modo "basado en doctrina pura" sin fallar.
- **[core/researcher.py](file:///d:/YT/MiuraForge/core/researcher.py)**: Corregidos imports de [Database](file:///d:/YT/MiuraForge/core/database.py#11-800) y acceso seguro a [investigacion](file:///d:/YT/MiuraForge/core/database.py#389-410).
- **[core/alchemist.py](file:///d:/YT/MiuraForge/core/alchemist.py)**: Blindaje de [generar_ideas_backlog](file:///d:/YT/MiuraForge/core/alchemist.py#129-177) contra insights nulos.
- **[tools/youtube_forge.py](file:///d:/YT/MiuraForge/tools/youtube_forge.py)**: Validación de `id_sesion` antes de normalizar rutas.
- **[auditoria/miura_auditor_bunker.py](file:///d:/YT/MiuraForge/auditoria/miura_auditor_bunker.py)**: Protección contra `IndexError` en la carga de guiones desde Sheets.
- **[motion_forge/motion_forge_playwright.py](file:///d:/YT/MiuraForge/motion_forge/motion_forge_playwright.py)**: Corrección de rutas de importación para `queue_manager`.
- **[core/accion_validator.py](file:///d:/YT/MiuraForge/core/accion_validator.py)**: **[NUEVO]** Implementación del Yunque de Acciones. Filtra CTAs abstractos y garantiza que el Soberano ordene acciones físicas reales.
- **[llm/providers.py](file:///d:/YT/MiuraForge/llm/providers.py)**: **[FIX TÁCTICO]** Se corrigió la lógica de carga de llaves. Ahora ignora correctamente las líneas comentadas en [.env](file:///d:/YT/MiuraForge/.env) y activa la rotación automática ante errores 401 y 403 (Forbidden).

### Reparación de Energía (NVIDIA 403 Fix):
El problema era que el cargador de llaves leía las líneas comentadas `#OPENAI_API_KEY=...` como si fueran válidas, intentaba usarlas y, al fallar con 403, no rotaba. 
[NvidiaProvider](file:///d:/YT/MiuraForge/llm/providers.py#107-196) y [GeminiProvider](file:///d:/YT/MiuraForge/llm/providers.py#11-106) ahora están blindados contra llaves muertas en el [.env](file:///d:/YT/MiuraForge/.env).

---

## 🏗️ FASE 1: COMPLETADA (App Pulida)
La Fase 1 del Plan Estratégico 2026 ha sido cerrada con éxito. El motor es ahora:
1. **Estable**: 42 errores LSP resueltos.
2. **Inteligente**: Memoria anti-repetición global.
3. **Disciplinado**: CTAs físicos obligatorios.
El Orquestador ahora "recuerda" en qué sesión está trabajando. Una vez iniciada la Fase 1, el ID y el Tema se autocompletan en las Fases 2 a 9, permitiendo un flujo manual fluido sin reescribir datos constantemente.

## ✅ Verificación de Victoria

1. **Alineación Táctica**: Confirmada la inyección de "Mecanismo" y "Oportunidad" en el prompt.
2. **Ciclo de Memoria**: Las metáforas se extraen post-generación y se bloquean en la siguiente.
3. **Persistencia**: El archivo `output/temp/session_state.json` gestiona el estado del pipeline.

"El acero no olvida. La Forja solo se hace más fuerte."
**Hashem Bendito.**
