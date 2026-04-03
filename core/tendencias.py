import datetime


def col_letter(n):
    """Convierte número de columna a letra de Excel (1=A, 27=AA, etc)."""
    result = ""
    while n > 0:
        n, remainder = divmod(n - 1, 26)
        result = chr(65 + remainder) + result
    return result


class RadarTendencia:
    """Implementa la Directiva 2: Detección de dolores emergentes.

    NOTA: El cálculo de freq_7d/freq_30d ahora lo hace ClusterizadorDolores
    en un single-pass. Este módulo solo se encarga de LEER los clusters
    ya calculados y actualizar el estado de tendencia con batch update.
    """

    def __init__(self, db_manager):
        self.db = db_manager

    def calcular_tendencias(self):
        """Lee clusters y actualiza tendencias con batch update."""
        ws_clusters = self.db.clusters
        if not ws_clusters:
            print("⚠️ [Radar] Tabla CLUSTERS_DOLOR no vinculada.")
            return

        try:
            clusters_data = ws_clusters.get_all_records()
            if not clusters_data:
                return

            headers = [h.lower() for h in ws_clusters.row_values(1)]
            try:
                idx_tendencia = headers.index("tendencia_estado") + 1
            except ValueError:
                print("⚠️ [Radar] Columna tendencia_estado no encontrada.")
                return

            # Batch update: recolectar todos los cambios y aplicar de una vez
            updates = []
            for i, cluster in enumerate(clusters_data):
                f7 = int(cluster.get("freq_7d", 0) or 0)
                f30 = int(cluster.get("freq_30d", 0) or 0)

                # Fórmula y thresholds consistentes con clusterizador
                ratio = f7 / (f30 / 4) if f30 > 0 else float(f7)

                if ratio >= 3:
                    estado = f"🔥 EMERGENTE ({ratio:.1f})"
                elif ratio >= 1.5:
                    estado = f"📈 CRECIENDO ({ratio:.1f})"
                else:
                    estado = f"➡️ ESTABLE ({ratio:.1f})"

                row_idx = i + 2
                updates.append(
                    {"range": f"{chr(64 + idx_tendencia)}{row_idx}", "values": [[estado]]}
                )

            # Batch update en vez de celda por celda
            if updates:
                ws_clusters.batch_update(updates)

            print("📈 [Radar] Tendencias calculadas y proyectadas en el Búnker.")
        except Exception as e:
            print(f"⚠️ [Radar] Error calculando tendencias: {e}")
