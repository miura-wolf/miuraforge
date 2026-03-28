import datetime

class RadarTendencia:
    """Implementa la Directiva 2: Detección de dolores emergentes (Ratio 7d/30d)."""
    
    def __init__(self, db_manager):
        self.db = db_manager

    def calcular_tendencias(self):
        """Calcula el ratio de tendencia basado en la frecuencia de menciones temporales."""
        if not self.db.investigacion: return
        
        try:
            records = self.db.investigacion.get_all_records()
            if not records: return

            ahora = datetime.datetime.now()
            hace_7d = ahora - datetime.timedelta(days=7)
            hace_30d = ahora - datetime.timedelta(days=30)

            metricas_dolor = {} # {nombre_dolor: {7d: 0, 30d: 0}}

            for r in records:
                dolor = (r.get('DOLOR_PRINCIPAL') or 'desconocido').strip().upper()
                fecha_str = r.get('FECHA') or ''
                try:
                    fecha_obj = datetime.datetime.strptime(fecha_str, "%Y-%m-%d %H:%M")
                except:
                    continue

                if dolor not in metricas_dolor:
                    metricas_dolor[dolor] = {"7d": 0, "30d": 0}

                if fecha_obj >= hace_7d:
                    metricas_dolor[dolor]["7d"] += 1
                if fecha_obj >= hace_30d:
                    metricas_dolor[dolor]["30d"] += 1

            # Actualizar la tabla CLUSTERS_DOLOR con la tendencia
            ws_clusters = self.db.clusters
            if not ws_clusters:
                print("⚠️ [Radar] Tabla CLUSTERS_DOLOR no vinculada.")
                return
            clusters_data = ws_clusters.get_all_records()
            
            updates = [] # Lista de diccionarios para actualizar (más lento pero más seguro por fila)
            # Nota: Para mayor eficiencia, se podría mapear todo y subir en un bloque
            
            headers = [h.lower() for h in ws_clusters.row_values(1)]
            try:
                idx_f7 = headers.index("freq_7d") + 1
                idx_f30 = headers.index("freq_30d") + 1
                idx_tendencia = headers.index("tendencia_estado") + 1
            except ValueError:
                print("⚠️ [Radar] Columnas de tendencia no encontradas. El Escudo debería restaurarlas.")
                return

            for i, cluster in enumerate(clusters_data):
                nombre = cluster.get('nombre_cluster', '').strip().upper()
                stats = metricas_dolor.get(nombre, {"7d": 0, "30d": 0})
                
                f7 = stats["7d"]
                f30 = stats["30d"]
                
                # Ratio de tendencia (Fórmula Directiva 2)
                ratio = f7 / (f30 / 4) if f30 > 0 else 0 # Normalizado a 4 semanas
                
                estado = "ESTABLE"
                if ratio > 1.5: estado = "🔥 EMERGENTE"
                elif ratio < 0.5: estado = "❄️ DECRECIENDO"
                
                # Actualizar columnas dinámicamente según índices
                row_idx = i + 2
                ws_clusters.update_cell(row_idx, idx_f7, f7)
                ws_clusters.update_cell(row_idx, idx_f30, f30)
                ws_clusters.update_cell(row_idx, idx_tendencia, f"{estado} ({ratio:.1f})")

            print("📈 [Radar] Tendencias calculadas y proyectadas en el Búnker.")
        except Exception as e:
            print(f"⚠️ [Radar] Error calculando tendencias: {e}")
