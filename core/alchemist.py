import os
from google.genai import Client
from dotenv import load_dotenv

load_dotenv()

import json
import re

# ---------------------------------------------------------------------------
# ARQUETIPOS DE FICCIÓN — Personajes cuya muerte, caída o redención
# encarna principios de Disciplina en Acero.
# REGLA DE USO: Nunca citar textual. Siempre parafrasear el principio
# y atribuir el personaje como ejemplo cultural. Esto no es reproducción
# de guion — es análisis filosófico aplicado.
# ---------------------------------------------------------------------------
ARQUETIPOS_FICCION = [
    {
        "personaje": "Arthur Morgan",
        "obra": "Red Dead Redemption 2",
        "tipo": "videojuego",
        "principio": "Un hombre que vivió para otros descubre, al morir, que nunca se eligió a sí mismo. La redención llega demasiado tarde para cambiar el pasado, pero a tiempo para morir con honor.",
        "tension_doctrinal": "silencio acumulado, identidad construida para sobrevivir, el precio del rol",
    },
    {
        "personaje": "Joel Miller",
        "obra": "The Last of Us",
        "tipo": "videojuego",
        "principio": "Un hombre que perdió todo decide que sobrevivir no es suficiente — necesita algo por lo que luchar. El problema es que confunde proteger con controlar.",
        "tension_doctrinal": "propósito instalado por miedo, el proveedor invisible, la máscara del protector",
    },
    {
        "personaje": "Walter White",
        "obra": "Breaking Bad",
        "tipo": "serie",
        "principio": "Un hombre que nunca se reclamó a sí mismo en vida decide hacerlo a través de la destrucción. La identidad que construyó era tan falsa que solo pudo revelar la real destruyendo todo lo demás.",
        "tension_doctrinal": "identidad falsa, valor fusionado con producción, máscara que se rompe",
    },
    {
        "personaje": "Maximus Décimo Meridio",
        "obra": "Gladiador",
        "tipo": "película",
        "principio": "Un hombre al que le quitaron todo — familia, rango, libertad — y que encontró que lo único que no podían quitarle era la dirección que él mismo instaló. Murió en el campo, no en el olvido.",
        "tension_doctrinal": "propósito bajo presión extrema, el precio de ser, finitud como claridad",
    },
    {
        "personaje": "Rocky Balboa",
        "obra": "Rocky",
        "tipo": "película",
        "principio": "No ganó el primer combate. La victoria no era el cinturón — era demostrar que podía seguir en pie cuando todo decía que no podía. El resultado no define al hombre. La ejecución sí.",
        "tension_doctrinal": "responsabilidad sin autodestrucción, consistencia sobre intensidad, identidad por acción",
    },
    {
        "personaje": "Tony Soprano",
        "obra": "Los Soprano",
        "tipo": "serie",
        "principio": "Un hombre que lo tenía todo externamente y lo perdió todo internamente. La anestesia que construyó — poder, dinero, respeto — nunca tocó el vacío. Solo lo tapó.",
        "tension_doctrinal": "el hombre anestesiado, vacío sin dirección, el proveedor que siente que falla",
    },
    {
        "personaje": "Chris Gardner",
        "obra": "En busca de la felicidad",
        "tipo": "película",
        "principio": "Un hombre en el punto más bajo — sin techo, con un hijo, sin red — que no usó las circunstancias como excusa. La dirección instalada en condiciones imposibles es la única dirección que prueba ser real.",
        "tension_doctrinal": "instalación de dirección, responsabilidad como elección, constructor consciente",
    },
    {
        "personaje": "Geralt de Rivia",
        "obra": "The Witcher",
        "tipo": "videojuego/serie",
        "principio": "Un hombre que eligió no elegir durante décadas, creyendo que eso lo mantenía libre. Descubrió que no elegir también es una elección — y tiene consecuencias.",
        "tension_doctrinal": "parálisis por análisis, susceptibilidad al ruido externo, el hombre sin norte",
    },
]


class Alchemist:
    def __init__(self):
        self.client = Client(api_key=os.getenv("GEMINI_API_KEY"))
        self.model_id = os.getenv("ACTIVE_MODEL")

        # Carga de Doctrina (Directiva 4)
        try:
            with open("core/doctrina_prohibida.json", "r", encoding="utf-8") as f:
                self.prohibidas = json.load(f)
            with open("core/doctrina_industrial.json", "r", encoding="utf-8") as f:
                self.industriales = json.load(f)
        except:
            self.prohibidas = []
            self.industriales = []

    def leer_doctrina(self):
        ruta = os.path.join("prompts", "alquimia.txt")
        with open(ruta, "r", encoding="utf-8") as f:
            return f.read()

    def _seleccionar_arquetipos(self, tema: str, max_arquetipos: int = 3) -> list:
        """
        Selecciona los arquetipos más relevantes para un tema dado,
        comparando palabras clave del tema contra tension_doctrinal de cada arquetipo.
        Fallback: devuelve los primeros max_arquetipos si no hay match.
        """
        tema_lower = tema.lower()
        scored = []
        for arq in ARQUETIPOS_FICCION:
            tension = arq["tension_doctrinal"].lower()
            principio = arq["principio"].lower()
            score = sum(
                1 for palabra in tema_lower.split() if palabra in tension or palabra in principio
            )
            scored.append((score, arq))
        scored.sort(key=lambda x: x[0], reverse=True)
        seleccionados = [arq for _, arq in scored[:max_arquetipos]]
        return seleccionados

    def _formatear_arquetipos(self, arquetipos: list) -> str:
        """Convierte la lista de arquetipos en bloque de texto para el prompt."""
        if not arquetipos:
            return ""
        lineas = ["🎭 ARQUETIPOS DE FICCIÓN DISPONIBLES:"]
        lineas.append("Úsalos como espejos del dolor real. NUNCA citar textual — siempre")
        lineas.append("parafrasear el principio y nombrar al personaje como ejemplo cultural.\n")
        for arq in arquetipos:
            lineas.append(f"── {arq['personaje']} ({arq['obra']} / {arq['tipo']})")
            lineas.append(f"   Principio: {arq['principio']}")
            lineas.append(f"   Tensión: {arq['tension_doctrinal']}\n")
        return "\n".join(lineas)

    def generar_ideas_backlog(self, insight):
        """Genera 10 ideas de video (títulos) a partir de un solo insight psicológico."""
        if not insight:
            return []

        arquetipos = self._seleccionar_arquetipos(
            str(insight.get("problema_principal") or "")
            + " "
            + str(insight.get("dolor_principal") or ""),
            max_arquetipos=2,
        )
        bloque_arquetipos = self._formatear_arquetipos(arquetipos)

        # Preparar campos seguros para el prompt
        frases_potentes = insight.get("frases_potentes") or []
        if not isinstance(frases_potentes, list):
            frases_potentes = [str(frases_potentes)]

        prompt = f"""
        Actúa como el Alquimista de Disciplina en Acero.
        A partir del siguiente INSIGHT psicológico, genera 10 ideas de títulos para YouTube Shorts.
        
        INSIGHT:
        - Problema: {insight.get("problema_principal") or "Desconocido"}
        - Frases: {", ".join(frases_potentes)}
        - Dolor: {insight.get("dolor_principal") or "Desconocido"}
        
        {bloque_arquetipos}
        
        REGLAS:
        - Títulos cortos, agresivos, directos a la yugular.
        - Evita palabras blandas.
        - Puedes usar el nombre de un personaje de ficción como gancho si refuerza el título.
          Ejemplo: "Lo que Arthur Morgan entendió justo antes de morir"
        - Usa el formato: "1. Título\n2. Título..."
        
        Responde SOLO con la lista de 10 títulos.
        """
        if self.model_id is None:
            raise ValueError("ACTIVE_MODEL no está configurado en las variables de entorno")

        response = self.client.models.generate_content(model=self.model_id, contents=prompt)

        if response.text is None:
            raise ValueError("La respuesta del modelo no contiene texto")

        lineas = [l.strip() for l in response.text.split("\n") if l.strip() and l[0].isdigit()]
        return lineas[:10]

    def transmutar_dolor(self, tema_investigacion, context="", banned_metaphors=""):
        print(f"⚗️ [Alquimista] Transmutando: {tema_investigacion}...")

        doctrina = self.leer_doctrina()
        prompt_memoria = (
            f"\n⚠️ PROHIBIDO USAR ESTAS METÁFORAS: {banned_metaphors}" if banned_metaphors else ""
        )

        # Inyección de Glosario (Directiva 4)
        glosario_imp = f"""
        🔥 LEY DE LENGUAJE MIURA:
        PROHIBIDO (Lenguaje suave): {", ".join(self.prohibidas[:15])}
        OBLIGATORIO (Lenguaje industrial): {", ".join(self.industriales[:15])}
        
        Transforma cualquier concepto emocional en una analogía de mecánica, forja o combustión.
        """

        # Selección automática de arquetipos relevantes al tema
        arquetipos = self._seleccionar_arquetipos(tema_investigacion, max_arquetipos=3)
        bloque_arquetipos = self._formatear_arquetipos(arquetipos)

        prompt = f"""
        {doctrina}
        
        {glosario_imp}
 
        {prompt_memoria}
 
        CONTEXTO DE INVESTIGACIÓN (Testimonios reales):
        {context}
 
        {bloque_arquetipos}
 
        TEMA A TRANSMUTAR: {tema_investigacion}
 
        REQUERIMIENTO ADICIONAL:
        Además de las fases, genera 30 títulos virales basados en este dolor, siguiendo estas 6 plantillas (5 variaciones por cada una):
        1. VERDAD INCÓMODA (Directo a la herida)
        2. REVELACIÓN (El descubrimiento que cambia todo)
        3. CONFESIÓN (Vulnerabilidad táctica)
        4. ERROR CRÍTICO (El fallo que destruye vidas)
        5. DESPERTAR (El momento de quiebre) — al menos 2 de estos 5 deben usar un arquetipo de ficción como gancho
        6. TRAMPA (La mentira que todos aceptan)
 
        REGLA DE FICCIÓN EN TÍTULOS:
        Cuando uses un personaje, nombra solo el personaje y la lección — nunca reproduzcas
        frases textuales del guion o la obra. Parafrasea el principio.
        Ejemplo correcto: "Lo que Joel entendió cuando ya era tarde"
        Ejemplo incorrecto: "Joel dijo: 'Tienes que encontrar algo por lo que luchar'"
 
        Añade los títulos al JSON final en un campo llamado "titulos_virales" organizado por plantilla.
        Incluye también el campo "arquetipo_usado": {"personaje": "", "obra": "", "principio_parafraseado": ""} con los datos del arquetipo que mejor encaje si utilizaste alguno.
        """

        if self.model_id is None:
            raise ValueError("ACTIVE_MODEL no está configurado en las variables de entorno")

        response = self.client.models.generate_content(model=self.model_id, contents=prompt)

        if response.text is None:
            raise ValueError("La respuesta del modelo no contiene texto")

        texto = response.text.replace("```json", "").replace("```", "").strip()
        try:
            data = json.loads(texto)
            return json.dumps(data, ensure_ascii=False, indent=2)
        except json.JSONDecodeError:
            print("⚠️ [Alquimista] JSON detectado con ruido. Intentando rescate...")
            rescue = re.search(r"\{.*\}", texto, re.DOTALL)
            if rescue:
                try:
                    data = json.loads(rescue.group())
                    return json.dumps(data, ensure_ascii=False, indent=2)
                except:
                    pass
            print("❌ [Alquimista] Fallo crítico al generar JSON estructurado.")
            return texto
