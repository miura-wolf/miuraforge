import os
import re
import json
import requests
from tavily import TavilyClient
from googleapiclient.discovery import build
from dotenv import load_dotenv
from tenacity import retry, stop_after_attempt, wait_exponential
from llm.factory import LLMFactory
from core.database import Database

load_dotenv()

SUBREDDITS_MIURA = [
    "NoFap",
    "decidingtobebetter", 
    "getdisciplined",
    "selfimprovement",
    "marriedredpill",
    "loseit"
]

BASE_ARCTIC = "https://arctic-shift.photon-reddit.com/api"

class Researcher:
    def __init__(self):
        self.tavily_key = os.getenv("TAVILY_API_KEY")
        self.youtube_key = os.getenv("YOUTUBE_API_KEY")
        
        self.tavily = TavilyClient(api_key=self.tavily_key)
        if self.youtube_key:
            self.youtube = build("youtube", "v3", developerKey=self.youtube_key)
        else:
            self.youtube = None
            
        # -- ESCUDO ANTI-BASURA (Blacklist de perfiles/patrones inútiles) --
        self.blacklist_patterns = [
            r"lang=",          # Bloquear parámetros de idioma foráneo
            r"jd41700",        # Perfil reportado como basura
            r"\?s=",           # Tracker de social media que suele traer basura
            r"status/1\d{17}"  # A veces IDs muy específicos de bots
        ]

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def buscar_dolor(self, tema):
        """
        RADAR OSINT: Filtrado Psicológico y Extracción de Dolor Humano.
        """
        print(f"📡 [Explorador] Iniciando Radar OSINT: {tema}...")
        
        # 1. Búsqueda Multiplataforma (Tavily + YouTube)
        hallazgos_crudos = self.buscar_fuentes_web(tema) + self.buscar_youtube_dolor(tema)
        hallazgos_crudos = hallazgos_crudos[:40] # Aumentamos volumen para que GLM5 tenga qué filtrar
        
        print(f"🔍 [Explorador] {len(hallazgos_crudos)} fuentes capturadas. Validando testimonios...")
        
        import time
        hallazgos_validos = []
        fallos_llm = 0

        for h in hallazgos_crudos:
            try:
                analisis = self.analizar_psicologia(h['content'])
            except Exception as e:
                if "429" in str(e) or "quota" in str(e).lower():
                    print("⚠️ [Explorador] Cuota detectada. Pausa táctica...")
                    time.sleep(4.0)
                    analisis = self.analizar_psicologia(h['content'])
                else:
                    print(f"⚠️ [Explorador] Error inesperado en análisis: {e}")
                    fallos_llm += 1
                    continue
            
            if not analisis.get('valido', False):
                fallos_llm += 1
                continue
                
            h.update({
                "problema_principal":  analisis.get('problema_principal', ''),
                "emociones":           analisis.get('emociones', []),
                "creencias":           analisis.get('creencias', []),
                "sintomas":            analisis.get('sintomas', []),
                "frases_potentes":     list(set(
                    self.extraer_frases_potentes(h['content']) +
                    analisis.get('frases_potentes', [])
                )),
                "nivel_dolor":         analisis.get('nivel_dolor', 1),
                "solucion_miura":      analisis.get('solucion_miura', ''),
                "engagement_estimado": analisis.get('engagement_estimado', 0),
                "arquetipo_sugerido":  analisis.get('arquetipo_sugerido', '')
            })
            
            if h.get('engagement', 0) == 0:
                estimado = analisis.get('engagement_estimado', 0)
                h['engagement'] = max(int(estimado), 1) if estimado else 0
            
            principal, secundarios = self.clasificar_dolor(analisis)
            h["dolor_principal"]     = principal
            h["dolores_secundarios"] = secundarios
            
            hallazgos_validos.append(h)

        print(f"✅ [Explorador] Validación completada. {len(hallazgos_validos)} testimonios reales identificados.")
        print(f"📊 [Researcher] Fallos LLM / descartados: {fallos_llm} de {len(hallazgos_crudos)} fuentes.")
        return hallazgos_validos, len(hallazgos_crudos)

    # ─────────────────────────────────────────────────────────────────────────
    # UTILIDADES DE FUENTE
    # ─────────────────────────────────────────────────────────────────────────

    def _extraer_autor_desde_url(self, url, platform, titulo_resultado=""):
        """
        Extrae un autor legible desde la URL segun la plataforma.
        Elimina la heuristica sucia de 'User_dominio'.

        Casos cubiertos:
        - Reddit:   /r/SUBREDDIT/...           -> r/SUBREDDIT
        - Substack: subdomain.substack.com     -> subdomain
        - Medium:   medium.com/@user/...       -> @user
                    medium.com/publicacion/... -> publicacion  [FIX]
        - X:        x.com/usuario/status/...   -> @usuario     [FIX: filtra 'https:']
        - Quora:    quora.com/profile/Nombre   -> Nombre
        - YouTube:  usa el titulo del resultado
        - Fallback: dominio sin 'www.'
        """
        try:
            partes         = url.split('/')
            dominio        = partes[2] if len(partes) > 2 else ""
            dominio_limpio = dominio.replace('www.', '')

            # Reddit
            if platform == "reddit" or "reddit.com" in dominio:
                if '/r/' in url:
                    return "r/" + url.split('/r/')[1].split('/')[0].split('?')[0]
                return "Reddit (anonimo)"

            # Substack / Medium / Blog
            elif platform == "blog" or "substack.com" in dominio or "medium.com" in dominio:
                if dominio.endswith('.substack.com'):
                    return dominio.replace('.substack.com', '')
                if 'medium.com' in dominio:
                    if '/@' in url:
                        return '@' + url.split('/@')[1].split('/')[0].split('?')[0]
                    # FIX: medium.com/publicacion/slug sin @
                    segs = [s for s in url.replace('https://', '').replace('http://', '')
                            .split('/') if s and 'medium.com' not in s]
                    if segs:
                        return segs[0]
                return dominio_limpio

            # X / Twitter
            elif platform == "x" or "x.com" in dominio or "twitter.com" in dominio:
                # FIX: filtrar 'https:', 'http:' con el chequeo de ':' y limpiar parámetros '?'
                segs = [s.split('?')[0] for s in url.split('/')
                        if s
                        and 'x.com'       not in s
                        and 'twitter.com' not in s
                        and ':'           not in s]
                if segs:
                    return '@' + segs[0]
                return "@anonimo_X"

            # Quora
            elif platform == "quora" or "quora.com" in dominio:
                if '/profile/' in url:
                    return url.split('/profile/')[1].split('/')[0].replace('-', ' ')
                return "Quora (anonimo)"

            # YouTube
            elif platform == "youtube":
                return titulo_resultado if titulo_resultado else "YouTube (anonimo)"

            # Fallback
            else:
                return "Fuente desconocida"

        except Exception:
            return "Fuente desconocida"

    def _es_contenido_hispanohablante(self, url, contenido):
        """
        Filtra fuentes que claramente no son del nicho hispanohablante.
        """
        SUBREDDITS_EXCLUIDOS = [
            '/r/Suomi', '/r/de/', '/r/france', '/r/italy', '/r/polska',
            '/r/sweden', '/r/portugal', '/r/brasil', '/r/brazil',
            '/r/AskUK', '/r/britishproblems', '/r/japan', '/r/China'
        ]
        for sub in SUBREDDITS_EXCLUIDOS:
            if sub.lower() in url.lower():
                print(f"🚫 [Researcher] Descartado por region no hispana: {url}")
                return False

        INDICADORES_NO_HISPANO = [
            'ar', 'och', 'inte', 'det', 'som',
            'ist', 'nicht', 'aber', 'dass',
            'est', 'pas', 'pour', 'dans',
            'ei', 'on', 'ja',
        ]
        palabras = contenido.lower().split()
        if len(palabras) < 20:
            return True
        hits  = sum(1 for p in palabras if p in INDICADORES_NO_HISPANO)
        ratio = hits / len(palabras)
        if ratio > 0.12:
            print(f"🚫 [Researcher] Descartado por idioma no hispano (ratio={ratio:.2f}): {url}")
            return False
        return True

    def _es_contenido_del_nicho(self, contenido):
        """
        FILTRO ANTIMUGRE: Verifica si el contenido pertenece al nicho de Miura.
        Evita ruido como 'aprender idiomas', 'salud publica general', 'fitness generico'.
        """
        text = contenido.lower()
        
        # 1. Palabras Clave de Poder (Debe tener al menos una)
        KEYWORDS_NICHO = [
            "disciplina", "proposito", "propósito", "soledad", "hombres", 
            "masculinidad", "adiccion", "adicción", "vacio", "vacío", 
            "autoengaño", "mentirse", "debilitado", "fuerte", "mentalidad",
            "fracaso", "valor", "identidad", "rumbo", "meta",
            "discipline", "purpose", "loneliness", "men", "masculinity",
            "addiction", "void", "self-deception", "failure", "identity",
            "struggle", "lost", "broken", "weak", "strength"
        ]
        
        # 2. Palabras Prohibidas (Basura detectada en auditorías pasadas)
        PROHIBIDAS = [
            "aprender frances", "learning french", "idiomas", "duolingo",
            "salud publica", "eeuu mental health", "public health",
            "belleza", "influencer", "chisme", "farándula", "gaming", "leagues"
        ]
        
        # -- Lógica de Descarte por Patrones (Escudo Anti-Basura) --
        for pattern in self.blacklist_patterns:
            if re.search(pattern, text.lower()):
                return False

        if any(p in text for p in PROHIBIDAS):
            return False
            
        # -- Lógica de Aceptación --
        return any(k in text for k in KEYWORDS_NICHO)

    # ─────────────────────────────────────────────────────────────────────────
    # BUSQUEDA
    # ─────────────────────────────────────────────────────────────────────────

    def generar_queries_inteligentes(self, tema):
        """Usa el LLM para generar queries OSINT altamente efectivas."""
        brain = LLMFactory.get_brain("research_trends")
        prompt = f"""
        Actua como un Especialista en Inteligencia OSINT y Psicologia Masculina.
        Tu mision es generar queries de busqueda para encontrar testimonios REALES de hombres sufriendo o enfrentando este tema: '{tema}'.
        
        Genera 4 queries optimizadas para encontrar DOLOR REAL, enfocandote en:
        1. Reddit (comunidades de desahogo: site:reddit.com)
        2. X/Twitter (hilos de confesion: site:x.com o site:twitter.com)
        3. Quora (preguntas existenciales: site:quora.com)
        4. Blogs/Substack (site:medium.com o site:substack.com)
        
        Usa palabras clave de alta carga emocional: "no puedo mas", "me siento solo", "I feel lost", "confesion", "desahogo".
        
        Responde estrictamente en formato JSON:
        {{
          "queries": [
            {{ "query": "site:reddit.com ...", "platform": "reddit" }},
            {{ "query": "site:x.com ...", "platform": "x" }},
            {{ "query": "site:quora.com ...", "platform": "quora" }},
            {{ "query": "site:substack.com OR site:medium.com ...", "platform": "blog" }}
          ]
        }}
        """
        try:
            res = brain.generate(prompt)
            res_limpio = res.strip()
            if res_limpio.startswith("```"):
                res_limpio = re.sub(r"```(?:json)?", "", res_limpio).strip("`").strip()
            match = re.search(r'\{.*\}', res_limpio, re.DOTALL)
            if match:
                return json.loads(match.group(0)).get('queries', [])
            else:
                print(f"⚠️ [Researcher] JSON no encontrado en generar_queries: {res_limpio[:200]}")
        except json.JSONDecodeError as e:
            print(f"⚠️ [Researcher] JSON invalido en generar_queries: {e}")
        except Exception as e:
            print(f"⚠️ [Researcher] Error en generar_queries: {e}")
        return []

    def buscar_reddit_tavily(self, tema, limite=10):
        """
        Alternativa robusta a Arctic Shift usando Tavily site:reddit.com.
        Garantiza acceso a contenido renderizado y evita bloqueos de API.
        """
        print(f"📡 [Reddit/Tavily] Infiltrándome en Reddit para: {tema}...")
        
        # Traducir el tema al inglés para maximizar resultados en subreddits clave
        brain = LLMFactory.get_brain("research_trends")
        try:
            tema_en = brain.generate(f"Translate this topic to English for a Reddit search query (short and direct): {tema}").strip().strip('"')
        except:
            tema_en = tema

        query = f"site:reddit.com ({tema} OR {tema_en}) (desahogo OR confession OR 'I feel' OR 'story')"
        
        hallazgos = []
        try:
            results = self.tavily.search(query=query, search_depth="advanced", max_results=limite)
            for r in results.get('results', []):
                url = r.get('url', '')
                contenido = r.get('content', '')
                if not self._es_contenido_del_nicho(contenido):
                    continue
                    
                hallazgos.append({
                    "content": contenido,
                    "url": url,
                    "platform": "reddit",
                    "source": "Reddit (Tavily)",
                    "author": self._extraer_autor_desde_url(url, "reddit"),
                    "engagement": 0,
                    "query": query
                })
        except Exception as e:
            print(f"⚠️ [Reddit/Tavily] Error: {e}")
            
        return hallazgos

    def buscar_fuentes_web(self, tema):
        """Búsqueda OSINT expandida. Reddit vía Tavily para mayor fiabilidad."""
        
        # 1. Reddit vía Tavily (reemplaza Arctic Shift por bloqueos de API)
        hallazgos_reddit = self.buscar_reddit_tavily(tema)
        
        # 2. Queries inteligentes para fuentes NO-Reddit (Quora, Medium, blogs)
        queries_dinamicas = self.generar_queries_inteligentes(tema)
        
        if not queries_dinamicas:
            queries_dinamicas = [
                {"query": f"site:quora.com '{tema}' 'why am I lonely' desahogo", "platform": "quora"},
                {"query": f"site:medium.com OR site:substack.com '{tema}' hombres dolor vida", "platform": "blog"}
            ]
        else:
            # Filtrar queries de Reddit — ya las cubrió Arctic Shift
            queries_dinamicas = [q for q in queries_dinamicas if q.get("platform") != "reddit"]
        
        # 3. Tavily solo para fuentes externas (Quora, Medium, blogs)
        hallazgos_externos = []
        print(f"🧠 [Explorador] Ejecutando {len(queries_dinamicas)} queries Tavily (no-Reddit)...")
        
        for item in queries_dinamicas:
            q = item.get('query')
            platform = item.get('platform')
            try:
                results = self.tavily.search(query=q, search_depth="advanced", max_results=5)
                for r in results.get('results', []):
                    raw_url = r.get('url', '')
                    contenido = r.get('content', '')
                    titulo = r.get('title', '')
                    domain = raw_url.split('/')[2] if '/' in raw_url else "Web"
                    
                    # Conservamos el filtro de idioma y region
                    if not self._es_contenido_hispanohablante(raw_url, contenido):
                        continue
                    
                    # Filtro Antimugre Niche Guard
                    if not self._es_contenido_del_nicho(contenido):
                        continue

                    # Conservamos la extraccion inteligente de autor
                    autor = self._extraer_autor_desde_url(raw_url, platform, titulo)

                    hallazgos_externos.append({
                        "content": contenido,
                        "url": raw_url,
                        "platform": platform,
                        "source": domain,
                        "author": autor,
                        "engagement": 0,
                        "query": q
                    })
            except Exception as e:
                print(f"⚠️ [Researcher] Error en busqueda web query '{q}': {e}")
                continue
        
        return hallazgos_reddit + hallazgos_externos

    # ─────────────────────────────────────────────────────────────────────────
    # ANALISIS PSICOLOGICO
    # ─────────────────────────────────────────────────────────────────────────

    def analizar_psicologia(self, texto):
        """Valida si el texto contiene una experiencia real y califica el dolor."""
        brain = LLMFactory.get_brain("research_batch")
        prompt = f"""
        Analiza el siguiente texto publicado en internet.
        Determina si contiene una experiencia personal REAL relacionada con dolor humano masculino.

        DESCARTA (valido: false) de forma agresiva si el contenido es:
        - Una noticia informativa, estadística o de salud pública.
        - Publicidad, spam, cursos de idiomas (Duolingo, francés, inglés, etc.).
        - Consejos de belleza, fitness genérico, chismes o política.
        - Contenido que no sea una voz humana real compartiendo un problema.

        SOLO VALIDA (valido: true) SI:
        - Detectas un desahogo, confesión o crisis existencial MASCULINA real.
        - El dolor es "Disciplina en Acero" (soledad, falta de rumbo, adicciones).
        - SI TIENES DUDA, DESCARTA. Es mejor tener pocos testimonios puros que basura.

        Si es VALIDO, responde en JSON:
        {{
         "valido": true,
         "problema_principal": "...",
         "emociones": ["..."],
         "creencias": ["..."],
         "sintomas": ["..."],
         "frases_potentes": ["..."],
         "nivel_dolor": 1-4,
         "solucion_miura": "Genera una solucion tactica concreta bajo la doctrina Miura para este dolor especifico, usando lenguaje de Disciplina en Acero (metaforas de industria, forja, presion).",
         "engagement_estimado": 1-1000,
         "arquetipo_sugerido": "Opcional. Si el dolor descrito resuena fuertemente con el arco narrativo de un personaje icónico de videojuego, película o serie conocida en el mundo hispanohablante (ej: Arthur Morgan, Joel, Walter White, Rocky, Maximus), escribe el nombre del personaje. Si no hay match natural, deja string vacío."
        }}

        Escala de dolor: 1 (bajo) a 4 (extremo).
        Texto: {texto}
        """
        try:
            res = brain.generate(prompt)
            res_limpio = res.strip()
            
            # Limpieza agresiva de Markdown y texto extra
            if "```" in res_limpio:
                res_limpio = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', res_limpio, re.DOTALL)
                res_limpio = res_limpio.group(1) if res_limpio else res.strip()
            
            match = re.search(r'\{.*\}', res_limpio, re.DOTALL)
            if match:
                return json.loads(match.group(0))
            else:
                # Si el LLM devolvió un string plano de 'descarte', lo detectamos
                if "valido" in res_limpio.lower() and "false" in res_limpio.lower():
                    return {"valido": False}
                print(f"⚠️ [Researcher] JSON no encontrado en analizar_psicologia: {res_limpio[:200]}")
        except json.JSONDecodeError as e:
            print(f"⚠️ [Researcher] JSON invalido del LLM: {e} — Respuesta: {res[:200]}")
        except Exception as e:
            print(f"⚠️ [Researcher] Error en analisis psicologico: {e}")
        return {"valido": False}

    # ─────────────────────────────────────────────────────────────────────────
    # YOUTUBE
    # ─────────────────────────────────────────────────────────────────────────

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def buscar_youtube_dolor(self, tema):
        """Rastrea testimonios reales en comentarios de YouTube."""
        if not self.youtube: return []
        hallazgos = []
        try:
            search_response = self.youtube.search().list(
                q=f"{tema} hombres testimonios", type="video", part="id,snippet", maxResults=3
            ).execute()
            for item in search_response.get("items", []):
                v_id    = item["id"]["videoId"]
                v_title = item["snippet"]["title"]
                v_url   = f"https://www.youtube.com/watch?v={v_id}"
                try:
                    comments = self.youtube.commentThreads().list(
                        videoId=v_id, part="snippet", maxResults=3, order="relevance"
                    ).execute()
                    for c in comments.get("items", []):
                        snip = c["snippet"]["topLevelComment"]["snippet"]
                        hallazgos.append({
                            "content":    snip["textDisplay"],
                            "url":        v_url,
                            "platform":   "youtube",
                            "source":     v_title,
                            "author":     snip["authorDisplayName"],
                            "engagement": int(snip.get("likeCount", 0)),
                            "query":      tema
                        })
                except Exception as e:
                    print(f"⚠️ [Researcher] Error comentarios YouTube {v_id}: {e}")
                    continue
        except Exception as e:
            print(f"⚠️ [Researcher] Error en busqueda YouTube: {e}")
        return hallazgos

    # ─────────────────────────────────────────────────────────────────────────
    # EXTRACCION Y CLASIFICACION
    # ─────────────────────────────────────────────────────────────────────────

    def extraer_frases_potentes(self, texto):
        """Heuristica para encontrar frases de alto impacto emocional."""
        keywords = [
            "I feel", "I can't", "I ruined", "I hate myself", "I wasted",
            "me siento", "no puedo", "arruine", "odio", "desperdicie",
            "estoy harto", "maldito"
        ]
        frases = []
        partes = re.split(r'[.,!?\n]', texto)
        for p in partes:
            p = p.strip()
            if len(p) > 10 and any(k.lower() in p.lower() for k in keywords):
                frases.append(p)
        return list(set(frases))

    def clasificar_dolor(self, analisis):
        """Mapea el analisis hacia los 12 Dolores Estructurales de Miura."""
        DOLORES = {
            "Proposito perdido":       ["proposito", "vacio", "sentido", "rumbo", "meta", "que hacer"],
            "Falta disciplina":        ["disciplina", "control", "vago", "procrastinacion", "voluntad", "dejar de hacer", "no puedo"],
            "Dopamina":                ["porno", "porn", "paja", "adiccion", "masturbacion", "dopamina", "placer"],
            "Soledad Estructural":     ["solo", "soledad", "amigos", "aislado", "nadie", "aislamiento"],
            "Relaciones Toxicas":      ["novia", "mujer", "pareja", "rechazo", "citas", "ex", "relacion"],
            "Identidad Perdida":       ["identidad", "quien soy", "masculinidad", "hombre", "valor"],
            "Verguenza/Fracaso":       ["verguenza", "fracaso", "perdedor", "humillacion"],
            "Inestabilidad Economica": ["dinero", "trabajo", "sueldo", "pobre", "finanzas", "empleo"],
            "Vacio Espiritual":        ["alma", "dios", "espiritu", "muerte", "trascendencia"],
            "Falta de Respeto":        ["respeto", "autoridad", "ignorado", "valor", "validacion"],
            "Miedo al Futuro":         ["futuro", "arruinado", "tarde", "viejo", "edad"],
            "Paralisis por Analisis":  ["leido", "videos", "paralisis", "analisis", "mental", "informacion"]
        }
        texto_combate = " ".join(
            analisis.get('creencias', []) + [analisis.get('problema_principal', '')]
        ).lower()
        detectados = []
        for d, keys in DOLORES.items():
            if any(k in texto_combate for k in keys):
                detectados.append(d)
        principal   = detectados[0] if detectados else "Identidad Perdida"
        secundarios = detectados[1:] if len(detectados) > 1 else []
        return principal, secundarios

    # ─────────────────────────────────────────────────────────────────────────
    # INTELIGENCIA SEMANAL
    # ─────────────────────────────────────────────────────────────────────────

    def _buscar_serper(self, query, num=10):
        """
        Llama a Serper (Google Search) y devuelve resultados estructurados.
        Más barato que Tavily — solo devuelve links y snippets, no contenido completo.
        Usar como primer filtro para detectar tendencias.
        """
        serper_key = os.getenv("SERPER_API_KEY")
        if not serper_key:
            return []
        
        try:
            resp = requests.post(
                "https://google.serper.dev/search",
                headers={
                    "X-API-KEY": serper_key,
                    "Content-Type": "application/json"
                },
                json={"q": query, "num": num, "hl": "es", "gl": "us"},
                timeout=10
            )
            if resp.status_code == 200:
                data = resp.json()
                resultados = []
                for r in data.get("organic", []):
                    resultados.append({
                        "title": r.get("title", ""),
                        "snippet": r.get("snippet", ""),
                        "url": r.get("link", ""),
                    })
                return resultados
        except Exception as e:
            print(f"⚠️ [Serper] Error en búsqueda: {e}")
        return []

    def detectar_pulso_semanal(self):
        """
        Descubre los 3 temas más calientes de la semana en el nicho masculino.
        Arquitectura: Serper (Google, barato) → Tavily fetch solo en URLs prometedoras.
        """
        print("🔍 [Explorador] Detectando el pulso de la semana...")

        import datetime
        import random
        mes_actual = datetime.datetime.now().strftime("%B %Y")
        
        # Consultamos temas recientes para evitar repetición
        try:
            db = Database()
            if db.investigacion:
                registros = db.investigacion.get_all_records()
                temas_anteriores = list(set([str(r.get('TEMA', '')) for r in registros[-15:]]))
            else:
                temas_anteriores = []
        except:
            temas_anteriores = []

        pilares_dolor = [
            "dating failure loneliness men",
            "career crisis purpose men 2026",
            "discipline burnout motivation men",
            "identity crisis masculinity 2026",
            "fatherhood family struggle men",
            "physical appearance insecurity men",
            "mental health isolation men reddit"
        ]
        
        # Seleccionamos 3 pilares aleatorios + 1 general
        seleccionados = random.sample(pilares_dolor, 3)
        queries_serper = [
            f"{seleccionados[0]} trends {mes_actual}",
            f"{seleccionados[1]} latest discussions 2026",
            f"{seleccionados[2]} confession stories",
            "hombres sufrimiento disciplina tendencia semana"
        ]

        # 1. Serper: recolectar snippets y URLs de Google — barato y rápido
        all_snippets = ""
        urls_prometedoras = []

        for q in queries_serper:
            resultados = self._buscar_serper(q, num=5)
            for r in resultados:
                snippet = r.get("snippet", "")
                url = r.get("url", "")
                titulo = r.get("title", "")
                if snippet:
                    all_snippets += f"\n- {titulo}: {snippet}"
                # Marcar URLs de Reddit y Medium como candidatas a fetch profundo
                if any(d in url for d in ["reddit.com", "medium.com", "substack.com"]):
                    urls_prometedoras.append(url)

        # 2. Tavily fetch quirúrgico — solo en las 2 mejores URLs externas (no Reddit)
        urls_externas = [u for u in urls_prometedoras if "reddit.com" not in u][:2]
        for url in urls_externas:
            try:
                res = self.tavily.extract(urls=[url])
                if res.get("results"):
                    contenido = res["results"][0].get("raw_content", "")[:800]
                    all_snippets += f"\n[DEEP] {contenido}"
            except:
                continue

        if not all_snippets:
            print("⚠️ [Explorador] No se encontró ruido suficiente en la red.")
            return []

        # 3. LLM sintetiza las tendencias desde todo el ruido recolectado
        brain = LLMFactory.get_brain("research_trends")
        prompt = f"""
        Analiza este ruido de la red sobre hombres y desarrollo personal/dolor en la última semana:
        {all_snippets}

        EVITA REPETIR estos temas ya tratados recientemente: {', '.join(temas_anteriores)}
        
        Identifica los 3 TEMAS o DOLORES más recurrentes y específicos que están afectando a los hombres AHORA.
        Para cada tema define:
        1. Nombre del Tema (Gancho corto)
        2. Por qué es tendencia hoy (breve).
        3. Query estratégica para encontrar TESTIMONIOS REALES (raw pain). Usa palabras como "I feel lost", "confesión", "desahogo", "failure" y site:reddit.com.
        
        Responde estrictamente en JSON:
        {{
          "tendencias": [
            {{ "tema": "...", "razon": "...", "query_profunda": "..." }},
            {{ "tema": "...", "razon": "...", "query_profunda": "..." }},
            {{ "tema": "...", "razon": "...", "query_profunda": "..." }}
          ]
        }}
        """
        try:
            res = brain.generate(prompt)
            res_limpio = res.strip()
            if res_limpio.startswith("```"):
                res_limpio = re.sub(r"```(?:json)?", "", res_limpio).strip("`").strip()
            match = re.search(r'\{.*\}', res_limpio, re.DOTALL)
            if match:
                return json.loads(match.group(0)).get('tendencias', [])
            else:
                print(f"⚠️ [Researcher] JSON no encontrado en detectar_pulso: {res_limpio[:200]}")
        except json.JSONDecodeError as e:
            print(f"⚠️ [Researcher] JSON invalido en detectar_pulso: {e}")
        except Exception as e:
            print(f"⚠️ [Researcher] Error sintetizando tendencias: {e}")
        return []

    def extraer_ganchos_virales(self, url):
        """Extrae el Titulo y el Hook de apertura de una fuente viral para el Arsenal."""
        print(f"🎯 [Explorador] Extrayendo ganchos de: {url}")
        content = ""
        title   = ""
        
        if "youtube.com" in url or "youtu.be" in url:
            video_id = None
            if "v=" in url:          video_id = url.split("v=")[1].split("&")[0]
            elif "youtu.be/" in url: video_id = url.split("youtu.be/")[1].split("?")[0]
            if video_id and self.youtube:
                try:
                    res = self.youtube.videos().list(part="snippet", id=video_id).execute()
                    if res.get('items'):
                        snippet = res['items'][0]['snippet']
                        title   = snippet['title']
                        content = snippet['description'][:1500]
                except Exception as e:
                    print(f"⚠️ [Researcher] Error metadatos YouTube {url}: {e}")
        else:
            try:
                res = self.tavily.extract(urls=[url])
                if res.get('results'):
                    content = res['results'][0].get('raw_content', '')
                    title   = res['results'][0].get('url', url)
            except Exception as e:
                print(f"⚠️ [Researcher] Error extrayendo contenido web {url}: {e}")
            
        if not content:
            print(f"⚠️ [Researcher] Sin contenido extraible para: {url}")
            return None

        brain = LLMFactory.get_brain("research_batch")
        prompt = f"""
        Analiza este contenido viral de alto impacto:
        Titulo: {title}
        Contenido/Resumen: {content[:2000]}
        
        Extrae la ingenieria viral:
        1. Titulo Maestro (el mas efectivo detectado o una mejora).
        2. Hook de Apertura (la frase inicial que rompe el scroll).
        3. Plantilla Narrativa (VERDAD INCOMODA, REVELACION, CONFESION, ERROR CRITICO, DESPERTAR, TRAMPA).
        4. Intensidad Viral (1 a 10 basada en impacto emocional).
        
        Responde en JSON:
        {{
          "titulo_maestro": "...",
          "hook_apertura": "...",
          "plantilla": "...",
          "intensidad": 8
        }}
        """
        try:
            res = brain.generate(prompt)
            res_limpio = res.strip()
            if res_limpio.startswith("```"):
                res_limpio = re.sub(r"```(?:json)?", "", res_limpio).strip("`").strip()
            match = re.search(r'\{.*\}', res_limpio, re.DOTALL)
            if match:
                return json.loads(match.group(0))
            else:
                print(f"⚠️ [Researcher] JSON no encontrado en extraer_ganchos: {res_limpio[:200]}")
        except json.JSONDecodeError as e:
            print(f"⚠️ [Researcher] JSON invalido en extraer_ganchos: {e}")
        except Exception as e:
            print(f"⚠️ [Researcher] Error en extraer_ganchos_virales: {e}")
        return None

    def _es_gancho_del_nicho(self, gancho_data):
        """Verifica que el gancho pertenece al nicho masculino hispanohablante."""
        if not gancho_data: return False
        
        texto = (
            (gancho_data.get('titulo_maestro', '') or '') + ' ' +
            (gancho_data.get('hook_apertura', '') or '')
        ).lower()
        
        DOLORES_VALIDOS = [
            "proposito", "propósito", "disciplina", "soledad", "identidad",
            "masculinidad", "hombre", "relacion", "relación", "pareja",
            "fracaso", "vergüenza", "verguenza", "economia", "economía",
            "trabajo", "futuro", "paralisis", "parálisis", "dopamina",
            "adiccion", "adicción", "vacio", "vacío", "depresion", "depresión",
            "ansiedad", "autoengaño", "autoengano", "limite", "límite"
        ]
        
        return any(dolor in texto for dolor in DOLORES_VALIDOS)
