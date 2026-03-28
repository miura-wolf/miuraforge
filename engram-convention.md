# 🧠 Convención de Memoria (Engram) - Miura Forge

Este archivo define cómo utilizamos `engram` para mantener la memoria persistente entre sesiones de desarrollo.

## 📌 Etiquetas de Proyecto
- Usar siempre `--project MiuraForge` para todas las memorias relacionadas con este motor.

## 📝 Formatos de Título
- **Sesión: [Tema]**: Resumen general al inicio/fin de una sesión.
- **Decisión: [ID]**: Registro de una decisión arquitectónica o de diseño.
- **Bug: [Descripción]**: Registro de un error encontrado y su solución.
- **Hito: [Nombre]**: Alcance de un objetivo mayor del pipeline.

## 🛠 Comandos de Referencia

### Guardar Memoria
```bash
engram save "Sesión: Integración de Engram" "Resumen de lo hecho..." --project MiuraForge
```

### Recuperar Contexto
```bash
engram context MiuraForge
```

## 📜 Reglas de Oro
1. Cada vez que se corrija un bug crítico (e.g., error 403 en Meta AI), se debe guardar en Engram.
2. Al iniciar una nueva sesión, el agente debe disparar `engram context` para recuperar el estado anterior.
3. Las metáforas de la doctrina Miura que se consideren "gastadas" deben guardarse como memorias para evitar repetición en el pipeline.
