# disciplinaenacero.com

Sitio web oficial de Disciplina en Acero.

## Estructura

```
disciplinaenacero/
├── index.html          ← Página principal
├── netlify.toml        ← Configuración Netlify
├── css/
│   └── main.css        ← Estilos globales
├── js/
│   └── main.js         ← Scripts globales
└── pages/
    ├── about.html      ← Doctrina / Nosotros
    ├── ebook.html      ← Página del libro (expectativa)
    ├── merch.html      ← Merchandising (próximamente)
    └── terminos.html   ← Términos y Condiciones
```

## Deploy en Netlify — Paso a paso

### Opción A: Arrastrar carpeta (más rápido)
1. Ve a https://app.netlify.com
2. Crea cuenta gratuita
3. En el dashboard haz clic en "Add new site" → "Deploy manually"
4. Arrastra la carpeta `disciplinaenacero/` completa
5. Netlify genera una URL temporal (ej: random-name.netlify.app)
6. En Site Settings → Domain Management → agrega `disciplinaenacero.com`

### Opción B: Vía GitHub (recomendada para actualizaciones futuras)
1. Crea repositorio privado en GitHub
2. Sube esta carpeta
3. En Netlify: "Import from Git" → conecta el repositorio
4. Cada push a `main` redespliega el sitio automáticamente

## Conectar dominio

En tu registrador de dominio (donde compraste disciplinaenacero.com):
- Cambia los nameservers a los de Netlify, o
- Agrega un registro CNAME: `www` → `[tu-sitio].netlify.app`
- Para el dominio raíz (@): agrega registro A → `75.2.60.5`

Netlify activa HTTPS automáticamente vía Let's Encrypt (gratis).

## Pendientes antes del lanzamiento

- [ ] Conectar formulario Lead Magnet → Brevo API o ImprovMX
- [ ] Agregar botón de PayPal en pages/ebook.html cuando el libro esté listo
- [ ] Configurar contacto@disciplinaenacero.com con ImprovMX
- [ ] Subir imagen real de portada del libro (reemplaza portada simulada)
- [ ] Activar Google Analytics o Plausible para métricas

## Correo con dominio propio

Opción rápida (reenvío) — ImprovMX:
1. Ve a https://improvmx.com
2. Agrega el dominio disciplinaenacero.com
3. Crea alias: contacto@ → tu Gmail personal
4. En tu registrador agrega los registros MX que ImprovMX indica
5. Listo en < 30 minutos

## Agregar PayPal cuando estés listo

En pages/ebook.html, reemplaza el botón "AVÍSAME" por el código
que genera PayPal en: paypal.com/buttons → "Buy Now"
Selecciona: producto digital, precio $9 USD, sin envío.
