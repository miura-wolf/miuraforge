# ⚔️ Guía de Administración del Virtual Environment (venv) — MiuraForgeEngine

Soberano, para que su fragua nunca se contamine con herramientas externas y siempre use el combustible adecuado, debe manejar las instalaciones dentro del entorno virtual del proyecto.

## 1. El Problema: El Python "Global"
Si usa simplemente `pip install`, Windows lo instalará en la carpeta raíz de Python de su usuario (`C:\Users\...`), pero el **MiuraForgeEngine** está configurado para buscar sus piezas en la carpeta local `d:\YT\MiuraForge\venv`.

## 2. Cómo Instalar Correctamente (Windows)

Para instalar cualquier librería nueva (ejemplo: `playwright-stealth`) dentro de la fragua, use la ruta directa al ejecutable de la venv:

```powershell
.\venv\Scripts\python.exe -m pip install nombre-de-la-libreria
```

### Ejemplo Real:
Si quiere instalar `playwright-stealth`:
`.\venv\Scripts\python.exe -m pip install playwright-stealth`

---

## 3. Cómo Listar lo que hay en la Fragua
Para ver qué herramientas están realmente instaladas en el `venv` del proyecto:

```powershell
.\venv\Scripts\python.exe -m pip list
```

---

## 4. Playwright: El Motor de Navegación
Cuando instale librerías relacionadas con Playwright (como hizo con `playwright-stealth`), a veces es necesario instalar o actualizar los navegadores internos (Chromium):

```powershell
.\venv\Scripts\python.exe -m playwright install chromium
```

---

## 5. El Comodín: Activar la Venv (Opcional)
Si no quiere escribir la ruta larga cada vez, puede "entrar" en el entorno:

1. Ejecute: `.\venv\Scripts\Activate.ps1`
2. El terminal mostrará `(venv)` al inicio.
3. Ahora puede usar `pip install` normal mientras esté en esa sesión.
4. Para salir, escriba: `deactivate`

**Recomendación del Gran Visir:** Use siempre la ruta completa (`.\venv\Scripts\python.exe -m pip...`) para evitar confusiones de sesión. ⚒️🛡️
