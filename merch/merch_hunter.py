"""
merch_hunter.py — El Cazador de Frases para Merch
===================================================
Mina la tabla PRODUCCION en Google Sheets, extrae frases
con potencial de merch (camisetas, gorras, libretas, posters)
y las registra en la tabla MERCH_CANDIDATAS para revisión del Sultán.

Criterios de selección:
  — Guiones con ADN Disciplina en Acero ≥ 8 (puntuación del Auditor)
  — Frases de 3 a 10 palabras
  — Sin palabras prohibidas de la doctrina
  — Clasificadas por formato de producto sugerido

Uso:
  python merch_hunter.py --cazar         ← Minea PRODUCCION y llena MERCH_CANDIDATAS
  python merch_hunter.py --ver           ← Muestra candidatas pendientes de revisión
  python merch_hunter.py --aprobar       ← Revisión interactiva una por una
  python merch_hunter.py --exportar      ← Genera lista final aprobada en TXT
  python merch_hunter.py --verificar     ← Test de conexión con Sheets

Variables de entorno (mismo .env del motor Miura):
  GOOGLE_SHEET_ID           → ID del spreadsheet
  GOOGLE_JSON_CREDENTIALS   → ruta al JSON de credenciales
  OPENAI_API_KEY            → Nvidia NIM (para refinamiento con IA)
  OPENAI_BASE_URL           → https://integrate.api.nvidia.com/v1
#   OPENAI_MODEL              → mistralai/mistral-large-3 (vía Factory)
"""

import os
import re
import sys
import time
import argparse
import datetime
import gspread
from google.oauth2.service_account import Credentials
from dotenv import load_dotenv
from pathlib import Path

# Importar configuración centralizada
try:
    sys.path.append(str(Path(__file__).resolve().parent.parent))
    from core.config import CREDENTIALS_PATH as DEFAULT_CREDS_PATH
except ImportError:
    DEFAULT_CREDS_PATH = Path("credentials.json")

try:
    from openai import OpenAI as OpenAIClient

    NVIDIA_DISPONIBLE = True
except ImportError:
    NVIDIA_DISPONIBLE = False

load_dotenv()

# ─── CONFIGURACIÓN ────────────────────────────────────────────────────
SHEETS_ID = os.getenv("GOOGLE_SHEET_ID", os.getenv("GOOGLE_SHEETS_ID", ""))
# Prioridad: variable de entorno > configuración centralizada > fallback legacy
CREDS_PATH = os.getenv(
    "GOOGLE_JSON_CREDENTIALS", os.getenv("GOOGLE_CREDENTIALS_PATH", str(DEFAULT_CREDS_PATH))
)
NVIDIA_KEY = os.getenv("OPENAI_API_KEY", "")
NVIDIA_URL = os.getenv("OPENAI_BASE_URL", "https://integrate.api.nvidia.com/v1")
NVIDIA_MOD = os.getenv("OPENAI_MODEL", "deepseek-ai/deepseek-v3.1")  # Usar variable de entorno

SCOPES = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]

# ─── DOCTRINA — PALABRAS PROHIBIDAS ───────────────────────────────────
# Palabras que NO deben aparecer en frases de merch (voz Andrés)
PALABRAS_PROHIBIDAS = [
    "sentir",
    "sentirte",
    "sientes",
    "siento",
    "inspiración",
    "inspirar",
    "inspirado",
    "potencial",
    "camino",
    "viaje",
    "proceso",
    "crecer",
    "crecimiento",
    "evolución",
    "evolucionar",
    "amor propio",
    "autoestima",
    "bienestar",
    "feliz",
    "felicidad",
    "alegría",
    "motiva",
    "motivación",
    "motivar",
    "interior",
    "alma",
    "espíritu",
    "espiritual",
    "maravilloso",
    "increíble",
    "extraordinario",
    "positivo",
    "positiva",
    "mentalidad positiva",
    "abundancia",
    "manifestar",
    "universo",
    "perdón",
    "perdonar",
    "sanar",
    "sanación",
]

# ─── FORMATOS DE MERCH Y SUS REGLAS ───────────────────────────────────
FORMATOS = {
    "CAMISETA": {"min_palabras": 3, "max_palabras": 7, "emoji": "👕"},
    "GORRA": {"min_palabras": 2, "max_palabras": 5, "emoji": "🧢"},
    "LIBRETA": {"min_palabras": 5, "max_palabras": 12, "emoji": "📓"},
    "POSTER": {"min_palabras": 4, "max_palabras": 10, "emoji": "🖼️"},
    "ACCESORIO": {"min_palabras": 2, "max_palabras": 6, "emoji": "⚔️"},
}

# Columnas de la tabla MERCH_CANDIDATAS
COLS_MERCH = [
    "FECHA",
    "FRASE",
    "FORMATO_SUGERIDO",
    "PUNTUACION_ADN",
    "ID_PRODUCCION",
    "CLUSTER",
    "ESTADO",
    "NOTAS",
]


# ─── CONEXIÓN SHEETS ──────────────────────────────────────────────────
def conectar_sheets():
    creds = Credentials.from_service_account_file(CREDS_PATH, scopes=SCOPES)
    client = gspread.authorize(creds)
    return client.open_by_key(SHEETS_ID)


def obtener_o_crear_hoja(ss, nombre, encabezados):
    """Obtiene la hoja si existe, la crea con encabezados si no."""
    try:
        return ss.worksheet(nombre)
    except gspread.exceptions.WorksheetNotFound:
        hoja = ss.add_worksheet(title=nombre, rows=500, cols=len(encabezados))
        hoja.append_row(encabezados)
        print(f"✅ [Sheets] Tabla '{nombre}' creada con encabezados.")
        return hoja


# ─── EXTRACCIÓN DE FRASES ─────────────────────────────────────────────
def limpiar_frase(frase):
    """Normaliza y limpia una frase candidata."""
    frase = frase.strip()
    frase = re.sub(r"\s+", " ", frase)
    # Capitalizar primera letra
    if frase:
        frase = frase[0].upper() + frase[1:]
    # Asegurar punto final si no tiene puntuación
    if frase and frase[-1] not in ".!?":
        frase += "."
    return frase


def contiene_prohibidas(frase):
    """Retorna True si la frase contiene palabras prohibidas."""
    frase_lower = frase.lower()
    for palabra in PALABRAS_PROHIBIDAS:
        if palabra in frase_lower:
            return True
    return False


def contar_palabras(frase):
    """Cuenta palabras reales (sin puntuación)."""
    return len(re.findall(r"\b\w+\b", frase))


def clasificar_formato(frase):
    """
    Determina el formato de merch más adecuado según longitud y tono.
    Retorna lista de formatos compatibles.
    """
    n = contar_palabras(frase)
    compatibles = []
    for formato, reglas in FORMATOS.items():
        if reglas["min_palabras"] <= n <= reglas["max_palabras"]:
            compatibles.append(formato)

    # Reglas de tono adicionales
    frase_lower = frase.lower()
    if any(w in frase_lower for w in ["construye", "forja", "ejecuta", "corta", "mide"]):
        # Verbos imperativos → camiseta y gorra primero
        compatibles = sorted(
            compatibles,
            key=lambda x: (
                ["CAMISETA", "GORRA", "ACCESORIO", "LIBRETA", "POSTER"].index(x)
                if x in ["CAMISETA", "GORRA", "ACCESORIO", "LIBRETA", "POSTER"]
                else 99
            ),
        )

    return compatibles[0] if compatibles else "POSTER"


def extraer_frases_de_guion(texto_guion):
    """
    Extrae frases candidatas de un guion.
    Separa por puntos, saltos de línea y punto y coma.
    """
    candidatas = []
    # Separar por delimitadores
    partes = re.split(r"[.\n;!?]+", texto_guion)
    for parte in partes:
        frase = limpiar_frase(parte)
        if not frase or len(frase) < 10:
            continue
        n_palabras = contar_palabras(frase)
        if n_palabras < 2 or n_palabras > 15:
            continue
        if contiene_prohibidas(frase):
            continue
        candidatas.append(frase)
    return candidatas


def puntuar_frase_merch(frase):
    """
    Score de potencial merch (0-10).
    Basado en: impacto, brevedad, doctrina, imperativo.
    """
    score = 5.0
    n = contar_palabras(frase)
    frase_lower = frase.lower()

    # Brevedad (ideal 4-7 palabras)
    if 4 <= n <= 7:
        score += 2.0
    elif n <= 3:
        score += 1.5
    elif n > 10:
        score -= 1.5

    # Verbos de acción / imperativos
    imperativos = [
        "construye",
        "forja",
        "corta",
        "ejecuta",
        "rompe",
        "mide",
        "bloquea",
        "calcula",
        "define",
        "instala",
    ]
    if any(v in frase_lower for v in imperativos):
        score += 1.5

    # Palabras de doctrina Miura
    doctrina = [
        "acero",
        "forja",
        "hierro",
        "martillo",
        "yunque",
        "soldadura",
        "cadena",
        "fricción",
        "estructura",
        "metal",
    ]
    hits = sum(1 for d in doctrina if d in frase_lower)
    score += min(hits * 0.5, 1.5)

    # Penalizar si suena a autoayuda genérica
    genericas = ["siempre", "nunca", "todo", "nada", "quizás", "tal vez"]
    if any(g in frase_lower for g in genericas):
        score -= 1.0

    return round(min(max(score, 0), 10), 1)


# ─── REFINAMIENTO CON NVIDIA (OPCIONAL) ───────────────────────────────
def refinar_con_factory(frases_candidatas, cluster):
    """
    Pide a LLMFactory que seleccione y refine las 3 mejores frases
    para merch desde la lista de candidatas.
    """
    from llm.factory import LLMFactory

    brain = LLMFactory.get_brain("merch")

    lista = "\n".join([f"- {f}" for f in frases_candidatas[:20]])
    prompt = f"""Eres el curador de merch de Disciplina en Acero.
El canal habla con voz industrial, directa, sin consuelo vacío.
Tema del guion: {cluster}

De estas frases candidatas, selecciona las 3 mejores para estampar en merch (camisetas, gorras, libretas).
Criterios: brevedad, impacto, voz de Andrés (no motivacional, sí doctrinal).

Frases candidatas:
{lista}

Responde SOLO con las 3 frases seleccionadas, una por línea, sin numeración ni explicación.
Si alguna necesita ajuste mínimo de redacción, aplícalo."""

    try:
        texto = brain.generate(prompt, temperature=0.7, max_tokens=200)
        refinadas = [limpiar_frase(l) for l in texto.split("\n") if l.strip()]
        return refinadas[:3]
    except Exception as e:
        print(f"⚠️ [Nvidia] Refinamiento fallido: {e}")
        return None


# ─── OPERACIONES PRINCIPALES ──────────────────────────────────────────


def cazar_frases():
    """
    Lee PRODUCCION, extrae frases con potencial merch,
    las registra en MERCH_CANDIDATAS.
    """
    print("\n⚔️  [Cazador] Iniciando cacería de frases...\n")
    ss = conectar_sheets()

    # Obtener tabla PRODUCCION
    try:
        hoja_prod = ss.worksheet("PRODUCCION")
        produccion = hoja_prod.get_all_records()
    except gspread.exceptions.WorksheetNotFound:
        print("❌ Tabla PRODUCCION no encontrada.")
        return

    if not produccion:
        print("❌ PRODUCCION está vacía.")
        return

    # Obtener o crear MERCH_CANDIDATAS
    hoja_merch = obtener_o_crear_hoja(ss, "MERCH_CANDIDATAS", COLS_MERCH)
    existentes = hoja_merch.get_all_records()
    frases_ya_registradas = {r.get("FRASE", "").strip().lower() for r in existentes}

    # Filtrar guiones con ADN ≥ 8
    guiones_validos = []
    for row in produccion:
        adn_raw = str(row.get("ADN_ACERO", row.get("PUNTUACION_ADN", "0")))
        try:
            adn = float(re.search(r"[\d.]+", adn_raw).group())
        except:
            adn = 0
        if adn >= 8:
            guiones_validos.append(row)

    print(f"📊 Guiones en PRODUCCION: {len(produccion)}")
    print(f"📊 Guiones con ADN ≥ 8:  {len(guiones_validos)}")
    print(f"📊 Frases ya registradas: {len(frases_ya_registradas)}\n")

    total_nuevas = 0

    for row in guiones_validos:
        id_prod = str(row.get("ID_PRODUCCION", row.get("ID", ""))).strip()
        cluster = str(row.get("CLUSTER", row.get("NUCLEO_DOLOR", ""))).strip()
        guion = str(row.get("GUION_FINAL", row.get("GUION_MASTER", row.get("GUION", "")))).strip()
        adn_raw = str(row.get("ADN_ACERO", row.get("PUNTUACION_ADN", "8")))

        try:
            adn = float(re.search(r"[\d.]+", adn_raw).group())
        except:
            adn = 8.0

        if not guion:
            continue

        print(f"🔍 Analizando: {id_prod} — {cluster}")

        # Extraer candidatas localmente
        candidatas = extraer_frases_de_guion(guion)

        if not candidatas:
            print(f"   Sin candidatas válidas.\n")
            continue

        # Refinamiento con Factory (top 3 curatoriales)
        refinadas = refinar_con_factory(candidatas, cluster)

        # Usar refinadas si existen, sino top 3 por score local
        if refinadas:
            print(f"   ✅ [Nvidia] {len(refinadas)} frases refinadas")
            seleccion = refinadas
        else:
            scored = sorted(candidatas, key=puntuar_frase_merch, reverse=True)
            seleccion = scored[:3]

        nuevas_este_guion = 0
        for frase in seleccion:
            if not frase or frase.lower() in frases_ya_registradas:
                continue

            formato = clasificar_formato(frase)
            score = puntuar_frase_merch(frase)
            fecha = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

            fila = [fecha, frase, formato, adn, id_prod, cluster, "PENDIENTE", ""]
            hoja_merch.append_row(fila)
            frases_ya_registradas.add(frase.lower())
            nuevas_este_guion += 1
            total_nuevas += 1

            emoji = FORMATOS.get(formato, {}).get("emoji", "📦")
            print(f"   {emoji} [{formato}] {frase}")
            time.sleep(0.3)  # pausa cortés con Sheets

        if nuevas_este_guion == 0:
            print(f"   Sin frases nuevas (ya registradas).")
        print()

    print(f"━" * 60)
    print(f"✅ Cacería completada. Frases nuevas registradas: {total_nuevas}")
    print(f"   Revísalas en la tabla MERCH_CANDIDATAS de Sheets.")
    print(f"   Luego corre: python merch_hunter.py --aprobar\n")


def ver_candidatas():
    """Muestra todas las frases PENDIENTES de revisión."""
    print("\n⚔️  [Cazador] Cargando candidatas pendientes...\n")
    ss = conectar_sheets()

    try:
        hoja = ss.worksheet("MERCH_CANDIDATAS")
        datos = hoja.get_all_records()
    except gspread.exceptions.WorksheetNotFound:
        print("❌ Tabla MERCH_CANDIDATAS no encontrada. Corre --cazar primero.")
        return

    pendientes = [r for r in datos if r.get("ESTADO", "") == "PENDIENTE"]

    if not pendientes:
        print("✅ No hay frases pendientes de revisión.")
        return

    print(f"{'─' * 65}")
    print(f"  {'FORMATO':<12} {'ADN':<6} {'CLUSTER':<22} FRASE")
    print(f"{'─' * 65}")

    por_formato = {}
    for r in pendientes:
        fmt = r.get("FORMATO_SUGERIDO", "?")
        por_formato.setdefault(fmt, []).append(r)

    for fmt, filas in sorted(por_formato.items()):
        emoji = FORMATOS.get(fmt, {}).get("emoji", "📦")
        for r in filas:
            adn = r.get("PUNTUACION_ADN", "?")
            cluster = str(r.get("CLUSTER", ""))[:20]
            frase = r.get("FRASE", "")
            print(f"  {emoji} {fmt:<11} {str(adn):<6} {cluster:<22} {frase}")
        print()

    print(f"{'─' * 65}")
    print(f"  Total pendientes: {len(pendientes)}")
    print(f"  Para revisar: python merch_hunter.py --aprobar\n")


def aprobar_interactivo():
    """Revisión interactiva frase por frase — aprueba, rechaza o edita."""
    print("\n⚔️  [Cazador] Modo revisión interactiva...\n")
    ss = conectar_sheets()

    try:
        hoja = ss.worksheet("MERCH_CANDIDATAS")
        todos = hoja.get_all_values()
    except gspread.exceptions.WorksheetNotFound:
        print("❌ Tabla MERCH_CANDIDATAS no encontrada.")
        return

    if len(todos) < 2:
        print("❌ Sin datos en MERCH_CANDIDATAS.")
        return

    encabezados = todos[0]
    filas = todos[1:]

    idx_frase = encabezados.index("FRASE") if "FRASE" in encabezados else 1
    idx_formato = encabezados.index("FORMATO_SUGERIDO") if "FORMATO_SUGERIDO" in encabezados else 2
    idx_estado = encabezados.index("ESTADO") if "ESTADO" in encabezados else 6
    idx_notas = encabezados.index("NOTAS") if "NOTAS" in encabezados else 7
    idx_cluster = encabezados.index("CLUSTER") if "CLUSTER" in encabezados else 5

    pendientes = [
        (i, row)
        for i, row in enumerate(filas)
        if len(row) > idx_estado and row[idx_estado] == "PENDIENTE"
    ]

    if not pendientes:
        print("✅ Sin frases pendientes.")
        return

    aprobadas = rechazadas = editadas = 0

    for i, (idx_fila, row) in enumerate(pendientes):
        frase = row[idx_frase] if len(row) > idx_frase else ""
        formato = row[idx_formato] if len(row) > idx_formato else ""
        cluster = row[idx_cluster] if len(row) > idx_cluster else ""
        emoji = FORMATOS.get(formato, {}).get("emoji", "📦")

        print(f"\n{'━' * 60}")
        print(f"  [{i + 1}/{len(pendientes)}] {emoji} {formato}")
        print(f"  Cluster: {cluster}")
        print(f"\n  ❝ {frase} ❞\n")
        print(f"  [s] Aprobar   [n] Rechazar   [e] Editar   [q] Salir")

        accion = input("  ⚔️  Tu decisión: ").strip().lower()

        fila_sheets = idx_fila + 2  # +1 encabezado, +1 base 1

        if accion == "s":
            hoja.update_cell(fila_sheets, idx_estado + 1, "APROBADA")
            print(f"  ✅ APROBADA")
            aprobadas += 1

        elif accion == "n":
            motivo = input("  Motivo (opcional): ").strip()
            hoja.update_cell(fila_sheets, idx_estado + 1, "RECHAZADA")
            if motivo:
                hoja.update_cell(fila_sheets, idx_notas + 1, motivo)
            print(f"  ❌ RECHAZADA")
            rechazadas += 1

        elif accion == "e":
            nueva = input(f"  Nueva frase (ENTER para cancelar): ").strip()
            if nueva:
                nuevo_formato = clasificar_formato(nueva)
                nuevo_emoji = FORMATOS.get(nuevo_formato, {}).get("emoji", "📦")
                hoja.update_cell(fila_sheets, idx_frase + 1, nueva)
                hoja.update_cell(fila_sheets, idx_formato + 1, nuevo_formato)
                hoja.update_cell(fila_sheets, idx_estado + 1, "APROBADA")
                print(f"  ✏️  Editada → {nuevo_emoji} [{nuevo_formato}] {nueva}")
                print(f"  ✅ APROBADA")
                aprobadas += 1
                editadas += 1

        elif accion == "q":
            print("\n  [Cazador] Revisión interrumpida.")
            break

        time.sleep(0.3)

    print(f"\n{'━' * 60}")
    print(f"  Sesión completada:")
    print(f"  ✅ Aprobadas: {aprobadas} ({editadas} editadas)")
    print(f"  ❌ Rechazadas: {rechazadas}")
    print(f"\n  Para exportar: python merch_hunter.py --exportar\n")


def exportar_aprobadas():
    """Genera lista final de frases aprobadas en TXT y la imprime."""
    print("\n⚔️  [Cazador] Exportando frases aprobadas...\n")
    ss = conectar_sheets()

    try:
        hoja = ss.worksheet("MERCH_CANDIDATAS")
        datos = hoja.get_all_records()
    except gspread.exceptions.WorksheetNotFound:
        print("❌ Tabla MERCH_CANDIDATAS no encontrada.")
        return

    aprobadas = [r for r in datos if r.get("ESTADO", "") == "APROBADA"]

    if not aprobadas:
        print("❌ Sin frases aprobadas todavía. Corre --aprobar primero.")
        return

    # Agrupar por formato
    por_formato = {}
    for r in aprobadas:
        fmt = r.get("FORMATO_SUGERIDO", "OTRO")
        por_formato.setdefault(fmt, []).append(r)

    # Generar TXT
    lineas = []
    lineas.append("⚔️  DISCIPLINA EN ACERO — FRASES PARA MERCH")
    lineas.append(f"   Generado: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}")
    lineas.append("=" * 60)

    for fmt, filas in sorted(por_formato.items()):
        emoji = FORMATOS.get(fmt, {}).get("emoji", "📦")
        lineas.append(f"\n{emoji}  {fmt} ({len(filas)} frases)")
        lineas.append("─" * 40)
        for r in filas:
            frase = r.get("FRASE", "")
            cluster = r.get("CLUSTER", "")
            lineas.append(f"  • {frase}")
            lineas.append(f"    [{cluster}]")

    lineas.append("\n" + "=" * 60)
    lineas.append(f"  TOTAL: {len(aprobadas)} frases aprobadas")

    salida = "\n".join(lineas)
    print(salida)

    # Guardar en archivo
    nombre_archivo = f"MERCH_FRASES_{datetime.datetime.now().strftime('%Y%m%d_%H%M')}.txt"
    with open(nombre_archivo, "w", encoding="utf-8") as f:
        f.write(salida)

    print(f"\n✅ Archivo guardado: {nombre_archivo}\n")


def verificar_config():
    """Test de conexión con Sheets y Nvidia."""
    print("\n🔍 [Cazador] Verificando configuración...\n")
    errores = []

    if not SHEETS_ID:
        errores.append("❌ GOOGLE_SHEET_ID no configurado")
    else:
        try:
            ss = conectar_sheets()
            hojas = [h.title for h in ss.worksheets()]
            print(f"✅ Sheets conectado.")
            print(f"   Hojas disponibles: {', '.join(hojas)}")
            tiene_produccion = "PRODUCCION" in hojas
            print(
                f"   {'✅' if tiene_produccion else '⚠️ '} Tabla PRODUCCION: {'encontrada' if tiene_produccion else 'NO encontrada'}"
            )
        except Exception as e:
            errores.append(f"❌ Sheets error: {e}")

    if not NVIDIA_KEY:
        print("⚠️  OPENAI_API_KEY (Nvidia) no configurada — refinamiento IA desactivado")
    else:
        print(f"✅ Nvidia Key detectada (comienza por {NVIDIA_KEY[:8]}...)")
        print(f"   Modelo: {NVIDIA_MOD}")

    if errores:
        print("\n".join(errores))
        return False

    print("\n✅ El Cazador está listo para operar.\n")
    return True


# ─── CLI ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="⚔️  Merch Hunter — Disciplina en Acero",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument(
        "--cazar", action="store_true", help="Minea PRODUCCION y registra candidatas"
    )
    parser.add_argument("--ver", action="store_true", help="Muestra candidatas pendientes")
    parser.add_argument(
        "--aprobar", action="store_true", help="Revisión interactiva frase por frase"
    )
    parser.add_argument("--exportar", action="store_true", help="Exporta frases aprobadas a TXT")
    parser.add_argument(
        "--verificar", action="store_true", help="Verifica conexión con Sheets y Nvidia"
    )

    args = parser.parse_args()

    if args.verificar:
        verificar_config()
    elif args.cazar:
        cazar_frases()
    elif args.ver:
        ver_candidatas()
    elif args.aprobar:
        aprobar_interactivo()
    elif args.exportar:
        exportar_aprobadas()
    else:
        parser.print_help()
