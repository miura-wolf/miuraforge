import os
import datetime
import re
from core.researcher import Researcher
from core.database import Database
from core.clusterizador import ClusterizadorDolores
from core.tendencias import RadarTendencia
from core.extractor_frases import ExtractorFrases

def run_weekly_oracle():
    print("🔮 [ORÁCULO] Iniciando Sesión de Planificación Semanal Miura...")
    
    researcher = Researcher()
    db = Database()
    
    # 1. Fase de Descubrimiento (Escaneo Táctico de Tendencias)
    tendencias = researcher.detectar_pulso_semanal()
    
    if not tendencias:
        print("❌ [Oráculo] No se pudieron detectar tendencias claras. Abortando misión.")
        return

    print(f"\n📈 Se han detectado {len(tendencias)} corrientes de dolor críticas:")
    for i, t in enumerate(tendencias):
        print(f"【{i+1}】 TEMA: {t['tema']}")
        print(f"    VALOR ESTRATÉGICO: {t['razon']}")
    
    import random
    nombres_epicos = [
        "BIZANCIO", "ROMA", "ESPARTA", "ATENAS", "BABILONIA", "EGIPTO", "FENICIA", "PERSIA", "SUMERIA", "CARTAGO",
        "ALEJANDRO", "LEONIDAS", "CIRO", "DARIO", "JERJES", "RAMSES", "TUTANKAMON", "NABUCODONOSOR", "HAMMURABI",
        "JULIO_CESAR", "AUGUSTO", "TRAJANO", "ADRIANO", "MARCO_AURELIO", "CLAUDIO", "TITO", "VESPASIANO",
        "SULEIMAN", "MEHMET", "SELIM", "OSMAN", "VICINGO", "SAMURAI", "AZTECA", "INCA", "MAYA", "ESTOICO", "ESPARTANO"
    ]
    nombre_base = random.choice(nombres_epicos)
    id_semana = f"{nombre_base}_" + datetime.datetime.now().strftime("%Y%m%d")
    
    # 2. Procesamiento de Temas para Contenido Semanal
    for trend in tendencias:
        try:
            tema = trend['tema']
            query_profunda = trend['query_profunda']
            
            print(f"\n⚔️  Ejecutando Infiltración OSINT para: {tema}...")
            # Usamos buscar_dolor que ya integra validación psicológica
            hallazgos, _ = researcher.buscar_dolor(query_profunda)
            
            if hallazgos:
                # Registrar Hallazgos y Análisis en el Búnker
                db.registrar_hallazgos(id_semana, hallazgos)
                db.registrar_investigacion_psicologica(id_semana, hallazgos, tema=tema)
                
                # 3. Inteligencia Competitiva: Extracción de Ganchos Virales
                # Analizamos las 2 fuentes más potentes encontradas
                print(f"🎯 Extrayendo ganchos tácticos de la competencia para {tema}...")
                for h in hallazgos[:2]:
                    url = h.get('url')
                    ganchos = researcher.extraer_ganchos_virales(url)
                    if ganchos and researcher._es_gancho_del_nicho(ganchos):
                        db.registrar_ganchos_competencia(id_semana, ganchos)
                    elif ganchos:
                        print(f"🚫 [Oracle] Gancho descartado por fuera del nicho: {ganchos.get('titulo_maestro', '')}")
                
                dolor_detectado = hallazgos[0].get('dolor_principal', 'Identidad Perdida')
                db.actualizar_dolor(dolor_detectado)
        except Exception as e:
            print(f"⚠️ [Oráculo] Fallo crítico procesando tendencia '{trend.get('tema')}': {e}. Continuando con la siguiente...")
            continue
            
    # 5. Inteligencia Estratégica (Fase IMP): Generar Clusters y Tendencias
    print("\n📊 [Oráculo] Generando Reporte de Inteligencia Estratégica...")
    clusterizador = ClusterizadorDolores(db)
    radar = RadarTendencia(db)
    extractor = ExtractorFrases(db)
    
    clusterizador.clusterizar_dolores()
    radar.calcular_tendencias()
    extractor.extraer_frases_memorables()
            
    print(f"\n✅ [Oráculo] Misión cumplida. Backlog de 90 días alimentado y Arsenal de Ganchos actualizado.")

if __name__ == "__main__":
    run_weekly_oracle()
