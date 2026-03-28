
import os
import sys
from pypdf import PdfReader

def procesar_pdf_bhatia(ruta_pdf):
    # Obtener solo el nombre del archivo
    nombre_archivo = os.path.basename(ruta_pdf)
    
    # REGLA DE ORO: Debe empezar por DrBhatia (o DR Bhatia para ser resilientes al espacio)
    # El usuario dijo "DrBhatia", pero su archivo tiene espacio. Seremos inteligentes.
    prefijo_esperado = "DrBhatia"
    # Normalizamos para comparar: quitamos espacios y pasamos a minúsculas
    nombre_normalizado = nombre_archivo.replace(" ", "").lower()
    
    if not nombre_normalizado.startswith(prefijo_esperado.lower()):
        print(f"❌ ERROR: El archivo '{nombre_archivo}' no cumple con el protocolo doctrinal.")
        print(f"⚠️ El PDF debe comenzar con el prefijo '{prefijo_esperado}'. Acceso denegado.")
        return False

    print(f"📖 [Lector Doctrinal] Accediendo a la sabiduría de: {nombre_archivo}")
    
    try:
        reader = PdfReader(ruta_pdf)
        texto_completo = ""
        for page in reader.pages:
            texto_completo += page.extract_text() + "\n"
        
        if not texto_completo.strip():
            print("⚠️ El PDF parece estar vacío o no contiene texto extraíble.")
            return False
            
        print(f"✅ Sabiduría extraída con éxito ({len(texto_completo)} caracteres).")
        return texto_completo
        
    except Exception as e:
        print(f"❌ Error crítico leyendo el PDF: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python lector_doctrinal_bhatia.py <ruta_al_pdf>")
    else:
        procesar_pdf_bhatia(sys.argv[1])
