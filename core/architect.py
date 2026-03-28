import os
import re
import pandas as pd
from llm.factory import LLMFactory
from llm.memory_manager import MemoryManager


class Architect:
    def __init__(self, db_manager):
        # El cerebro se pide dinámicamente según la factory
        self.brain = LLMFactory.get_brain("architect")
        self.db = db_manager
        self.memory = MemoryManager(db=self.db)
        self.knowledge_path = "knowledge/"

    def cargar_doctrina(self):
        """Prepara los manuales de Disciplina en Acero (devuelve rutas)."""
        print("📜 [Arquitecto] Preparando manuales de doctrina...")
        archivos = ["FUNDAMENTO.pdf", "PARALISIS.pdf", "ESTRATEGIA.pdf"]
        contexto_rutas = []

        for nombre in archivos:
            # os.path.abspath para asegurar que el provider lo encuentre
            ruta = os.path.abspath(os.path.join(self.knowledge_path, nombre))
            if os.path.exists(ruta):
                contexto_rutas.append(ruta)
            else:
                print(f"⚠️ [Arquitecto] No se encontró: {nombre}")
        return contexto_rutas

    def _extraer_inteligencia(self, tema_buscado):
        """Busca en el Puente de Mando (Sheets) los datos tácticos validados."""
        try:
            hallazgos_recientes = self.db.obtener_investigacion_reciente(tema_buscado)
            if hallazgos_recientes:
                h = hallazgos_recientes[0]  # El más reciente
                print(
                    f"🧠 [Arquitecto] Inteligencia recuperada de Sheets para: {tema_buscado}"
                )
                # Aseguramos que los campos existen y no son None antes de operar
                frases = h.get("FRASES_POTENTES") or ""
                creencias = h.get("CREENCIAS") or ""
                
                return {
                    "Frase Representativa": frases.split("|")[0].strip() if frases else "N/A",
                    "Por qué Paraliza": creencias.split(",")[0].strip() if creencias else "N/A",
                    "Oportunidad de Intervención para Short": h.get("DOLOR_PRINCIPAL") or "Desconocido",
                    "arquetipo_sugerido": h.get("ARQUETIPO_SUGERIDO") or "",
                    "fuente": "Sheets",
                }
        except Exception as e:
            print(f"⚠️ [Arquitecto] Error consultando inteligencia en Sheets: {e}")

        return None

    def _count_words(self, text):
        """Cuenta palabras de forma precisa (estándar Python)."""
        return len(text.strip().split())

    def redactar_guion_completo(
        self, tema_global, timestamp, data_estrategica=None, skip_approval=False
    ):
        """Forja el guion completo (3 fases) en una sola fila estratégica."""
        print(
            f"🔨 [Arquitecto] Forjando el BLOQUE DE ACERO completo para: {tema_global}"
        )

        # 1. Recuperar Inteligencia
        info_csv = self._extraer_inteligencia(tema_global)

        # 2. Cargar Instrucciones de Andrés (Manual de Tono)
        ruta_prompt = os.path.join("prompts", "arquitecto.txt")
        with open(ruta_prompt, "r", encoding="utf-8") as f:
            instrucciones_andres = f.read()

        # 3. Cargar ADN Doctrinal (Libro 1)
        adn_doctrinal = ""
        ruta_adn = os.path.join("doctrina", "libro1_adn.txt")
        if os.path.exists(ruta_adn):
            with open(ruta_adn, "r", encoding="utf-8") as f:
                adn_doctrinal = f.read()

        # 4. Construir el Contexto de Batalla
        contexto_real = ""
        if info_csv and isinstance(info_csv, dict):
            arquetipo_ancla = info_csv.get("arquetipo_sugerido") or ""
            contexto_real = f"""
            --- INTELIGENCIA DE CAMPO ---
            DOLOR DETECTADO: {info_csv.get("Oportunidad de Intervención para Short") or "Desconocido"}
            FRASE VIRAL ASOCIADA: "{info_csv.get("Frase Representativa") or "N/A"}"
            MECANISMO DE PARÁLISIS: {info_csv.get("Por qué Paraliza") or "N/A"}
            """
            if arquetipo_ancla:
                contexto_real += f"\nARQUETIPO ANCLA: {arquetipo_ancla}"
                contexto_real += f"\n(Úsalo como espejo del dolor si aporta fuerza al guion. Parafrasea el principio, nunca cites textual.)"

        doctrina = self.cargar_doctrina()

        # 5. Recuperar Memoria de Metáforas (Engram)
        palabras_prohibidas = self.memory.get_banned_str() if self.memory else ""

        # 6. Forja con la IA (Una sola llamada con instrucciones por fase)
        prompt_final = f"""
        {instrucciones_andres}
        
        --- ADN DOCTRINAL ---
        {adn_doctrinal}
        
        TEMA PRINCIPAL: {tema_global}
        {contexto_real}
        {f"ESTRUCTURA ADICIONAL: {data_estrategica}" if data_estrategica else ""}
        
        --- REGLAS DE FORJA POR FASE ---
        FASE 1 (La Ilusión): Ataca la mentira superficial. Usa la Frase Viral como ancla de dolor inicial.
        FASE 2 (La Resistencia - El Martillo): No repitas el problema. Usa el Mecanismo de Parálisis para explicarle al espectador por qué está bloqueado. Expón su cobardía mental.
        FASE 3 (El Nuevo Orden - La Orden Final): Dicta una sentencia final. Convierte la Oportunidad de Intervención en una orden física, seca y ejecutable AHORA. Sin rodeos.

        REGLA DE ORO: Genera el guion completo de forma percusiva (130-150 palabras).
        PALABRAS PROHIBIDAS (Metáforas gastadas): {palabras_prohibidas}
        """

        guion_ia = self.brain.generate(
            prompt_final,
            context_files=doctrina,
            temperature=0.3,
            reasoning_effort="low",
            top_p=0.9,
        )

        # VALIDACIÓN: Evitar guiones vacíos o fallos de filtro
        if not guion_ia or len(guion_ia.strip()) < 50:
            msg_error = "[GUION VACÍO — Requiere regeneración manual]"
            print(
                f"⚠️ [Arquitecto] El LLM devolvió contenido insuficiente para: {tema_global}"
            )
            self.db.guardar_fase(
                timestamp,
                "MASTER",
                msg_error,
                "Visual pendiente",
                "pendiente",
                estado="revision",
            )
            return msg_error

        # 5. Limpieza industrial de etiquetas (FASE 1, **FASE 2**, — FASE 3:, etc.)
        guion_ia = re.sub(
            r"(?i)\*?\*?\s*FASE\s+\d+\s*[:\-—]*\s*\*?\*?", "", guion_ia
        ).strip()
        guion_ia = re.sub(
            r"^[\s\-—]+", "", guion_ia, flags=re.M
        ).strip()  # Limpiar guiones al inicio de líneas

        # --- FILTRO DE PUREZA ANTES DE SUBIR ---
        basura_keywords = [
            "francés",
            "idioma",
            "anki",
            "duolingo",
            "puntuación global",
            "guion es operativo",
        ]
        es_basura = any(re.search(word, guion_ia, re.I) for word in basura_keywords)

        estado_registro = "RECHAZADO" if es_basura else "pendiente"
        contenido_subida = "[CENSURADO - CHATARRA]" if es_basura else guion_ia

        # 6. Registro inicial en PRODUCCION como MASTER
        self.db.guardar_fase(
            timestamp,
            "MASTER",
            contenido_subida,
            "Visual pendiente",
            "pendiente",
            estado=estado_registro,
        )

        if es_basura:
            return contenido_subida

        if not skip_approval:
            print(
                f"✅ [Arquitecto] Guion MASTER forjado. Soberano, revise la tabla PRODUCCION."
            )
            # Recuperar lo que el usuario pudo haber editado en Sheets
            guion_final = (
                self.db.obtener_guion_validado(timestamp, "MASTER") or guion_ia
            )
        else:
            guion_final = guion_ia

        self._aprender_metaphoras(guion_final)
        return guion_final

    def _aprender_metaphoras(self, texto_guion):
        """Extrae y guarda metáforas para no repetirlas."""
        extract_prompt = f"Extrae solo 3 metáforas clave de este texto (ej: 'anestesia', 'tumba'). Solo palabras, separadas por coma: {texto_guion}"
        try:
            # Usamos el cerebro para extraer
            palabras = self.brain.generate(
                extract_prompt,
                temperature=0.25,
                reasoning_effort="low",
                top_p=0.9,
                frequency_penalty=0.4,
                presence_penalty=0.1,
            )
            if palabras:
                lista_palabras = [p.strip() for p in palabras.split(",") if p.strip()]
                self.memory.update_metaphors(lista_palabras)
        except Exception as e:
            print(f"⚠️ [Arquitecto] Error en memoria: {e}")
