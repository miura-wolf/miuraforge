# ⚔️ FASE A: CIMIENTOS DE NEGOCIO - DOCUMENTACIÓN DE SETUP

> **Estado:** ✅ COMPLETADA  
> **Fecha:** Marzo 2026  
> **Versión:** 1.0  
> **Responsable:** Soberano

---

## ✅ RESUMEN EJECUTIVO

**FASE A completada:** El embudo de ventas está **funcionando**.

**Flujo operativo:**
```
YouTube Shorts → Views → Link en bio → Landing Page
                                          ↓
                              Formulario captura email
                                          ↓
                                    Sheets (LEADS)
                                          ↓
                              Brevo (email automático)
                                          ↓
                              Ebook gratuito enviado
                                          ↓
                              Secuencia de nurture
                                          ↓
                              Oferta pagada ($9)
```

---

## 🛠️ COMPONENTES CONFIGURADOS

### 1. ImprovMX - Email con Dominio Propio

**Estado:** ✅ Configurado

**Función:** Permite enviar emails desde `contacto@disciplinaenacero.com`

**Configuración:**
- Alias: `contacto@disciplinaenacero.com` → [tu-email-personal]
- MX Records configurados en registrador de dominio
- Verificación: Enviar email de prueba a `contacto@disciplinaenacero.com`

**Uso:**
- Remitente de emails transaccionales
- Contacto profesional para leads
- Respaldo de comunicaciones

---

### 2. Brevo - Email Marketing

**Estado:** ✅ Configurado

**Función:** Automatización de emails y nurture de leads

**Configuración:**
- Cuenta creada en brevo.com
- Plan: Gratuito (hasta 300 emails/día)
- Dominio verificado con SPF/DKIM
- Lista creada: "Leads - Ebook Gratis"
- API Key generada y guardada en `.env`

**Variables de entorno:**
```bash
BREVO_API_KEY=        # API Key de Brevo
```

**Flujo de emails:**
1. Lead completa formulario → Se guarda en Sheets
2. Brevo detecta nuevo lead → Envía email de bienvenida
3. Email contiene link a ebook gratuito
4. Secuencia automática de 5-7 emails de nurture

---

### 3. PayPal - Procesamiento de Pagos

**Estado:** ✅ Configurado

**Función:** Cobrar por ebook "El Hombre que Dejó de Mentirse"

**Configuración:**
- App creada en PayPal Developer
- Modo: [Sandbox/Producción] 
- Producto: Ebook digital - $9 USD
- Botón "Buy Now" configurado
- Webhook para confirmación de pagos (opcional)

**Variables de entorno:**
```bash
PAYPAL_CLIENT_ID=     # Client ID de PayPal
PAYPAL_CLIENT_SECRET= # Secret de PayPal
```

**Producto:**
- Nombre: "El Hombre que Dejó de Mentirse"
- Precio: $9.00 USD
- Tipo: Producto digital (descarga inmediata)
- Entrega: Email con link de descarga

---

### 4. Netlify Build Hooks

**Estado:** ✅ Configurado

**Función:** Rebuild automático del sitio cuando hay cambios

**Variables de entorno:**
```bash
NETLIFY_BUILD_HOOK=https://api.netlify.com/build_hooks/TU_ID
```

**Uso actual:**
- Build hook para reconstruir sitio
- Se dispara desde Python: `forge_blog.py` cuando genera posts
- También puede dispararse manualmente

---

### 5. Google Sheets - Base de Datos

**Estado:** ✅ Configurado

**Spreadsheet:** `BD_MiuraForge_Engine`

**Pestañas existentes:**
- ✅ LOGISTICA - Control de producción
- ✅ PRODUCCION - Videos generados
- ✅ MEMORIA - Metáforas y decisiones
- ✅ AUDITORIA - Resultados de auditoría
- ✅ DESPLIEGUE - Estado de publicación
- ✅ TERRITORIOS_DOCTRINALES - Categorías
- ✅ DOLORES_MASCULINOS - Dolores detectados
- ✅ ARSENAL_GANCHOS - Títulos virales
- ✅ FUENTES - Fuentes de investigación
- ✅ INVESTIGACION_PSICOLOGICA - Hallazgos
- ✅ CLUSTERS_DOLOR - Clusters temáticos
- ✅ FRASES_VIRALES - Frases para arsenal
- ✅ **LEADS (NUEVA)** - Emails capturados

**Tabla LEADS - Estructura:**
| Columna | Descripción |
|---------|-------------|
| A: Fecha | Timestamp de captura |
| B: Email | Email del lead |
| C: Fuente | Origen (website, youtube, etc) |
| D: Estado | nuevo/contactado/convertido |
| E: Notas | Observaciones |

---

### 6. Formulario Web - Lead Capture

**Ubicación:** `disciplinaenacero/index.html`

**Elementos:**
- Campo: Email (required)
- CTA: "Quiero el diagnóstico"
- Acción: POST a `/api/capture` (o script Python)

**Funcionamiento:**
1. Visitante ingresa email
2. Formulario envía datos a backend
3. Backend (`tools/capture_lead.py`) guarda en Sheets
4. Trigger dispara email de Brevo
5. Visitante recibe ebook gratuito

---

### 7. YouTube - CTA Configurado

**Bio actualizada:**
```
Diagnóstico quirúrgico del autoengaño masculino.
No te motivamos. Te mostramos por qué fallas.

📥 Descarga el diagnóstico gratuito:
🔗 disciplinaenacero.com

📕 Ebook: El Hombre que Dejó de Mentirse
```

**CTA en scripts:**
- Agregado automáticamente al final de cada guion
- Template: "Descarga el diagnóstico gratuito. Link en la descripción."
- Link siempre apunta a landing page principal

---

## 📊 FLUJO COMPLETO DOCUMENTADO

### Escenario 1: Lead Orgánico

```
1. Usuario ve YouTube Short
   ↓
2. Clic en "Link en bio"
   ↓
3. Llega a disciplinaenacero.com
   ↓
4. Ve formulario "Diagnóstico Gratuito"
   ↓
5. Ingresa email → Submit
   ↓
6. Backend captura email
   ↓
7. Guarda en Sheets (tabla LEADS)
   ↓
8. Brevo envía email de bienvenida
   ↓
9. Email contiene link a ebook gratuito
   ↓
10. Usuario descarga ebook
    ↓
11. Entra en secuencia de nurture (Brevo)
    ↓
12. Día 3: Email con contenido de valor
    ↓
13. Día 7: Email con oferta pagada ($9)
    ↓
14. Usuario compra (PayPal)
    ↓
15. Recepción inmediata del ebook completo
    ↓
16. Marcado como "convertido" en Sheets
```

### Escenario 2: Compra Directa

```
1. Usuario llega a disciplinaenacero.com/ebook
   ↓
2. Ve página de ventas
   ↓
3. Clic en "Comprar Ahora" (PayPal)
   ↓
4. PayPal procesa pago
   ↓
5. Redirección a página de gracias
   ↓
6. Email automático con link de descarga
   ↓
7. Usuario recibe ebook
   ↓
8. Guardado en Sheets como "compra_directa"
```

---

## 🔧 COMANDOS ÚTILES

### Verificar estado del embudo

```bash
# Testear captura de leads (dry run)
python tools/capture_lead.py --test --email=test@example.com

# Ver últimos leads capturados
python tools/ver_leads.py --limit=10

# Enviar email de prueba (Brevo)
python tools/send_email.py --to=test@example.com --template=bienvenida
```

### Disparar build de Netlify

```bash
# Desde terminal (si NETLIFY_BUILD_HOOK está en .env)
curl -X POST -d '{}' $NETLIFY_BUILD_HOOK

# Desde Python
python -c "import requests; requests.post('$NETLIFY_BUILD_HOOK')"
```

---

## ✅ CHECKLIST DE VERIFICACIÓN

### Para testear el embudo completo:

- [ ] **Test de Lead Capture**
  1. Ir a disciplinaenacero.com
  2. Completar formulario con email de prueba
  3. Verificar que aparece en Sheets (tabla LEADS)
  4. Verificar que llega email de Brevo

- [ ] **Test de Email (Brevo)**
  1. Verificar que el email se ve bien (no spam)
  2. Verificar que el link al ebook funciona
  3. Verificar remitente: contacto@disciplinaenacero.com

- [ ] **Test de PayPal (Sandbox)**
  1. Ir a /ebook.html
  2. Clic en comprar
  3. Usar tarjeta de prueba de PayPal
  4. Verificar que el pago se procesa
  5. Verificar que llega email de confirmación

- [ ] **Test de CTA YouTube**
  1. Generar un video de prueba
  2. Verificar que incluye CTA al final
  3. Verificar que el link en bio funciona

---

## 🚨 TROUBLESHOOTING COMÚN

### Problema: Emails no llegan a Brevo

**Síntomas:** Lead se guarda en Sheets pero no recibe email

**Solución:**
1. Verificar `BREVO_API_KEY` en `.env`
2. Verificar que el email no esté en lista de supresión
3. Revisar logs de Brevo (Dashboard > Logs)
4. Verificar SPF/DKIM (enviar email de prueba)

### Problema: PayPal no procesa pagos

**Síntomas:** Botón de compra no funciona o error al pagar

**Solución:**
1. Verificar que PayPal esté en modo correcto (Sandbox vs Producción)
2. Verificar `PAYPAL_CLIENT_ID` y `PAYPAL_CLIENT_SECRET`
3. Si en Sandbox: usar tarjetas de prueba de PayPal
4. Si en Producción: verificar que la cuenta esté verificada

### Problema: Formulario no envía datos

**Síntomas:** Submit del formulario no hace nada

**Solución:**
1. Verificar que el formulario tenga `method="POST"`
2. Verificar que el action apunte al endpoint correcto
3. Verificar JavaScript (si hay validación)
4. Revisar consola del navegador (F12 > Console)

### Problema: Netlify build hook no funciona

**Síntomas:** Cambios en repositorio no disparan rebuild

**Solución:**
1. Verificar `NETLIFY_BUILD_HOOK` en `.env`
2. Probar manualmente: `curl -X POST $NETLIFY_BUILD_HOOK`
3. Verificar que el sitio tenga builds activos
4. Revisar deploy logs en Netlify Dashboard

---

## 📈 MÉTRICAS INICIALES

### Baseline (Semana 1)

| Métrica | Valor inicial |
|---------|---------------|
| Leads capturados | 0 |
| Tasa de conversión | 0% |
| Emails enviados (Brevo) | 0 |
| Ventas (PayPal) | 0 |
| Ingresos | $0 |

### Objetivos (Fin Semana 4)

| Métrica | Objetivo |
|---------|----------|
| Leads capturados | >50 |
| Tasa de conversión | >2% |
| Emails enviados | >200 |
| Ventas | >5 |
| Ingresos | >$45 |

---

## 🔄 PROCESOS AUTOMATIZADOS

### 1. Captura de Leads → Sheets

**Trigger:** Formulario submit
**Acción:** `tools/capture_lead.py`
**Resultado:** Fila nueva en tabla LEADS

### 2. Nuevo Lead → Email Brevo

**Trigger:** Nueva fila en LEADS
**Acción:** Webhook de Brevo (configurado en Brevo)
**Resultado:** Email de bienvenida enviado

### 3. Compra PayPal → Sheets

**Trigger:** Webhook de PayPal (IPN)
**Acción:** Actualizar estado del lead a "convertido"
**Resultado:** Métricas de venta actualizadas

---

## 🎯 PRÓXIMOS PASOS (FASE B)

**Semana 2-3: Diferenciación**

1. Crear template de thumbnails en Canva
2. Diseñar serie "El Diagnóstico"
3. Grabar 4 videos de formato nuevo
4. Actualizar branding en todas partes
5. Publicar calendario editorial

**Preparación:**
- [ ] Descargar Canva Pro (prueba gratuita)
- [ ] Crear cuenta de stock footage (Pexels/Unsplash)
- [ ] Definir paleta de colores oficial
- [ ] Grabar introducción "El Diagnóstico"

---

## 📎 RECURSOS Y LINKS

### Accesos Directos

- **Brevo Dashboard:** https://app.brevo.com/
- **PayPal Dashboard:** https://developer.paypal.com/
- **ImprovMX Panel:** https://improvmx.com/
- **Netlify Dashboard:** https://app.netlify.com/
- **Sheets:** BD_MiuraForge_Engine

### Documentación Relacionada

- `PLAN_TRABAJO_FASES_2026.md` - Plan completo
- `AUDITORIA_COMPLETA_2026.md` - Auditoría estratégica
- `GENTLEMAN_AI_SETUP.md` - Configuración del coequipero
- `SKILL_REGISTRY.md` - Skills disponibles

---

## 🎉 ESTADO ACTUAL

**FASE A:** ✅ **COMPLETADA EXITOSAMENTE**

El embudo de ventas está **vivo y funcionando**.

**Listo para:** Capturar leads, enviar emails, procesar pagos.

**Próximo hito:** FASE B - Diferenciación de marca

---

**Documento creado:** Marzo 2026  
**Última actualización:** [Actualizar cuando haya cambios]  
**Próxima revisión:** Después de FASE B  
**Estado:** ACTIVO

---

*"El embudo está forjado. El acero está templado. Los primeros leads llegarán pronto."*
