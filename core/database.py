from typing import Optional
import re

import gspread
from gspread.worksheet import Worksheet
from oauth2client.service_account import ServiceAccountCredentials
from tenacity import retry, stop_after_attempt, wait_exponential
from core.config import CREDENTIALS_PATH


class Database:
    # Type hints para los worksheets
    logistica: Optional[Worksheet]
    produccion: Optional[Worksheet]
    memoria: Optional[Worksheet]
    auditoria: Optional[Worksheet]
    despliegue: Optional[Worksheet]
    territorios: Optional[Worksheet]
    dolores: Optional[Worksheet]
    ganchos: Optional[Worksheet]
    fuentes: Optional[Worksheet]
    investigacion: Optional[Worksheet]
    clusters: Optional[Worksheet]
    frases: Optional[Worksheet]
    blog_contenido: Optional[Worksheet]

    def __init__(self, spreadsheet_name="BD_MiuraForge_Engine"):
        # Configuración de acceso
        scope = [
            "https://spreadsheets.google.com/feeds",
            "https://www.googleapis.com/auth/drive",
        ]
        try:
            creds = ServiceAccountCredentials.from_json_keyfile_name(str(CREDENTIALS_PATH), scope)
            self.client = gspread.authorize(creds)
            self.sheet = self.client.open(spreadsheet_name)

            # Conectamos las hojas del Imperio de manera resiliente
            all_worksheets = {w.title.strip(): w for w in self.sheet.worksheets()}

            self.logistica = all_worksheets.get("LOGISTICA")
            self.produccion = all_worksheets.get("PRODUCCION")
            self.memoria = all_worksheets.get("MEMORIA")
            self.auditoria = all_worksheets.get("AUDITORIA")
            self.despliegue = all_worksheets.get("DESPLIEGUE")
            self.territorios = all_worksheets.get("TERRITORIOS_DOCTRINALES")
            self.dolores = all_worksheets.get("DOLORES_MASCULINOS")
            self.ganchos = all_worksheets.get("ARSENAL_GANCHOS")
            self.fuentes = all_worksheets.get("FUENTES")
            self.investigacion = all_worksheets.get("INVESTIGACION_PSICOLOGICA")
            self.clusters = all_worksheets.get("CLUSTERS_DOLOR")
            self.frases = all_worksheets.get("FRASES_VIRALES")
            self.blog_contenido = all_worksheets.get("BLOG_CONTENIDO")

            # Inicializar Cache para velocidad (Columna 1 = URL en FUENTES)
            if self.fuentes:
                try:
                    self.urls_cache = set(self.fuentes.col_values(1))
                except:
                    self.urls_cache = set()
            else:
                self.urls_cache = set()

            if not all([self.logistica, self.produccion, self.fuentes]):
                print("⚠️ [Database] Faltan tablas críticas en el Puente de Mando.")

            # --- ESCUDO DE ESTRUCTURA (Fase IMP) ---
            self._activar_escudo_estructura()

            if not self.investigacion:
                print("⚠️ [Database] Tabla INVESTIGACION_PSICOLOGICA no vinculada.")

            print("✅ [Database] Conexión establecida y Puente de Mando blindado.")
        except Exception as e:
            print(f"❌ [Database] Error de conexión: {e}")

    def _activar_escudo_estructura(self):
        """Asegura que las cabeceras de todas las tablas sean las correctas (Fase IMP)."""
        mapeo_maestro = {
            "LOGISTICA": ["ID_Sesion", "Tema", "Fecha", "Estado", "Metricas"],
            "PRODUCCION": [
                "ID_Sesion",
                "Fase",
                "Guion",
                "Prompt_Visual",
                "Voz_Status",
                "Estado",
            ],
            "MEMORIA": ["Metafora"],
            "AUDITORIA": [
                "ID_Master",
                "Guion_Original",
                "Guion_Optimizado",
                "Intensidad",
                "Ritmo",
                "Coherencia",
                "ADN",
                "Fallas",
                "Ajustes",
                "Fecha",
            ],
            "FUENTES": [
                "ID",
                "ID_SESION",
                "PLATAFORMA",
                "ORIGEN",
                "URL",
                "AUTOR",
                "ENGAGEMENT",
                "FECHA",
                "QUERY",
                "FECHA_EXTRACCION",
            ],
            "INVESTIGACION_PSICOLOGICA": [
                "ID_SEMANA",
                "TEMA",
                "DOLOR_PRINCIPAL",
                "PROBLEMA_RAIZ",
                "FRASES_POTENTES",
                "CREENCIAS",
                "SOLUCION_MIURA",
                "PLATAFORMA",
                "FECHA",
                "ARQUETIPO_SUGERIDO",
            ],
            "DOLORES_MASCULINOS": [
                "ID_DOLOR",
                "CATEGORIA",
                "DESCRIPCION",
                "CREENCIAS",
                "VERDAD",
                "INTENSIDAD",
                "FRECUENCIA",
                "EJEMPLO",
            ],
            "ARSENAL_GANCHOS": [
                "GANCHO",
                "PLANTILLA",
                "INTENSIDAD",
                "ID_SESION",
                "FECHA",
            ],
            "CLUSTERS_DOLOR": [
                "cluster_id",
                "nombre_cluster",
                "frecuencia",
                "temas_relacionados",
                "frase_dominante",
                "ultima_actualizacion",
                "freq_7d",
                "freq_30d",
                "tendencia_estado",
            ],
            "FRASES_VIRALES": [
                "id_frase",
                "frase",
                "dolor_asociado",
                "plataforma",
                "tema",
            ],
            "BLOG_CONTENIDO": [
                "ID",
                "Estado",
                "Título",
                "Slug",
                "Fecha",
                "Descripción",
                "Keywords",
                "Categoría",
                "Imagen_URL",
                "Enlace_Afiliado",
                "Cuerpo_Raw",
                "Tags",
                "ReadTime_Min",
                "Featured",
                "ANCLA_VERDAD",
                "LIBRO_ESTADO"
            ],
        }

        # Obtenemos lista real de títulos para evitar duplicados
        titulos_reales = {w.title.strip().upper(): w for w in self.sheet.worksheets()}

        for nombre_oficial, headers_esperados in mapeo_maestro.items():
            nombre_upper = nombre_oficial.upper()
            ws = titulos_reales.get(nombre_upper)

            try:
                if not ws:
                    print(f"🔨 [Escudo] Forjando nueva tabla estratégica: {nombre_oficial}")
                    ws = self.sheet.add_worksheet(
                        title=nombre_oficial,
                        rows="1000",
                        cols=str(len(headers_esperados)),
                    )
                    ws.update("A1", [headers_esperados])
                    # Actualizamos el atributo correspondiente si existe
                    attr_map = {
                        "PRODUCCION": "produccion",
                        "LOGISTICA": "logistica",
                        "MEMORIA": "memoria",
                        "AUDITORIA": "auditoria",
                        "FUENTES": "fuentes",
                        "INVESTIGACION_PSICOLOGICA": "investigacion",
                        "ARSENAL_GANCHOS": "ganchos",
                        "CLUSTERS_DOLOR": "clusters",
                        "FRASES_VIRALES": "frases",
                        "BLOG_CONTENIDO": "blog_contenido",
                    }
                    if nombre_upper in attr_map:
                        setattr(self, attr_map[nombre_upper], ws)
                else:
                    actuales = [h.strip() for h in ws.row_values(1) if h.strip()]
                    actuales_upper = [h.upper() for h in actuales]
                    esperados_upper = [h.upper() for h in headers_esperados]

                    # Detectar columnas nuevas que faltan en la hoja existente
                    faltantes = [h for h, hu in zip(headers_esperados, esperados_upper) if hu not in actuales_upper]

                    if faltantes:
                        print(f"🔩 [Escudo] Agregando {len(faltantes)} columnas nuevas a {nombre_oficial}: {faltantes}")
                        # Expandir worksheet si hace falta
                        cols_actuales = ws.col_count
                        cols_necesarias = len(actuales) + len(faltantes)
                        if cols_necesarias > cols_actuales:
                            ws.resize(cols=cols_necesarias)
                        # Escribir los headers faltantes al final de la fila 1
                        for idx, header in enumerate(faltantes):
                            col_pos = len(actuales) + idx + 1
                            ws.update_cell(1, col_pos, header)
                    elif actuales_upper != esperados_upper:
                        print(f"🛠️ [Escudo] Restaurando estructura en: {nombre_oficial}")
                        ws.update("1:1", [[""] * len(actuales)])
                        ws.update("A1", [headers_esperados])
            except Exception as e:
                print(f"⚠️ [Escudo] Error vigilando {nombre_oficial}: {e}")

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def registrar_hallazgos(self, id_sesion, hallazgos):
        """
        Registra fuentes en la hoja FUENTES con alineación total a la estructura histórica.
        Formato: ID | ID_SESION | PLATAFORMA | ORIGEN | URL | AUTOR | ENGAGEMENT | FECHA | QUERY | FECHA_EXTRACCION
        """
        if not self.fuentes:
            return
        import datetime

        ahora = datetime.datetime.now()
        fecha_str = ahora.strftime("%Y-%m-%d %H:%M")

        try:
            if not self.urls_cache:
                self.urls_cache = set(
                    self.fuentes.col_values(5)
                )  # URL está en la Col E (5) según el nuevo mapeo

            filas_nuevas = []
            for i, h in enumerate(hallazgos):
                url = h.get("url")
                if url in self.urls_cache:
                    continue

                # Generamos ID único: ID_SESION + Secuencia
                row_id = f"{id_sesion}_{ahora.strftime('%H%M%S')}_{i}"

                # Mapeo: ID (A), ID_SESION (B), PLATAFORMA (C), ORIGEN (D), URL (E), AUTOR (F), ENGAGEMENT (G), FECHA (H), QUERY (I), FECHA_EXTRACCION (J)
                fila = [
                    row_id,
                    id_sesion,
                    h.get("platform", "desconocido"),
                    h.get("source", "web"),  # ORIGEN
                    url,
                    h.get("author", "N/A"),
                    h.get("engagement", 0),
                    fecha_str,
                    h.get("query", "N/A"),
                    fecha_str,  # FECHA_EXTRACCION
                ]
                filas_nuevas.append(fila)
                self.urls_cache.add(url)

            if filas_nuevas:
                self.fuentes.append_rows(filas_nuevas)
                print(
                    f"📊 [Database] {len(filas_nuevas)} hallazgos registrados con trazabilidad total."
                )
        except Exception as e:
            print(f"⚠️ [Database] Error en registro de hallazgos: {e}")

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def registrar_investigacion_psicologica(self, id_semana, hallazgos, tema="N/A"):
        """
        Registra el análisis profundo en INVESTIGACION_PSICOLOGICA.
        Alineado con: ID_SEMANA | TEMA | DOLOR_PRINCIPAL | PROBLEMA_RAIZ | FRASES_POTENTES | CREENCIAS | SOLUCION_MIURA | PLATAFORMA | FECHA
        """
        if not self.investigacion:
            return
        import datetime

        fecha = str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M"))
        filas = []
        for i, h in enumerate(hallazgos):
            filas.append(
                [
                    id_semana,
                    tema,
                    h.get("dolor_principal", "N/A"),
                    h.get("problema_raiz", h.get("problema_principal", "N/A")),
                    " | ".join(h.get("frases_potentes", [])),
                    ", ".join(h.get("creencias", [])),
                    h.get("solucion_miura", "N/A"),
                    h.get("platform", "desconocido"),
                    fecha,
                    h.get("arquetipo_sugerido", ""),
                ]
            )
        if filas:
            self.investigacion.append_rows(filas)
            print(f"🧠 [Database] {len(filas)} análisis psicológicos registrados para: {tema}")

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def actualizar_dolor(self, dolor_nombre):
        """
        Actualiza la frecuencia en DOLORES_MASCULINOS or lo registra si es nuevo.
        Alineado con columnas: CATEGORIA (B), FRECUENCIA_CONTENIDO (G/Col 7)
        """
        if not self.dolores:
            return
        try:
            records = self.dolores.get_all_records()
            found_idx = -1
            for i, row in enumerate(records):
                # Buscamos en CATEGORIA (segunda columna)
                if str(row.get("CATEGORIA", "")).lower() == dolor_nombre.lower():
                    found_idx = i + 2  # +1 header, +1 idx list
                    break

            if found_idx != -1:
                # FRECUENCIA_CONTENIDO es la columna 7
                curr_val = self.dolores.cell(found_idx, 7).value
                curr = int(curr_val) if curr_val and str(curr_val).isdigit() else 0
                self.dolores.update_cell(found_idx, 7, curr + 1)
                print(f"🔥 [Database] Frecuencia de '{dolor_nombre}' incrementada.")
            else:
                # Si no existe, lo añadimos con ID correlativo si es posible
                last_id = f"D{len(records) + 1:02d}"
                # Estructura: ID_DOLOR, CATEGORIA, DESCRIPCION, CREENCIAS, VERDAD, INTENSIDAD, FRECUENCIA, EJEMPLO
                nueva_fila = [
                    last_id,
                    dolor_nombre,
                    "Extraído vía OSINT",
                    "",
                    "",
                    "8",
                    1,
                    "Pendiente",
                ]
                self.dolores.append_row(nueva_fila)
                print(f"🆕 [Database] Nuevo dolor detectado y registrado: {dolor_nombre}")
        except Exception as e:
            print(f"⚠️ [Database] Error actualizando radar de dolor: {e}")

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def registrar_ganchos(self, id_sesion, titulos_por_plantilla):
        """Registra los 30 ganchos virales en ARSENAL_GANCHOS."""
        if not self.ganchos:
            return
        import datetime

        fecha = str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M"))
        filas = []
        for plantilla, titulos in titulos_por_plantilla.items():
            for t in titulos:
                filas.append([t, plantilla, id_sesion, fecha])

        if filas:
            self.ganchos.append_rows(filas)
            print(f"🎯 [Database] {len(filas)} ganchos virales forjados en el Arsenal.")

    # --- MÉTODOS DE EXPANSIÓN DOCTRINAL ---

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def obtener_territorios(self):
        """Recupera la lista de territorios doctrinales."""
        if not self.territorios:
            return []
        return self.territorios.get_all_records()

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def obtener_dolores(self):
        """Recupera la biblioteca de dolores masculinos."""
        if not self.dolores:
            return []
        return self.dolores.get_all_records()

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def registrar_ganchos_competencia(self, id_sesion, ganchos_data):
        """Registra ganchos extraídos de la competencia en ARSENAL_GANCHOS."""
        if not self.ganchos:
            return
        import datetime

        fecha = str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M"))
        # Estructura: GANCHO | PLANTILLA | INTENSIDAD | ID_SESION | FECHA
        fila = [
            ganchos_data.get("titulo_maestro", "N/A"),
            ganchos_data.get("plantilla", ganchos_data.get("estructura", "N/A")),
            ganchos_data.get("intensidad", "N/A"),
            id_sesion,
            fecha,
        ]
        self.ganchos.append_row(fila)
        print(
            f"🎯 [Database] Gancho de competencia registrado con intensidad {ganchos_data.get('intensidad')}."
        )

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def obtener_ganchos(self):
        """Recupera el arsenal de hooks estratégicos."""
        if not self.ganchos:
            return []
        return self.ganchos.get_all_records()

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def obtener_investigacion_reciente(self, tema, limite=5):
        """Recupera los hallazgos más recientes de la tabla INVESTIGACION_PSICOLOGICA."""
        if not self.investigacion:
            return []
        try:
            records = self.investigacion.get_all_records()
            # Filtramos por tema (búsqueda aproximada en dolor_principal o frases)
            filtrados = []
            for r in reversed(records):  # Los más recientes primero
                if (
                    tema.lower() in str(r.get("DOLOR_PRINCIPAL", "")).lower()
                    or tema.lower() in str(r.get("FRASES_POTENTES", "")).lower()
                ):
                    filtrados.append(r)
                if len(filtrados) >= limite:
                    break
            return filtrados
        except Exception as e:
            print(f"⚠️ [Database] Error recuperando investigación: {e}")
            return []

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def registrar_despliegue(self, data):
        """Registra el paquete de lanzamiento en la tabla DESPLIEGUE."""
        if not self.despliegue:
            return
        # Columnas: ID_MASTER, TITULO_GOLPE, SUBTITULO_REFUERZO, DESCRIPCION_ACERO, HASHTAGS_TACTICOS,
        # GANCHO_VISUAL_0_3, CTA_PRINCIPAL, TERRITORIO_DOCTRINAL, HORA_LANZAMIENTO, ESTADO_DESPLIEGUE
        import datetime

        hora = str(datetime.datetime.now().strftime("%H:%M:%S"))
        fila = [
            data.get("id_master"),
            data.get("titulo"),
            data.get("subtitulo", ""),
            data.get("descripcion"),
            data.get("hashtags"),
            data.get("gancho"),
            data.get("cta"),
            data.get("territorio"),
            hora,
            "PENDIENTE",
        ]
        self.despliegue.append_row(fila)
        print(f"🚀 [Database] Paquete de despliegue registrado para {data.get('id_master')}.")

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def obtener_datos_despliegue(self, id_master):
        """Intenta recuperar el paquete de despliegue (Hook, CTA, Titulo) desde Google Sheets."""
        if not self.despliegue:
            return None
        try:
            records = self.despliegue.get_all_records()
            for r in reversed(records):
                if str(r.get("ID_MASTER", "")).strip() == str(id_master).strip():
                    return r
        except Exception as e:
            print(f"⚠️ [Database] Error recuperando datos de despliegue: {e}")
        return None

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def registrar_auditoria_inicial(self, id_master, guion_original):
        """Prepara el registro de auditoría en Sheets sin crear duplicados."""
        if not self.auditoria:
            return
        import datetime

        fecha = str(datetime.datetime.now())
        id_str = str(id_master).strip()

        try:
            # Verificar si ya existe el ID
            all_ids = self.auditoria.col_values(1)
            for i, val in enumerate(all_ids):
                if str(val).strip() == id_str:
                    # Si ya existe, actualizamos el guion original por si cambió
                    self.auditoria.update_cell(i + 1, 2, guion_original)
                    self.auditoria.update_cell(i + 1, 10, fecha)
                    return

            # Si no existe, creamos la fila
            fila = [id_master, guion_original, "", "", "", "", "", "", "", fecha]
            self.auditoria.append_row(fila)
        except Exception as e:
            print(f"⚠️ [Database] Error registrando auditoría inicial: {e}")

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def actualizar_resultados_auditoria(self, id_master, resultados):
        """Vuelca los resultados del Auditor Bunker en Sheets con filtrado de pureza."""
        if not self.auditoria:
            return
        id_str = str(id_master).strip()

        # --- FILTRO DE PUREZA ANTES DE ESCRIBIR ---
        guion_opt = resultados.get("guion_optimizado", "").strip()
        basura_patterns = [
            r"puntuación global",
            r"supera el umbral",
            r"guion es operativo",
            r"ya es óptimo",
            r"fase individual",
            r"francés",
            r"idioma",
            r"anki",
        ]

        es_basura = any(re.search(p, guion_opt, re.I) for p in basura_patterns)
        if not guion_opt or len(guion_opt.split()) < 10:
            es_basura = True

        if not self.auditoria:
            return
        try:
            # 1. Actualizar tabla AUDITORIA
            all_ids = self.auditoria.col_values(1)
            row_idx = -1
            for i, val in enumerate(all_ids):
                if str(val).strip() == id_str:
                    row_idx = i + 1
                    break

            if row_idx != -1:
                # Si es basura, ponemos un aviso en lugar de la basura
                contenido_final = "[CENSURADO - FUERA DE FOCO]" if es_basura else guion_opt
                self.auditoria.update_cell(row_idx, 3, contenido_final)
                self.auditoria.update_cell(row_idx, 4, resultados.get("intensidad", "0"))
                self.auditoria.update_cell(row_idx, 5, resultados.get("ritmo", "0"))
                self.auditoria.update_cell(row_idx, 6, resultados.get("coherencia", "0"))
                self.auditoria.update_cell(row_idx, 7, resultados.get("adn_acero", "0"))
                self.auditoria.update_cell(
                    row_idx,
                    8,
                    resultados.get("fallas", "RECHAZADO AUTOMÁTICAMENTE" if es_basura else ""),
                )
                self.auditoria.update_cell(
                    row_idx,
                    9,
                    "ELIMINAR - CHATARRA" if es_basura else resultados.get("ajustes", ""),
                )
                print(f"✅ [Database] Auditoría del MASTER {id_master} sincronizada.")

                # 2. Si es basura, RECHAZAR en PRODUCCION inmediatamente
                if es_basura and self.produccion:
                    cell = self.produccion.find(id_str)
                    if cell:
                        # Columna 3 es Guion, Columna 6 es Estado
                        self.produccion.update_cell(cell.row, 3, "[CHATARRA ELIMINADA]")
                        self.produccion.update_cell(cell.row, 6, "RECHAZADO")
                        print(
                            f"🗑️ [Database] Registro {id_master} marcado como RECHAZADO por chatarra."
                        )
            else:
                print(f"⚠️ [Database] No se encontró el ID {id_master} en AUDITORIA.")
        except Exception as e:
            print(f"❌ [Database] Error actualizando auditoría: {e}")

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def obtener_guion_optimizado(self, id_master):
        """Recupera la versión refinada por el Auditor."""
        if not self.auditoria:
            return None
        all_values = self.auditoria.get_all_values()
        if not all_values:
            return None
        for row in all_values[1:]:
            if str(row[0]) == str(id_master):
                return row[2]  # GUION_OPTIMIZADO
        return None

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def obtener_resultados_auditoria(self, id_master):
        """
        Lee la fila de AUDITORIA con el ID dado y devuelve las métricas
        necesarias para el filtro de calidad del dataset de fine-tuning.
        """
        if not self.auditoria:
            return {}
        try:
            all_rows = self.auditoria.get_all_records()
            for row in all_rows:
                if str(row.get("ID_Master", "")).strip() == str(id_master).strip():
                    return {
                        "coherencia": row.get("Coherencia", 0),
                        "adn_acero": row.get("ADN", 0),
                        "intensidad": row.get("Intensidad", 0),
                        "ritmo": row.get("Ritmo", 0),
                    }
            return {}
        except Exception as e:
            print(f"⚠️ [Database] Error leyendo AUDITORIA para {id_master}: {e}")
            return {}

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def registrar_sesion(self, timestamp, tema, categoria):
        """Registra el inicio de una nueva forja en LOGISTICA."""
        if not self.logistica:
            print("⚠️ [Database] LOGISTICA no disponible para registro de sesión.")
            return
        nueva_fila = [timestamp, tema, categoria, "Guion Pendiente", "TBD"]
        self.logistica.append_row(nueva_fila)

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def guardar_fase(self, timestamp, fase, guion, visual, ruta_local, estado="pendiente"):
        """Vuelca el acero en la hoja de PRODUCCION de manera inteligente."""
        if not self.produccion:
            print("⚠️ [Database] PRODUCCION no disponible para guardar fase.")
            return
        try:
            all_values = self.produccion.get_all_values()

            if not all_values:
                # Si está vacío, simplemente añadimos
                nueva_fila = [timestamp, fase, guion, visual, ruta_local, estado]
                self.produccion.append_row(nueva_fila)
                return

            headers = all_values[0]
            try:
                idx_id = (
                    headers.index("ID")
                    if "ID" in headers
                    else headers.index("ID_Sesion")
                    if "ID_Sesion" in headers
                    else 0
                )
                idx_fase = headers.index("Fase") if "Fase" in headers else 1
            except ValueError:
                idx_id, idx_fase = 0, 1

            row_to_update = -1
            for i, row in enumerate(all_values):
                if i == 0:
                    continue
                if len(row) > max(idx_id, idx_fase):
                    if str(row[idx_id]) == str(timestamp) and str(row[idx_fase]) == str(fase):
                        row_to_update = i + 1  # +1 porque sheets es 1-indexed
                        break

            if row_to_update != -1:
                # Actualizamos Guion (3), Visual (4), Ruta (5), Estado (6)
                try:
                    col_guion = (headers.index("Guion") if "Guion" in headers else 2) + 1
                except:
                    col_guion = 3
                try:
                    col_visual = (headers.index("Visual") if "Visual" in headers else 3) + 1
                except:
                    col_visual = 4
                try:
                    col_ruta = (headers.index("Ruta") if "Ruta" in headers else 4) + 1
                except:
                    col_ruta = 5
                try:
                    col_estado = (headers.index("Estado") if "Estado" in headers else 5) + 1
                except:
                    col_estado = 6

                self.produccion.update_cell(row_to_update, col_guion, guion)
                self.produccion.update_cell(row_to_update, col_visual, visual)
                self.produccion.update_cell(row_to_update, col_ruta, ruta_local)
                self.produccion.update_cell(row_to_update, col_estado, estado)
                print(f"🔄 [Database] Entrada {fase} actualizada.")
            else:
                nueva_fila = [timestamp, fase, guion, visual, ruta_local, estado]
                self.produccion.append_row(nueva_fila)
        except Exception as e:
            print(f"⚠️ [Database] Error en guardar_fase: {e}")
            raise e

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def obtener_master_aprobado(self, timestamp):
        """Busca en PRODUCCION el guion MASTER aprobado pero con visual pendiente."""
        if not self.produccion:
            return None
        try:
            all_values = self.produccion.get_all_values()
            if not all_values:
                return None

            headers = all_values[0]
            try:
                idx_id = headers.index("ID") if "ID" in headers else 0
                idx_fase = headers.index("Fase") if "Fase" in headers else 1
                idx_guion = headers.index("Guion") if "Guion" in headers else 2
                idx_visual = headers.index("Visual") if "Visual" in headers else 3
                idx_estado = headers.index("Estado") if "Estado" in headers else 5
            except ValueError:
                idx_id, idx_fase, idx_guion, idx_visual, idx_estado = 0, 1, 2, 3, 5

            for row in all_values[1:]:
                if len(row) > max(idx_id, idx_fase, idx_guion, idx_visual, idx_estado):
                    if str(row[idx_id]) == str(timestamp) and str(row[idx_fase]) == "MASTER":
                        if str(row[idx_estado]).lower() == "aprobado":
                            return {
                                "guion": row[idx_guion],
                                "visual_actual": row[idx_visual],
                            }
        except Exception as e:
            print(f"⚠️ [Database] Error buscando Master: {e}")
        return None

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def obtener_guion_validado(self, timestamp, fase_num):
        """
        Busca en PRODUCCION el guion de la fase.
        Permite que el Soberano edite la celda en Sheets antes de seguir.
        """
        if not self.produccion:
            return None
        try:
            # Obtenemos todos los registros incluyendo cabeceras para depurar
            all_values = self.produccion.get_all_values()
            if not all_values:
                return None

            headers = all_values[0]
            # Buscamos índices de columnas para no depender de nombres exactos
            try:
                idx_id = (
                    headers.index("ID")
                    if "ID" in headers
                    else headers.index("ID_Sesion")
                    if "ID_Sesion" in headers
                    else 0
                )
                idx_fase = headers.index("Fase") if "Fase" in headers else 1
                idx_guion = headers.index("Guion") if "Guion" in headers else 2
            except ValueError:
                # Si fallan las cabeceras, usamos valores por defecto
                idx_id, idx_fase, idx_guion = 0, 1, 2

            for row in all_values[1:]:
                if len(row) > max(idx_id, idx_fase, idx_guion):
                    if str(row[idx_id]) == str(timestamp) and str(row[idx_fase]) == str(fase_num):
                        return row[idx_guion]
        except Exception as e:
            print(f"⚠️ [Database] Error en validación (Reintentando): {e}")
            raise e
        return None

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def actualizar_estado_logistica(self, timestamp, nuevo_estado):
        """Actualiza el estado global de la sesión."""
        if not self.logistica:
            return
        cell = self.logistica.find(str(timestamp))
        if cell:
            self.logistica.update_cell(cell.row, 4, nuevo_estado)

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def obtener_memoria_global(self):
        """Recupera todas las metáforas prohibidas desde la pestaña MEMORIA."""
        if not self.memoria:
            return []
        try:
            # Traemos todo como una lista plana
            all_rows = self.memoria.get_all_values()
            # Aplanamos la lista de listas y filtramos vacíos
            flat_list = [item for sublist in all_rows for item in sublist if item]
            return list(set([m.strip().lower() for m in flat_list]))
        except Exception as e:
            print(f"⚠️ [Database] Error en memoria global (Reintentando): {e}")
            raise e

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def agregar_a_memoria_global(self, nuevas_metaforas):
        """Añade nuevas metáforas a la pestaña MEMORIA."""
        if not self.memoria or not nuevas_metaforas:
            return
        try:
            filas = [[m.strip().lower()] for m in nuevas_metaforas if m.strip()]
            if filas:
                self.memoria.append_rows(filas)
                print(
                    f"📖 [Database] {len(filas)} nuevas metáforas registradas en la Memoria Global."
                )
        except Exception as e:
            print(f"⚠️ [Database] Error guardando en memoria global: {e}")
            raise e

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def obtener_titulo_video(self, timestamp):
        """Busca un título amigable para el archivo: primero en DESPLIEGUE, luego en LOGISTICA."""
        if not any([self.despliegue, self.logistica]):
            return None
        ts_str = str(timestamp).strip()
        
        # 1. Intentar en DESPLIEGUE (es el título real del video)
        if self.despliegue:
            try:
                records = self.despliegue.get_all_records()
                for r in reversed(records):
                    if str(r.get("ID_MASTER", "")).strip() == ts_str:
                        return r.get("TITULO_GOLPE")
            except:
                pass

        # 2. Fallback a LOGISTICA (es el tema o cluster)
        if self.logistica:
            try:
                records = self.logistica.get_all_records()
                for r in reversed(records):
                    # En logística la columna suele ser ID_Sesion o ID
                    id_val = r.get("ID_Sesion") or r.get("ID") or r.get("timestamp")
                    if str(id_val).strip() == ts_str:
                        return r.get("Tema") or r.get("tema")
            except:
                pass

        return None
