"""
Ejecutor del Oráculo Híbrido para Reseñas de Bloque
===================================================
Toma los libros en estado 'pendiente_oraculo' de BLOG_CONTENIDO,
pasa a NotebookLM (Hybrid Oracle) para extraer el briefing doctrinal
y la 'Voz del Pueblo' (Ancla Social), rellenando las columnas ANCLA_VERDAD
y CUERPO_RAW, y luego los pasa a 'ancla_lista' para el Alchemist.
"""

import sys
import os
import time

# Permite cargar el core
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from core.database import Database
from core.hybrid_oracle import HybridOracle

def run_oracle_for_featured():
    print("🔮 ORÁCULO HÍBRIDO — PROCESAMIENTO DE BLOGS")
    print("=" * 50)
    
    db = Database()
    if not db.blog_contenido:
        print("❌ Error: Hoja BLOG_CONTENIDO no accesible.")
        return

    registros = db.blog_contenido.get_all_records()
    headers = db.blog_contenido.row_values(1)
    
    col_id = headers.index("ID") + 1
    col_estado = headers.index("LIBRO_ESTADO") + 1
    col_cuerpo = headers.index("Cuerpo_Raw") + 1
    col_ancla = headers.index("ANCLA_VERDAD") + 1
    
    # Filtrar Prioridad 1 : Featured = TRUE y pendiente de oráculo
    libros_target = []
    for i, r in enumerate(registros):
        estado_actual = str(r.get("LIBRO_ESTADO", "")).strip().lower()
        es_featured = str(r.get("Featured", "")).strip().upper()
        
        if estado_actual == "pendiente_oraculo" and es_featured == "TRUE":
            libros_target.append({
                "row_index": i + 2, # +1 para cabecera, +1 índice 0
                "id": str(r.get("ID")),
                "titulo": str(r.get("Título"))
            })
            
    if not libros_target:
        print("✅ No hay libros PRIORIDAD 1 (Featured) en estado 'pendiente_oraculo'.")
        return
        
    print(f"🎯 Dispuesto a forjar doctrina para {len(libros_target)} libros de Prioridad 1.")
    
    oracle = HybridOracle()
    
    for l in libros_target:
        titulo = l['titulo']
        row_idx = l['row_index']
        
        try:
            # Investigar a traves del Oraculo Hibrido
            result = oracle.investigar_libro(titulo_libro=titulo)
            
            if result.get("exito"):
                briefing = result.get("briefing", "")
                ancla_social = result.get("ancla_social", "")
                
                # Actualizar Data en Sheets
                # Cuerpo_Raw = Briefing
                db.blog_contenido.update_cell(row_idx, col_cuerpo, briefing)
                # ANCLA_VERDAD = Ancla Social
                if ancla_social:
                    db.blog_contenido.update_cell(row_idx, col_ancla, ancla_social)
                # Estado = ancla_lista
                db.blog_contenido.update_cell(row_idx, col_estado, "ancla_lista")
                
                print(f"🔥 Libro '{titulo}' forjado con Ancla Social. Estado: ancla_lista")
            else:
                print(f"⚠️ Error al forjar '{titulo}': {result.get('error')}")
                # Marcar como error para no trabar el proceso
                db.blog_contenido.update_cell(row_idx, col_estado, "error_oraculo")
        except Exception as e:
            print(f"❌ Error crítico procesando '{titulo}': {e}")
        
        # Ritmo para no saturar 
        print("⏳ Enfriando oráculo (5s)...")
        time.sleep(5)
        
    print("\n✅ Todas las misiones de Oráculo completadas para Prioridad 1.")

if __name__ == "__main__":
    run_oracle_for_featured()
