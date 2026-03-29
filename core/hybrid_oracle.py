"""
🔮 ORÁCULO HÍBRIDO MIURA — Motor de Inteligencia Doctrinal
═══════════════════════════════════════════════════════════
Integra NotebookLM como capa RAG para investigación profunda.
Reemplaza las 40+ llamadas individuales a LLMs por UNA consulta
de contexto masivo al cuaderno semanal.

Arquitectura:
  1. OSINT Ligero   → Researcher detecta tendencias (Serper, barato)
  2. Deep Research  → NotebookLM busca 40 fuentes de alta calidad
  3. Digestión      → Consulta doctrinal al cuaderno (cero tokens LLM)
  4. Registro       → Hallazgos estructurados al Búnker (GSheets)

Requiere: notebooklm-mcp-server autenticado.
"""

import os
import json
import time
import datetime
import random
import subprocess
import sys
from pathlib import Path


# ─────────────────────────────────────────────────────────────────────────
# CONSTANTES DOCTRINALES
# ─────────────────────────────────────────────────────────────────────────

NOMBRES_EPICOS = [
    "BIZANCIO", "ROMA", "ESPARTA", "ATENAS", "BABILONIA", "EGIPTO",
    "FENICIA", "PERSIA", "SUMERIA", "CARTAGO", "ALEJANDRO", "LEONIDAS",
    "CIRO", "DARIO", "JERJES", "RAMSES", "TUTANKAMON", "NABUCODONOSOR",
    "HAMMURABI", "JULIO_CESAR", "AUGUSTO", "TRAJANO", "ADRIANO",
    "MARCO_AURELIO", "SULEIMAN", "MEHMET", "ESTOICO", "ESPARTANO"
]

PROMPT_CONSULTA_DOCTRINAL = """
Analiza TODAS las fuentes de este cuaderno y genera un Reporte de Inteligencia
para la marca "Disciplina en Acero" — contenido de desarrollo personal masculino.

Extrae lo siguiente:

1. **DOLORES DETECTADOS**: Los 3-5 dolores estructurales más recurrentes.
   Para cada uno indica: nombre, frecuencia relativa, ejemplo textual real.

2. **FRASES DE ACERO (Steel Quotes)**: Las 5-10 frases más potentes, crudas
   y memorables que encontraste en los testimonios. Deben servir como hooks
   para contenido viral. Incluye la fuente.

3. **GANCHOS DE MARKETING**: 3 títulos de video/artículo basados en los
   dolores detectados. Formato: gancho emocional + promesa de transformación.

4. **TENDENCIA DOMINANTE**: ¿Cuál es el tema que más se repite esta semana?
   ¿Por qué es relevante ahora?

5. **SOLUCIÓN MIURA**: Para cada dolor, propone una "Steel Solution" — una
   acción concreta, directa, sin rodeos, alineada con la filosofía de
   disciplina, propósito y verdad incómoda.

Responde en formato estructurado con headers ##.
"""

PROMPT_CONSULTA_BLOG = """
Analiza TODAS las fuentes de este cuaderno sobre el libro "{titulo_libro}"
y genera un briefing para escribir una reseña doctrinal para la marca
"Disciplina en Acero".

Extrae:

1. **TESIS CENTRAL**: ¿Cuál es la idea principal del libro en una frase?

2. **DOLORES QUE ATACA**: ¿Qué problemas específicos resuelve este libro?
   Conecta con dolores masculinos reales.

3. **ARMAS DOCTRINALES**: Las 3-5 herramientas, técnicas o verdades más
   potentes del libro que un hombre puede aplicar HOY.

4. **ANCLA DE VERDAD**: La frase más demoledora, cruda y transformadora
   del libro. Cita textual si es posible.

5. **VEREDICTO**: ¿Para quién es este libro y para quién NO?
   Sin rodeos, sin suavizar.

Responde en formato estructurado con headers ##.
"""


class HybridOracle:
    """
    Motor de inteligencia que combina OSINT ligero con NotebookLM
    para investigación profunda y extracción doctrinal.
    """

    def __init__(self, mcp_exe_path=None):
        """
        Inicializa el Oráculo Híbrido.
        
        Args:
            mcp_exe_path: Ruta al ejecutable notebooklm-mcp. 
                          Si es None, se auto-detecta del venv.
        """
        if mcp_exe_path is None:
            venv_path = Path(__file__).parent.parent / "venv" / "Scripts" / "notebooklm-mcp.exe"
            if venv_path.exists():
                self.mcp_exe = str(venv_path)
            else:
                self.mcp_exe = "notebooklm-mcp"
        else:
            self.mcp_exe = mcp_exe_path

        self.notebook_cache = {}  # {tema: notebook_id}

    # ─────────────────────────────────────────────────────────────────
    # NÚCLEO: Investigación Profunda vía NotebookLM
    # ─────────────────────────────────────────────────────────────────

    def investigar_tema(self, tema, modo="fast", notebook_id=None):
        """
        Ejecuta una investigación completa sobre un tema usando NotebookLM.
        
        Args:
            tema: El tema a investigar (ej: "crisis de identidad masculina 2026")
            modo: "fast" (~30s, ~10 fuentes) o "deep" (~5min, ~40 fuentes)
            notebook_id: ID de cuaderno existente. Si None, crea uno nuevo.
            
        Returns:
            dict con: notebook_id, fuentes_importadas, reporte_doctrinal
        """
        print(f"\n🔮 [Oráculo Híbrido] Investigación {modo.upper()} para: {tema}")
        print("=" * 60)

        resultado = {
            "tema": tema,
            "modo": modo,
            "notebook_id": None,
            "fuentes_importadas": 0,
            "reporte": None,
            "timestamp": datetime.datetime.now().isoformat(),
            "exito": False
        }

        try:
            # 1. Crear o reutilizar cuaderno
            if notebook_id:
                resultado["notebook_id"] = notebook_id
                print(f"📓 Reutilizando cuaderno: {notebook_id}")
            else:
                nb_id = self._crear_cuaderno(tema)
                if not nb_id:
                    print("❌ [Oráculo] No se pudo crear el cuaderno.")
                    return resultado
                resultado["notebook_id"] = nb_id

            # 2. Ejecutar Deep Research
            task_id = self._iniciar_investigacion(
                resultado["notebook_id"], tema, modo
            )
            if not task_id:
                print("❌ [Oráculo] No se pudo iniciar la investigación.")
                return resultado

            # 3. Esperar completitud
            investigacion_ok = self._esperar_investigacion(
                resultado["notebook_id"], task_id
            )
            if not investigacion_ok:
                print("⚠️ [Oráculo] La investigación no completó correctamente.")
                return resultado

            # 4. Importar fuentes al cuaderno
            fuentes = self._importar_fuentes(resultado["notebook_id"], task_id)
            resultado["fuentes_importadas"] = fuentes

            # 5. Consulta Doctrinal
            reporte = self._consultar_cuaderno(
                resultado["notebook_id"],
                PROMPT_CONSULTA_DOCTRINAL
            )
            resultado["reporte"] = reporte
            resultado["exito"] = bool(reporte)

            if resultado["exito"]:
                print(f"\n✅ [Oráculo] Investigación completada. "
                      f"{fuentes} fuentes digeridas.")
            
            return resultado

        except Exception as e:
            print(f"❌ [Oráculo] Error crítico: {e}")
            resultado["error"] = str(e)
            return resultado

    def investigar_libro(self, titulo_libro, urls_fuentes=None, notebook_id=None):
        """
        Investiga un libro específico para el Blog Alchemist.
        Puede recibir URLs de fuentes o hacer Deep Research.
        
        Args:
            titulo_libro: Nombre del libro
            urls_fuentes: Lista de URLs (reseñas, análisis, etc.)
            notebook_id: Cuaderno existente
            
        Returns:
            dict con briefing doctrinal para el Alchemist
        """
        print(f"\n📚 [Oráculo Híbrido] Investigando libro: {titulo_libro}")
        print("=" * 60)

        resultado = {
            "libro": titulo_libro,
            "notebook_id": None,
            "briefing": None,
            "exito": False
        }

        try:
            # 1. Crear cuaderno para el libro
            if notebook_id:
                nb_id = notebook_id
            else:
                nb_id = self._crear_cuaderno(f"Reseña: {titulo_libro}")
            
            if not nb_id:
                return resultado
            resultado["notebook_id"] = nb_id

            # 2. Añadir fuentes
            if urls_fuentes:
                # Modo dirigido: inyectar URLs específicas
                for url in urls_fuentes:
                    self._agregar_url(nb_id, url)
                    time.sleep(1)  # Rate limiting gentil
            else:
                # Modo autónomo: Deep Research
                query = (f"{titulo_libro} reseña análisis profundo "
                         f"desarrollo personal disciplina")
                task_id = self._iniciar_investigacion(nb_id, query, "fast")
                if task_id:
                    self._esperar_investigacion(nb_id, task_id)
                    self._importar_fuentes(nb_id, task_id)

            # 3. Consulta doctrinal especializada para libros
            prompt = PROMPT_CONSULTA_BLOG.format(titulo_libro=titulo_libro)
            briefing = self._consultar_cuaderno(nb_id, prompt)
            
            # 4. Extraer el Ancla Social (La Voz del Pueblo)
            ancla_social = self.obtener_ancla_social(nb_id)
            
            resultado["briefing"] = briefing
            resultado["ancla_social"] = ancla_social
            resultado["exito"] = bool(briefing)

            if resultado["exito"]:
                print(f"✅ [Oráculo] Briefing del libro generado exitosamente.")

            return resultado

        except Exception as e:
            print(f"❌ [Oráculo] Error investigando libro: {e}")
            resultado["error"] = str(e)
            return resultado

    def obtener_ancla_social(self, notebook_id):
        """
        Consulta específica a NotebookLM para extraer la opinión más cruda y honesta
        como un Ancla de Verdad.
        """
        print("🗣️ Extrayendo la 'Voz del Pueblo' (Ancla Social)...")
        prompt_ancla = (
            "Busca el testimonio o reseña de usuario real más cruda, honesta y dolorosa sobre este libro en tus fuentes. "
            "No quiero un resumen académico ni de la editorial. Quiero la voz de un hombre que sintió dolor, frustración "
            "o un despertar real al leerlo o intentar aplicarlo. "
            "Responde estrictamente en este formato, sin añadir nada más:\n"
            "\"[Testimonio/Cita exacta]\" — [Fuente, ej: Usuario de Reddit / Crítica de Amazon / Foro]"
            "\nSi no hay testimonios reales de usuarios, extrae la frase más polarizante del propio autor en el libro y cítalo a él."
        )
        ancla = self._consultar_cuaderno(notebook_id, prompt_ancla)
        if ancla:
            # Limpieza básica para evitar verbosidad del modelo
            ancla = ancla.replace("Aquí tienes el testimonio:", "").strip()
            # Si el modelo incluye la cadena "—" nos aseguramos de no cortarla, pero podemos quitar \n
        return ancla

    # ─────────────────────────────────────────────────────────────────
    # ORÁCULO SEMANAL HÍBRIDO (reemplaza weekly_oracle.py)
    # ─────────────────────────────────────────────────────────────────

    def run_oraculo_semanal(self, temas=None):
        """
        Ejecuta el ciclo semanal completo del Oráculo usando NotebookLM.
        
        Si no se pasan temas, usa el Researcher para detectar tendencias
        y luego delega la investigación profunda a NotebookLM.
        
        Args:
            temas: Lista de temas a investigar. Si None, auto-detecta.
            
        Returns:
            dict con resultados agregados
        """
        nombre_mision = random.choice(NOMBRES_EPICOS)
        id_semana = f"{nombre_mision}_{datetime.datetime.now().strftime('%Y%m%d')}"
        
        print(f"\n🔮 [ORÁCULO HÍBRIDO] Misión: {id_semana}")
        print("=" * 60)

        # 1. Detectar tendencias si no se pasaron temas
        if not temas:
            print("📡 Detectando pulso semanal con Serper (modo ligero)...")
            try:
                from core.researcher import Researcher
                researcher = Researcher()
                tendencias = researcher.detectar_pulso_semanal()
                temas = [t["tema"] for t in tendencias] if tendencias else []
            except Exception as e:
                print(f"⚠️ Detección de tendencias falló: {e}")
                temas = []

        if not temas:
            print("❌ [Oráculo] Sin temas para investigar. Abortando.")
            return {"exito": False, "razon": "sin_temas"}

        # 2. Crear cuaderno semanal
        titulo_cuaderno = f"Miura Intel — {id_semana}"
        nb_id = self._crear_cuaderno(titulo_cuaderno)
        if not nb_id:
            return {"exito": False, "razon": "notebook_creation_failed"}

        # 3. Deep Research para TODOS los temas en un solo cuaderno
        query_combinada = " | ".join(temas)
        query_investigacion = (
            f"Men's struggles and pain points 2026: {query_combinada}. "
            f"Focus on real testimonials, confessions, Reddit discussions, "
            f"and personal development challenges."
        )

        print(f"\n🧠 Ejecutando Deep Research en NotebookLM...")
        print(f"   Query: {query_investigacion[:100]}...")

        task_id = self._iniciar_investigacion(nb_id, query_investigacion, "deep")
        if not task_id:
            return {"exito": False, "razon": "research_start_failed"}

        # 4. Esperar y luego importar
        self._esperar_investigacion(nb_id, task_id)
        fuentes = self._importar_fuentes(nb_id, task_id)

        # 5. Consulta Doctrinal Final
        reporte = self._consultar_cuaderno(nb_id, PROMPT_CONSULTA_DOCTRINAL)

        # 6. Registrar en el Búnker
        resultado_final = {
            "exito": bool(reporte),
            "id_semana": id_semana,
            "notebook_id": nb_id,
            "notebook_url": f"https://notebooklm.google.com/notebook/{nb_id}",
            "temas": temas,
            "fuentes_importadas": fuentes,
            "reporte": reporte
        }

        if reporte:
            self._registrar_en_bunker(id_semana, temas, reporte)
            print(f"\n✅ [Oráculo Híbrido] Misión {id_semana} completada.")
            print(f"   📓 Cuaderno: {resultado_final['notebook_url']}")
            print(f"   📊 Fuentes digeridas: {fuentes}")
        else:
            print(f"\n⚠️ [Oráculo] Misión {id_semana} parcial — sin reporte.")

        return resultado_final

    # ─────────────────────────────────────────────────────────────────
    # MÉTODOS PRIVADOS — Interfaz con NotebookLM MCP
    # ─────────────────────────────────────────────────────────────────

    def _crear_cuaderno(self, titulo):
        """Crea un nuevo cuaderno en NotebookLM."""
        print(f"📓 Creando cuaderno: {titulo}")
        try:
            from notebooklm_mcp.client import NotebookLMClient
            client = NotebookLMClient()
            result = client.notebook_create(title=titulo)
            nb_id = result.get("id") or result.get("notebook_id")
            if nb_id:
                print(f"   ✅ Cuaderno creado: {nb_id}")
                self.notebook_cache[titulo] = nb_id
            return nb_id
        except ImportError:
            # Fallback: usar MCP tools directamente (cuando se ejecuta desde Antigravity)
            print("   ℹ️ Cliente directo no disponible. Usar desde Antigravity MCP.")
            return None
        except Exception as e:
            print(f"   ❌ Error creando cuaderno: {e}")
            return None

    def _iniciar_investigacion(self, notebook_id, query, modo="fast"):
        """Inicia una investigación (Deep Research) en NotebookLM."""
        print(f"🔍 Iniciando investigación ({modo}): {query[:80]}...")
        try:
            from notebooklm_mcp.client import NotebookLMClient
            client = NotebookLMClient()
            result = client.research_start(
                query=query,
                notebook_id=notebook_id,
                mode=modo,
                source="web"
            )
            task_id = result.get("task_id")
            if task_id:
                print(f"   ✅ Investigación iniciada: {task_id}")
            return task_id
        except ImportError:
            print("   ℹ️ Cliente directo no disponible. Usar desde Antigravity MCP.")
            return None
        except Exception as e:
            print(f"   ❌ Error iniciando investigación: {e}")
            return None

    def _esperar_investigacion(self, notebook_id, task_id, 
                                max_espera=360, intervalo=30):
        """Polling: espera a que la investigación termine."""
        print(f"⏳ Esperando investigación (máx {max_espera}s)...")
        try:
            from notebooklm_mcp.client import NotebookLMClient
            client = NotebookLMClient()
            
            inicio = time.time()
            while time.time() - inicio < max_espera:
                result = client.research_status(
                    notebook_id=notebook_id,
                    task_id=task_id,
                    max_wait=0  # Single poll
                )
                status = result.get("status", "unknown")
                
                if status == "completed":
                    elapsed = int(time.time() - inicio)
                    print(f"   ✅ Investigación completada en {elapsed}s")
                    return True
                elif status in ("failed", "error"):
                    print(f"   ❌ Investigación falló: {result.get('error', 'N/A')}")
                    return False
                else:
                    elapsed = int(time.time() - inicio)
                    print(f"   ⏳ Estado: {status} ({elapsed}s transcurridos)...")
                    time.sleep(intervalo)
            
            print(f"   ⚠️ Timeout después de {max_espera}s")
            return False
        except ImportError:
            print("   ℹ️ Cliente directo no disponible.")
            return False
        except Exception as e:
            print(f"   ❌ Error en polling: {e}")
            return False

    def _importar_fuentes(self, notebook_id, task_id):
        """Importa las fuentes descubiertas al cuaderno."""
        print("📥 Importando fuentes al cuaderno...")
        try:
            from notebooklm_mcp.client import NotebookLMClient
            client = NotebookLMClient()
            result = client.research_import(
                notebook_id=notebook_id,
                task_id=task_id
            )
            count = result.get("imported_count", 0)
            print(f"   ✅ {count} fuentes importadas")
            return count
        except ImportError:
            print("   ℹ️ Cliente directo no disponible.")
            return 0
        except Exception as e:
            print(f"   ❌ Error importando fuentes: {e}")
            return 0

    def _agregar_url(self, notebook_id, url):
        """Agrega una URL como fuente al cuaderno."""
        print(f"   🔗 Agregando: {url[:60]}...")
        try:
            from notebooklm_mcp.client import NotebookLMClient
            client = NotebookLMClient()
            client.notebook_add_url(notebook_id=notebook_id, url=url)
            return True
        except Exception as e:
            print(f"   ⚠️ Error agregando URL: {e}")
            return False

    def _consultar_cuaderno(self, notebook_id, query):
        """Ejecuta una consulta al cuaderno de NotebookLM."""
        print("🧠 Ejecutando consulta doctrinal al cuaderno...")
        try:
            from notebooklm_mcp.client import NotebookLMClient
            client = NotebookLMClient()
            result = client.notebook_query(
                notebook_id=notebook_id,
                query=query,
                timeout=120
            )
            respuesta = result.get("answer") or result.get("response", "")
            if respuesta:
                print(f"   ✅ Reporte recibido ({len(respuesta)} chars)")
            return respuesta
        except ImportError:
            print("   ℹ️ Cliente directo no disponible.")
            return None
        except Exception as e:
            print(f"   ❌ Error en consulta: {e}")
            return None

    def _registrar_en_bunker(self, id_semana, temas, reporte):
        """Guarda los resultados del Oráculo en Google Sheets."""
        print("💾 Registrando hallazgos en el Búnker...")
        try:
            from core.database import Database
            db = Database()
            
            if db.investigacion:
                fecha = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
                for tema in temas:
                    fila = [
                        id_semana,                              # ID_SESION
                        tema,                                   # TEMA
                        "Oráculo Híbrido (NotebookLM)",         # DOLOR_PRINCIPAL
                        reporte[:500] if reporte else "N/A",    # PROBLEMA_RAIZ
                        "",                                     # FRASES_POTENTES
                        "",                                     # CREENCIAS
                        "",                                     # SOLUCION_MIURA
                        "NotebookLM",                           # PLATAFORMA
                        fecha,                                  # FECHA
                        "Hybrid Oracle"                         # ARQUETIPO
                    ]
                    db.investigacion.append_row(fila)
                print(f"   ✅ {len(temas)} registros guardados en el Búnker.")
        except Exception as e:
            print(f"   ⚠️ Error registrando en Búnker: {e}")


# ─────────────────────────────────────────────────────────────────────────
# EJECUCIÓN DIRECTA (para testing desde terminal)
# ─────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    oracle = HybridOracle()
    
    if len(sys.argv) > 1:
        tema = " ".join(sys.argv[1:])
        result = oracle.investigar_tema(tema, modo="fast")
    else:
        result = oracle.run_oraculo_semanal()
    
    print("\n" + "=" * 60)
    print("📋 RESULTADO FINAL:")
    print(json.dumps({
        k: v for k, v in result.items() 
        if k != "reporte"
    }, indent=2, ensure_ascii=False))
    
    if result.get("reporte"):
        print("\n📜 REPORTE DOCTRINAL:")
        print("-" * 60)
        print(result["reporte"][:2000])
