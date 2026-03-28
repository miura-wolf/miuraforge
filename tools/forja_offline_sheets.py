import os
import sys
import re
import unicodedata
from dotenv import load_dotenv

# Aseguramos acceso a los módulos core
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from core.database import Database
from core.voice_director import VoiceDirector

def _sanitizar_nombre(texto):
    """Convierte un título en un nombre de archivo seguro."""
    if not texto: return "SIN_TITULO"
    # Normalizar (quitar acentos)
    texto = unicodedata.normalize('NFKD', str(texto)).encode('ascii', 'ignore').decode('ascii')
    # Solo alfanuméricos y espacios
    texto = re.sub(r'[^a-zA-Z0-9\s-]', '', texto)
    # Espacios a guiones bajos y a mayúsculas
    return re.sub(r'[\s-]+', '_', texto).strip('_').upper()

def forja_offline_desde_sheets():
    load_dotenv()
    
    console_width = 70
    print("=" * console_width)
    print(" 🎙️  MIURA FORGE - PRUEBA DE VOZ OFFLINE (SHEETS) ".center(console_width, "X"))
    print("=" * console_width)

    # 1. Conectar a la Base de Datos
    db = Database()
    
    # 2. Inicializar Director de Voz
    andres = VoiceDirector()
    
    if not andres._supertonic_disponible:
        print("❌ Error: Supertonic no está disponible.")
        return

    # 3. Obtener el último guion redactado (Tabla PRODUCCION)
    print("\n🔍 Buscando la última redacción estratégica en Google Sheets...")
    produccion = db.produccion.get_all_records()
    
    if not produccion:
        print("❌ No hay registros en la tabla PRODUCCION.")
        return

    # Tomamos el último registro
    ultimo_registro = produccion[-1]
    guion_completo = ultimo_registro.get("Guion", "")
    id_master = ultimo_registro.get("ID", "TEST_OFFLINE")

    # Intentar obtener título para el nombre
    titulo_raw = db.obtener_titulo_video(id_master)
    titulo_clean = _sanitizar_nombre(titulo_raw if titulo_raw else id_master)
    
    if not guion_completo:
        print("⚠️ El último registro no tiene GUION_REDACTADO.")
        return

    print(f"📄 Guion detectado (ID: {id_master})")
    if titulo_raw: print(f"🎬 Título: {titulo_raw}")
    print(f"📝 Inicio del texto: {guion_completo[:100]}...")

    # 4. Forjar Voz Offline (Supertonic)
    output_path = f"output/VOZ_OFFLINE_{titulo_clean}.wav"
    os.makedirs("output", exist_ok=True)

    print(f"\n🔥 Iniciando transmutación de voz vía SUPERTONIC M4 (Offline)...")
    texto_purificado = andres._purificar_texto(guion_completo)
    exito = andres._generar_supertonic(texto_purificado, output_path)

    if exito:
        print("\n" + "=" * console_width)
        print(f"✅ ¡FORJA COMPLETADA!".center(console_width))
        print(f"📁 Ubicación: {output_path}".center(console_width))
        print("=" * console_width)
        print("Soberano, la voz ha sido grabada en el búnker. Verifique el archivo.")
    else:
        print("\n❌ La forja ha fallado. Revisa los logs superiores.")

if __name__ == "__main__":
    forja_offline_desde_sheets()
