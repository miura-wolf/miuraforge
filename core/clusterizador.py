import json
from collections import Counter

class ClusterizadorDolores:
    """Implementa la Directiva 1: Agrupación de insights para detectar patrones de dolor."""
    
    def __init__(self, db_manager):
        self.db = db_manager

    def clusterizar_dolores(self):
        """Analiza INVESTIGACION_PSICOLOGICA y genera clusters en la tabla CLUSTERS_DOLOR."""
        if not self.db.investigacion: return []
        
        try:
            records = self.db.investigacion.get_all_records()
            if not records: return []

            # Agrupar por DOLOR_PRINCIPAL (Categoría)
            clusters = {}
            for r in records:
                categoria = (r.get('DOLOR_PRINCIPAL') or 'desconocido').strip().lower()
                if not categoria: continue
                
                if categoria not in clusters:
                    clusters[categoria] = {
                        "frecuencia": 0,
                        "frases": [],
                        "temas": set()
                    }
                
                clusters[categoria]["frecuencia"] += 1
                clusters[categoria]["temas"].add(r.get('TEMA', 'N/A'))
                # Capturamos frases potentes (limitado para no saturar)
                frases = [f.strip() for f in str(r.get('FRASES_POTENTES', '')).split('|') if f.strip()]
                clusters[categoria]["frases"].extend(frases[:2])

            # Preparar filas para la tabla CLUSTERS_DOLOR
            # Estructura: cluster_id, nombre_cluster, frecuencia, temas_relacionados, frase_dominante, ultima_actualizacion, freq_7d, freq_30d, tendencia
            import datetime
            ahora = datetime.datetime.now()
            ahora_str = ahora.strftime("%Y-%m-%d %H:%M")
            hace_7d = ahora - datetime.timedelta(days=7)
            hace_30d = ahora - datetime.timedelta(days=30)
            
            headers = ["cluster_id", "nombre_cluster", "frecuencia", "temas_relacionados", "frase_dominante", "ultima_actualizacion", "freq_7d", "freq_30d", "tendencia_estado"]
            filas_novedad = []

            for nombre, data in clusters.items():
                frase_top = Counter(data["frases"]).most_common(1)[0][0] if data["frases"] else "N/A"
                temas_str = ", ".join(list(data["temas"])[:3])
                
                # Cálculo de frecuencias temporales (con protección contra datos corruptos)
                freq_7d = 0
                for r in records:
                    if str(r.get('DOLOR_PRINCIPAL','')).strip().lower() == nombre and r.get('FECHA'):
                        try:
                            if datetime.datetime.strptime(str(r['FECHA'])[:16], "%Y-%m-%d %H:%M") >= hace_7d:
                                freq_7d += 1
                        except: continue

                freq_30d = 0
                for r in records:
                    if str(r.get('DOLOR_PRINCIPAL','')).strip().lower() == nombre and r.get('FECHA'):
                        try:
                            if datetime.datetime.strptime(str(r['FECHA'])[:16], "%Y-%m-%d %H:%M") >= hace_30d:
                                freq_30d += 1
                        except: continue

                ratio = round(freq_7d / freq_30d, 1) if freq_30d > 0 else freq_7d
                tendencia = f"🔥 EMERGENTE ({ratio})" if ratio >= 3 else \
                            f"📈 CRECIENDO ({ratio})" if ratio >= 1.5 else \
                            f"➡️ ESTABLE ({ratio})"

                fila = [
                    f"CLUSTER_{nombre.upper()[:10]}",
                    nombre.upper(),
                    data["frecuencia"],
                    temas_str,
                    frase_top,
                    ahora_str,
                    freq_7d,
                    freq_30d,
                    tendencia
                ]
                filas_novedad.append(fila)

            # Sincronizar con Sheets
            ws_clusters = self.db.clusters
            if not ws_clusters:
                print("⚠️ [Clusterizador] Tabla CLUSTERS_DOLOR no vinculada en Database.")
                return
            
            # Limpiar contenido previo (excepto headers) y subir nuevo
            if len(filas_novedad) > 0:
                ws_clusters.clear()
                ws_clusters.update('A1', [headers])
                ws_clusters.append_rows(filas_novedad)
                print(f"📊 [Clusterizador] {len(filas_novedad)} núcleos de dolor detectados y sincronizados.")
            
            return clusters
        except Exception as e:
            print(f"⚠️ [Clusterizador] Error en proceso: {e}")
            return []
