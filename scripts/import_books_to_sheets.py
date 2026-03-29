"""
Importador de Libros a la Forja (Búnker)
=======================================
Lee Docs/blog_ideas.txt y carga 50 libros en la tabla BLOG_CONTENIDO
de Google Sheets con estado 'pendiente_oraculo'.
"""

import os
import sys
import re
import datetime
from pathlib import Path

# Ajustar path para importar módulos de core
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from core.database import Database

def parsear_libros(archivo_txt="Docs/blog_ideas.txt"):
    """
    Parsea el archivo txt y devuelve una lista de diccionarios:
    [{'titulo': 'Ragnarok: El Camino de un Hombre', 'autor': 'Hombres Peligrosos', 'categoria': 'Desarrollo Masculino y Autoconocimiento', 'prioridad': 0}]
    """
    ruta = Path(__file__).parent.parent / "Docs" / "blog_ideas.txt"
    if not ruta.exists():
        print(f"❌ No se encuentra {ruta}")
        return []

    libros = []
    categoria_actual = "Libros"
    
    # Priority 1 exact matches based on the user's text
    prioridad_1 = [
        "Atomic Habits", 
        "Can't Hurt Me", 
        "El Sutil Arte de que Todo le Importe un C*o**", 
        "Padre Rico Padre Pobre", 
        "El Hombre en Busca de Sentido"
    ]

    with open(ruta, "r", encoding="utf-8") as f:
        lineas = f.readlines()

    for linea in lineas:
        linea = linea.strip()
        if not linea:
            continue
            
        # Detectar bloques de categoría
        if linea.startswith("BLOQUE"):
            # Ejemplo: BLOQUE 1 — Desarrollo Masculino y Autoconocimiento
            partes = linea.split("—")
            if len(partes) > 1:
                categoria_actual = partes[1].strip()
            continue
            
        # Ignorar comentarios entre paréntesis y otras líneas de texto general
        if linea.startswith("(") or linea.startswith("Sobre la idea") or linea.startswith("La katana"):
            continue
            
        # Un libro válido suele tener un guion largo "—" o medio "-"
        if "—" in linea or ("-" in linea and "Prioridad" not in linea):
            # Ignorar las líneas descriptivas del final de Prioridad 1, 2, 3
            if linea.startswith("Prioridad"):
                continue
                
            sep = "—" if "—" in linea else "-"
            partes_libro = linea.split(sep, 1)
            
            titulo = partes_libro[0].strip()
            autor = partes_libro[1].strip()
            
            # Limpiar comentarios de (versión español) del autor
            autor = re.sub(r'\(.*?\)', '', autor).strip()
            
            es_prioridad_1 = "FALSE"
            for p1 in prioridad_1:
                if p1.lower() in titulo.lower() or titulo.lower() in p1.lower():
                    es_prioridad_1 = "TRUE"
                    break
                    
            libros.append({
                "titulo": titulo,
                "autor": autor,
                "categoria": categoria_actual,
                "featured": es_prioridad_1
            })

    return libros

def importar_a_sheets():
    print("📚 Iniciando importación masiva al Búnker...")
    db = Database()
    
    if not db.blog_contenido:
        print("❌ Tabla BLOG_CONTENIDO no encontrada en el Búnker.")
        return

    libros = parsear_libros()
    if not libros:
        print("❌ No se parseó ningún libro.")
        return
        
    print(f"✅ Se identificaron {len(libros)} libros para importar.")
    
    # Obtener ID inicial (basado en los registros existentes)
    try:
        registros_existentes = db.blog_contenido.get_all_records()
        siguiente_id = len(registros_existentes) + 1
    except:
        siguiente_id = 1
        
    fecha_hoy = datetime.datetime.now().strftime("%Y-%m-%d")
    
    # Preparar el lote para bulk insert
    filas_a_insertar = []
    
    for l in libros:
        # Columna orden (depende de tu estructura en Google Sheets)
        # 1: ID, 2: Estado (Publicación), 3: Título, 4: Slug, 5: Fecha, 6: Descripción
        # 7: Keywords, 8: Categoría, 9: Imagen_URL, 10: Enlace_Afiliado, 11: Cuerpo_Raw
        # 12: Tags, 13: ReadTime_Min, 14: Featured, 15: ANCLA_VERDAD, 16: LIBRO_ESTADO
        
        titulo_completo = f"{l['titulo']} de {l['autor']}"
        slug = l['titulo'].lower().replace(" ", "-").replace("á","a").replace("é","e").replace("í","i").replace("ó","o").replace("ú","u")
        slug = re.sub(r'[^a-z0-9-]', '', slug)
        
        fila = [
            siguiente_id,            # ID
            "borrador",              # Estado (de Astro)
            titulo_completo,         # Título
            slug,                    # Slug
            fecha_hoy,               # Fecha
            "",                      # Descripción
            "libro, reseña, disciplina", # Keywords
            l['categoria'],          # Categoría
            "",                      # Imagen_URL
            "",                      # Enlace_Afiliado (para amazon)
            "",                      # Cuerpo_Raw
            "libros",                # Tags
            "5",                     # ReadTime_Min
            l['featured'],           # Featured
            "",                      # ANCLA_VERDAD
            "pendiente_oraculo"      # LIBRO_ESTADO (¡El detonante!)
        ]
        filas_a_insertar.append(fila)
        siguiente_id += 1
        
    # Insertar en lote
    if filas_a_insertar:
        print(f"⏳ Inyectando {len(filas_a_insertar)} libros en la matriz de Google Sheets...")
        db.blog_contenido.append_rows(filas_a_insertar)
        print("✅ Importación completada. 50 libros están ahora en el Búnker esperando al Oráculo.")
        
        # Resumen
        prioridad_1 = [f for f in filas_a_insertar if f[13] == "TRUE"]
        print(f"\n🔥 {len(prioridad_1)} libros marcados como PRIORIDAD 1 (Featured).")
        for p in prioridad_1:
            print(f"   - {p[2]}")

if __name__ == "__main__":
    importar_a_sheets()
