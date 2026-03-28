import json
import re

class ExtractorFrases:
    """Implementa la Directiva 3: Extracción de frases con alta carga emocional."""
    
    def __init__(self, db_manager):
        self.db = db_manager

    def extraer_frases_memorables(self):
        """Busca y registra las frases más potentes en la tabla FRASES_VIRALES."""
        if not self.db.investigacion: return
        
        try:
            records = self.db.investigacion.get_all_records()
            if not records: return

            frases_detectadas = []
            for r in records:
                texto_frases = r.get('FRASES_POTENTES') or ''
                if not texto_frases: continue
                
                partes = [f.strip() for f in texto_frases.split('|') if f.strip()]
                for p in partes:
                    # Filtro de calidad: entre 3 y 15 palabras
                    palabras = p.split()
                    if 3 <= len(palabras) <= 15:
                        frases_detectadas.append({
                            "frase": p,
                            "dolor": r.get('DOLOR_PRINCIPAL') or 'identidad',
                            "tema": r.get('TEMA') or 'N/A',
                            "plataforma": r.get('PLATAFORMA') or 'web'
                        })

            # Sincronizar con Sheets
            ws_frases = self.db.frases
            if not ws_frases:
                print("⚠️ [Extractor] Tabla FRASES_VIRALES no vinculada.")
                return
            
            # Subir solo las nuevas o limpiar y subir todo (por simplicidad, limpiar y subir)
            import datetime
            ahora = str(datetime.datetime.now().strftime("%Y%m%d"))
            
            filas_subir = []
            for i, f in enumerate(frases_detectadas[:50]): # Top 50 frases
                id_frase = f"FR_{ahora}_{i}"
                filas_subir.append([id_frase, f["frase"], f["dolor"], f["plataforma"], f["tema"]])

            if filas_subir:
                ws_frases.clear()
                headers = ["id_frase", "frase", "dolor_asociado", "plataforma", "tema"]
                ws_frases.update('A1', [headers])
                ws_frases.append_rows(filas_subir)
                print(f"🎙️ [Extractor] {len(filas_subir)} frases virales registradas en el Arsenal.")

        except Exception as e:
            print(f"⚠️ [Extractor] Error capturando frases: {e}")
