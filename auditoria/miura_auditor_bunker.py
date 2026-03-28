import os
import sys
import json
import re
import datetime
import argparse
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

# Sincronizar con el corazón del sistema
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from llm.factory import LLMFactory
from core.database import Database

console = Console()


class MiuraAuditorBunker:
    def __init__(self):
        self.ruta_base = os.path.dirname(__file__)
        self.lista_negra_path = os.path.join(self.ruta_base, "lista_negra.txt")
        self.prompt_path = os.path.join(os.path.dirname(self.ruta_base), "prompts", "auditoria.txt")
        self.registro_path = os.path.join(self.ruta_base, "registro_sentencias.json")
        self.purificar_prompt_path = os.path.join(
            os.path.dirname(self.ruta_base), "prompts", "purificador.txt"
        )

        self.db = Database()

        # Calibración del Motor vía Factory
        self.brain = LLMFactory.get_brain("auditor")
        self.temperature = 0.3
        self.reasoning_effort = "low"
        self.frequency_penalty = 0.2

    def cargar_recursos(self):
        # Cargar Lista Negra
        with open(self.lista_negra_path, "r", encoding="utf-8") as f:
            contenido = f.read()
            self.palabras_prohibidas = []
            for line in contenido.split("\n"):
                if ":" in line:
                    palabras = line.split(":")[1].split(",")
                    self.palabras_prohibidas.extend(
                        [p.strip().lower() for p in palabras if p.strip()]
                    )

        # Cargar Prompt de Auditoría
        with open(self.prompt_path, "r", encoding="utf-8") as f:
            self.instrucciones_auditoria = f.read()

        # Cargar Prompt de Purificación
        if os.path.exists(self.purificar_prompt_path):
            with open(self.purificar_prompt_path, "r", encoding="utf-8") as f:
                self.instrucciones_purga = f.read()
        else:
            self.instrucciones_purga = "Purifica el guion eliminando lenguaje suave."

    def parsear_sentencia(self, texto):
        """Extrae métricas y secciones de la respuesta del LLM (Versión Miura 2026)."""
        resultados = {
            "intensidad": "",
            "ritmo": "",
            "coherencia": "",
            "adn_acero": "",
            "fallas": "",
            "ajustes": "",
            "guion_optimizado": "",
        }

        # Regex flexible para capturar (1-10): X o simplemente X (Soporta EN/ES)
        def find_metric(patterns, text):
            for pattern in patterns:
                match = re.search(pattern, text, re.I | re.M)
                if match:
                    return match.group(1)
            return "0"

        resultados["intensidad"] = find_metric(
            [r"Intensidad.*?[\s:]+(\d+)", r"Intensity.*?[\s:]+(\d+)"], texto
        )
        resultados["ritmo"] = find_metric([r"Ritmo.*?[\s:]+(\d+)", r"Rhythm.*?[\s:]+(\d+)"], texto)
        resultados["coherencia"] = find_metric(
            [
                r"Coherencia doctrinal.*?[\s:]+(\d+)",
                r"Coherencia.*?[\s:]+(\d+)",
                r"Coherence.*?[\s:]+(\d+)",
            ],
            texto,
        )

        resultados["adn_acero"] = find_metric(
            [
                r"\*?\*?ADN Disciplina en Acero\*?\*?.*?[\s:]+(\d+)",
                r"ADN.*?[\s:]+(\d+)",
                r"DNA.*?[\s:]+(\d+)",
            ],
            texto,
        )

        def extract_section(header, text):
            # Busca el encabezado y captura hasta el siguiente marcador o final
            pattern = rf"{header}.*?\n(.*?)(?=\n#|\n\*\*|\n---|\n[a-zA-Z]+ \d|\Z)"
            match = re.search(pattern, text, re.S | re.I)
            return match.group(1).strip() if match else ""

        resultados["fallas"] = extract_section("Fallas detectadas", texto)
        resultados["ajustes"] = extract_section("Ajustes concretos", texto)

        # Limpiar la versión optimizada de posibles prefijos de bloque de código y etiquetas AI
        opt = extract_section("Versión optimizada", texto)
        if opt:
            opt_limpio = re.sub(r"^>\s*", "", opt, flags=re.M)  # Quitar citación markdown

            # --- LIMPIEZA INDUSTRIAL (Remover etiquetas que estorban en Voice/Visual) ---
            # 1. Quitar etiquetas negritas tipo "**Golpe inicial:**" o "**Cierre:**"
            opt_limpio = re.sub(r"\*\*.*?\*\*[:\- ]*", "", opt_limpio)

            # 2. Quitar emojis de números (1️⃣, 2️⃣, etc.) y numeración simple al inicio
            opt_limpio = re.sub(r"[0-9]️⃣\s*", "", opt_limpio)
            opt_limpio = re.sub(r"^\d+[\)\.]\s*", "", opt_limpio, flags=re.M)

            # 3. Quitar metadatos finales tipo "*(Total ≈ 112 palabras...)*"
            opt_limpio = re.sub(r"\n\*?\(.*?\)\*?\s*$", "", opt_limpio, flags=re.S)

            # 4. Quitar líneas que sean solo separadores o etiquetas solas
            lineas = [l.strip() for l in opt_limpio.split("\n") if l.strip()]
            resultados["guion_optimizado"] = "\n".join(lineas).strip()

        return resultados

    def escanear_chatarra(self, texto):
        texto_limpio = texto.lower()
        hallazgos = []
        for palabra in self.palabras_prohibidas:
            if re.search(rf"\b{re.escape(palabra)}\b", texto_limpio):
                hallazgos.append(palabra)
        return hallazgos

    def _auditoria_estructural(self, texto):
        palabras = texto.strip().split()
        total_p = len(palabras)
        frases = re.split(r"[.!?]+", texto)
        frases = [f.strip() for f in frases if f.strip()]

        frases_criticas = []
        for f in frases:
            len_f = len(f.split())
            if len_f > 14:  # Límite estricto Miura
                frases_criticas.append({"texto": f, "longitud": len_f})

        count_tu = len(re.findall(rf"\btú\b", texto, re.IGNORECASE))
        count_pasivos = len(
            re.findall(rf"\bpodrías\b|\btratar\b|\bintentar\b|\bsentir\b", texto, re.IGNORECASE)
        )

        return {
            "total_palabras": total_p,
            "frases_criticas": frases_criticas,
            "metrica_eje": {"tu": count_tu, "pasivos": count_pasivos},
        }

    def silenciador_ia(self, respuesta):
        if not respuesta or not isinstance(respuesta, str):
            return "[Error] El Auditor no devolvió una sentencia válida."

        puntos_interes = [
            "Puntuación",
            "Intensidad",
            "Ritmo",
            "Coherencia",
            "ADN",
            "Fallas",
            "Ajustes",
            "Versión",
            "Score",
            "Intensity",
            "Rhythm",
            "Coherence",
            "DNA",
            "Flaws",
            "Adjustments",
            "Version",
        ]
        lineas = respuesta.split("\n")
        lineas_limpias = []
        capturando = False

        for line in lineas:
            if any(p in line for p in puntos_interes):
                capturando = True
            if capturando:
                lineas_limpias.append(line)

        return "\n".join(lineas_limpias).strip()

    def purificar_guion(self, texto, hallazgos):
        """Reescribe el guion eliminando lenguaje terapéutico."""
        console.print(
            Panel(
                f"⚠️ [bold red]MATERIA PRIMA CONTAMINADA[/]\n\nPalabras detectadas: [bold yellow]{', '.join(hallazgos)}[/]\n\n🔥 Activando [bold red]PROTOCOLO PURGA DOCTRINAL[/]...",
                border_style="red",
            )
        )

        system_prompt = self.instrucciones_purga.replace("{hallazgos}", ", ".join(hallazgos))

        with console.status("[bold red]Purificando guion...[/]"):
            guion_limpio = self.brain.generate(
                f"{system_prompt}\n\nTEXTO A PURIFICAR:\n{texto}",
                temperature=0.1,  # Muy baja para evitar alucinaciones creativas
                reasoning_effort="low",
            )

        console.print("✅ [bold green]Versión purificada generada.[/]\n")
        return guion_limpio.strip() if guion_limpio else ""

    def ejecutar_auditoria(self, id_master=None, ruta_manual=None):
        console.print(
            Panel(
                "⚔️ [bold red]MIURA AUDITOR BUNKER[/] - Control de Calidad Doctrinal",
                border_style="bright_black",
            )
        )

        guion_texto = ""
        origen = ""
        purga_activada = False
        palabras_detectadas = []

        if id_master:
            console.print(
                f"📡 [Sheets] Cargando GUION_ORIGINAL del MASTER: [bold cyan]{id_master}[/]"
            )
            try:
                auditoria_sheet = self.db.auditoria
                if auditoria_sheet:
                    all_audits = auditoria_sheet.get_all_values()
                    id_buscado = str(id_master).strip()
                    for row in all_audits:
                        if row and len(row) > 1 and str(row[0]).strip() == id_buscado:
                            guion_texto = row[1]
                            origen = f"Sheets: {id_master}"
                            break
                else:
                    console.print("[yellow]⚠️ Tabla AUDITORIA no disponible.[/]")
            except Exception as e:
                console.print(f"[yellow]⚠️ Error consultando tabla: {e}[/]")

            if not guion_texto:
                console.print(
                    "[red]❌ Error: No se encontró el registro inicial en la tabla AUDITORIA.[/]"
                )
                return
        else:
            if not ruta_manual:
                ruta_manual = console.input(
                    "\n[bold yellow]📁 Ingrese la ruta del archivo .txt a auditar: [/]"
                )

            if not os.path.exists(ruta_manual):
                console.print("[red]❌ Error: El archivo no existe.[/]")
                return
            with open(ruta_manual, "r", encoding="utf-8") as f:
                guion_texto = f.read()

            # Para no perder data de TXT, generamos un ID y registramos en Sheets
            timestamp_manual = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            nombre_archivo = os.path.basename(ruta_manual).split(".")[0]
            id_master = f"MANUAL_{nombre_archivo}_{timestamp_manual}"
            origen = ruta_manual

            console.print(
                f"📦 [Sistema] Creando registro de auditoría local en Sheets: [bold yellow]{id_master}[/]"
            )
            self.db.registrar_auditoria_inicial(id_master, guion_texto)

        # Paso 2 — Filtro de Chatarra y Purificación
        self.cargar_recursos()
        hallazgos = self.escanear_chatarra(guion_texto)
        if hallazgos:
            purga_activada = True
            palabras_detectadas = hallazgos
            guion_texto = self.purificar_guion(guion_texto, hallazgos)

        # Paso 3 — Auditoría del LLM
        adn_doctrinal = ""
        ruta_adn = os.path.join(os.path.dirname(self.ruta_base), "doctrina", "libro1_adn.txt")
        if os.path.exists(ruta_adn):
            with open(ruta_adn, "r", encoding="utf-8") as f:
                adn_doctrinal = f.read()

        console.print("🔍 [bold cyan]Iniciando auditoría Miura...[/]")
        with console.status("[bold cyan]Llamando al Yunque del Auditor...[/]"):
            prompt_final = f"""
            {self.instrucciones_auditoria}
            
            --- ADN DOCTRINAL (LIBRO 1) ---
            {adn_doctrinal}
            
            GUION A AUDITAR:
            {guion_texto}
            """
            respuesta_cruda = self.brain.generate(
                prompt_final,
                temperature=self.temperature,
                frequency_penalty=self.frequency_penalty,
                reasoning_effort=self.reasoning_effort,
            )
            auditoria_llm = self.silenciador_ia(respuesta_cruda)

        # Paso 4 — Validaciones Automáticas
        stats = self._auditoria_estructural(guion_texto)
        resultados_parsed = self.parsear_sentencia(auditoria_llm)

        # Paso 5 — Presentación
        console.print("\n")
        if purga_activada:
            console.print(Panel(guion_texto, title="🛠️ GUION PURIFICADO", border_style="yellow"))

        table_stats = Table(show_header=False, box=None)
        table_stats.add_row("Total Palabras:", f"{stats['total_palabras']} / 140")
        table_stats.add_row("Impacto 'Tú':", f"{stats['metrica_eje']['tu']}")
        table_stats.add_row("Ruido Pasivo:", f"{stats['metrica_eje']['pasivos']}")
        console.print(
            Panel(table_stats, title="[bold white]Métricas de Estructura[/]", border_style="blue")
        )

        if stats["total_palabras"] > 140 or stats["frases_criticas"]:
            violaciones = []
            if stats["total_palabras"] > 140:
                violaciones.append(f"• Exceso de palabras: {stats['total_palabras']} (Máx 140)")
            for f in stats["frases_criticas"]:
                violaciones.append(
                    f'[bold red]❌ Frase Incandescente ({f["longitud"]} palabras):[/] "{f["texto"]}"'
                )
            console.print(
                Panel("\n".join(violaciones), title="⚠️ VIOLACIÓN DE DOCTRINA", border_style="red")
            )

        console.print(Panel(auditoria_llm, title="⚖️ SENTENCIA DEL AUDITOR", border_style="green"))

        # Sincronización con Sheets (Para ID de Master o Generado Manualmente)
        if purga_activada and not resultados_parsed.get("guion_optimizado"):
            resultados_parsed["guion_optimizado"] = guion_texto

        self.db.actualizar_resultados_auditoria(id_master, resultados_parsed)
        console.print(
            f"[bold green]✅ Resultados sincronizados en Google Sheets para el ID: {id_master}[/]"
        )

        # Registro Local
        history_entry = {
            "fecha": str(datetime.datetime.now()),
            "origen": origen,
            "purga_activada": purga_activada,
            "palabras_detectadas": palabras_detectadas,
            "stats": stats,
            "auditoria": auditoria_llm,
            "parsed": resultados_parsed,
        }
        try:
            with open(self.registro_path, "r", encoding="utf-8") as f:
                history = json.load(f)
        except:
            history = []
        history.append(history_entry)
        with open(self.registro_path, "w", encoding="utf-8") as f:
            json.dump(history, f, indent=4)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Miura Auditor Bunker")
    parser.add_argument("--id", help="ID de Sesión / ID_MASTER de Google Sheets")
    parser.add_argument("--file", help="Ruta local de archivo .txt")
    args = parser.parse_args()

    auditor = MiuraAuditorBunker()
    auditor.ejecutar_auditoria(id_master=args.id, ruta_manual=args.file)
