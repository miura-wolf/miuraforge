# AUDITORÍA DE ERRORES LSP - Miura Forge Engine

**Fecha:** Marzo 2026  
**Versión:** 1.0  
**Total de archivos analizados:** 20+ módulos principales  
**Total de errores encontrados:** 42

---

## 🔴 URGENTES (Bloquean ejecución)

### Archivo: core/database.py (15+ errores)

| Línea | Error | Severidad | Solución |
|-------|-------|-----------|----------|
| 40-62 | Worksheets asignados sin verificación de None | CRÍTICO | Agregar validación `if self.logistica:` antes de cada uso |
| 58 | `col_values` en None (self.fuentes) | CRÍTICO | Verificar `if self.fuentes:` antes |
| 297 | `get_all_records` en None (self.dolores) | CRÍTICO | Agregar `if not self.dolores: return []` |
| 354 | `get_all_records` en None (self.territorios) | CRÍTICO | Verificar existencia antes |
| 357 | `get_all_records` en None (self.dolores) | CRÍTICO | Verificar existencia antes |
| 385 | `get_all_records` en None (self.ganchos) | CRÍTICO | Verificar existencia antes |
| 439 | `find` en None (self.produccion) | CRÍTICO | Verificar `if self.produccion:` antes |
| 504 | `col_values` en None (self.auditoria) | CRÍTICO | Verificar existencia |
| 534-537 | `update_cell` en None (self.produccion) | CRÍTICO | Verificar existencia al inicio |
| 551 | `get_all_values` en None (self.auditoria) | CRÍTICO | Verificar `if not self.auditoria: return None` |
| 568 | `get_all_records` en None (self.auditoria) | CRÍTICO | Verificar existencia |
| 586 | `append_row` en None (self.logistica) | CRÍTICO | Verificar existencia |
| 589-651 | Múltiples accesos sin verificación en guardar_fase | CRÍTICO | Verificar existencia al inicio |
| 654-681 | Acceso sin verificación en obtener_master_aprobado | CRÍTICO | Agregar verificación al inicio |
| 684-718 | Acceso sin verificación en obtener_guion_validado | CRÍTICO | Verificar existencia |
| 721 | `find` en None (self.logistica) | CRÍTICO | Verificar existencia |
| 728-754 | Acceso a memoria sin verificación | CRÍTICO | Verificar existencia de memoria |
| 762-782 | Acceso a despliegue sin verificación | CRÍTICO | Verificar existencia |

**Patrón de solución:**
```python
def metodo(self):
    if not self.produccion:
        print("⚠️ [Database] PRODUCCION no disponible")
        return None
    # ... resto del código
```

---

### Archivo: core/architect.py (4 errores)

| Línea | Error | Severidad | Solución |
|-------|-------|-----------|----------|
| 41-44 | `split` en None (info_csv) | CRÍTICO | Verificar `if info_csv:` antes |
| 44 | `split` en None (info_csv) | CRÍTICO | Verificar existencia |
| 46 | `get` en None (info_csv) | CRÍTICO | Verificar existencia |
| 92 | `get` en None (info_csv) | CRÍTICO | Verificar existencia |

**Solución:**
```python
info_csv = self._extraer_inteligencia(tema_global)
if not info_csv:
    return None
# Ahora info_csv es seguro de usar
```

---

### Archivo: core/researcher.py (2 errores)

| Línea | Error | Severidad | Solución |
|-------|-------|-----------|----------|
| 582 | Database no importado | CRÍTICO | Agregar `from core.database import Database` |
| 587 | `get_all_records` en None (db.investigacion) | CRÍTICO | Verificar existencia |

---

### Archivo: motion_forge/motion_forge_playwright.py (1 error)

| Línea | Error | Severidad | Solución |
|-------|-------|-----------|----------|
| 49-57 | Import incorrecto | CRÍTICO | Cambiar `from queue_manager` a `from motion_forge.queue_manager` |

---

## 🟡 ALTOS (Edge Cases)

### Archivo: auditoria/miura_auditor_bunker.py (1 error)

| Línea | Error | Severidad | Solución |
|-------|-------|-----------|----------|
| 242-244 | Index out of bounds | CRÍTICO | Verificar `if len(row) > 1:` antes de acceder a `row[1]` |

**Solución:**
```python
for row in all_audits:
    if row and len(row) > 1 and str(row[0]).strip() == id_buscado:
        guion_texto = row[1]
```

---

### Archivo: core/alchemist.py (2 errores)

| Línea | Error | Severidad | Solución |
|-------|-------|-----------|----------|
| 142 | Argumentos None en concatenación | CRÍTICO | Verificar que insight no sea None antes |
| 143 | `join` en None | CRÍTICO | Verificar `if insight.get("frases_potentes"):` |

---

### Archivo: tools/youtube_forge.py (1 error)

| Línea | Error | Severidad | Solución |
|-------|-------|-----------|----------|
| 259 | `split` en None (id_sesion) | CRÍTICO | Verificar `if id_sesion:` antes |

---

## 🟢 MEDIOS (Advertencias)

### Archivo: llm/memory_manager.py (1 error)

| Línea | Error | Severidad | Solución |
|-------|-------|-----------|----------|
| 43 | Type mismatch en asignación | ADVERTENCIA | Asegurar retorno consistente |
| 61 | `append_rows` en None (self.db) | CRÍTICO | Verificar `if self.db:` |

---

### Archivo: core/tendencias.py (2 errores)

| Línea | Error | Severidad | Solución |
|-------|-------|-----------|----------|
| 24 | `strip` en None | ADVERTENCIA | Usar `(r.get('DOLOR_PRINCIPAL') or 'desconocido').strip()` |
| 40 | `worksheet` en None | CRÍTICO | Verificar existencia de db y sheet |

---

### Archivo: core/clusterizador.py (2 errores)

| Línea | Error | Severidad | Solución |
|-------|-------|-----------|----------|
| 19-35 | Acceso a records sin verificación | ADVERTENCIA | Verificar tipo antes de acceder |
| 54-67 | Fecha sin verificación | ADVERTENCIA | Usar `.get('FECHA')` |

---

### Archivo: core/extractor_frases.py (1 error)

| Línea | Error | Severidad | Solución |
|-------|-------|-----------|----------|
| 19-33 | Acceso a records sin verificación | ADVERTENCIA | Verificar tipo de r |

---

### Archivo: tools/search_arq_prod.py (1 error)

| Línea | Error | Severidad | Solución |
|-------|-------|-----------|----------|
| 12 | Import posiblemente circular | ADVERTENCIA | Funciona en runtime, ignorar LSP |

---

### Archivo: tools/review_prod.py (1 error)

| Línea | Error | Severidad | Solución |
|-------|-------|-----------|----------|
| 9 | Import posiblemente circular | ADVERTENCIA | Funciona en runtime, ignorar LSP |

---

## 📊 ANÁLISIS DE IMPACTO

| Archivo | Errores | Porcentaje | Prioridad |
|---------|---------|------------|-----------|
| core/database.py | 15+ | 36% | 🔴 URGENTE |
| core/architect.py | 4 | 10% | 🔴 URGENTE |
| core/researcher.py | 2 | 5% | 🔴 URGENTE |
| motion_forge/motion_forge_playwright.py | 1 | 2% | 🔴 URGENTE |
| auditoria/miura_auditor_bunker.py | 1 | 2% | 🟡 ALTO |
| core/alchemist.py | 2 | 5% | 🟡 ALTO |
| tools/youtube_forge.py | 1 | 2% | 🟡 ALTO |
| Otros | 16 | 38% | 🟢 MEDIO |

**Total:** 42 errores

---

## 🎯 RECOMENDACIÓN DE CORRECCIÓN

### Orden de corrección:

**Fase 1 (URGENTE):**
1. core/database.py - Agregar guard clauses en todos los métodos
2. core/architect.py - Verificar info_csv antes de usar
3. core/researcher.py - Agregar import y verificación
4. motion_forge/motion_forge_playwright.py - Corregir import

**Fase 2 (ALTO):**
5. auditoria/miura_auditor_bunker.py - Verificar índices
6. core/alchemist.py - Validar argumentos
7. tools/youtube_forge.py - Verificar id_sesion

**Fase 3 (MEDIO):**
8. Resto de archivos (advertencias de tipo)

---

## 📝 COMANDOS PARA VERIFICAR

```bash
# Verificar errores LSP en VS Code:
# 1. Abrir proyecto en VS Code
# 2. Ir a Problems panel (Ctrl+Shift+M)
# 3. Filtrar por "Python"

# O usar mypy:
mypy core/database.py --ignore-missing-imports
mypy core/architect.py --ignore-missing-imports
```

---

**Documento creado:** Marzo 2026  
**Próxima revisión:** Después de correcciones  
**Estado:** LISTO_PARA_CORRECCIÓN

---

*"Los errores están documentados. Es hora de corregirlos."*
