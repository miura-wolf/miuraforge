"""
schemas.py — Fuente única de verdad para la estructura del Puente de Mando (Google Sheets).
Importar MAPEO_MAESTRO desde aquí en lugar de definirlo inline en cada módulo.
"""

MAPEO_MAESTRO = {
    "LOGISTICA": ["ID_Sesion", "Tema", "Fecha", "Estado", "Metricas"],
    "PRODUCCION": [
        "ID_Sesion",
        "Fase",
        "Guion",
        "Prompt_Visual",
        "Voz_Status",
        "Estado",
    ],
    "MEMORIA": ["Metafora"],
    "AUDITORIA": [
        "ID_Master",
        "Guion_Original",
        "Guion_Optimizado",
        "Intensidad",
        "Ritmo",
        "Coherencia",
        "ADN",
        "Fallas",
        "Ajustes",
        "Fecha",
    ],
    "FUENTES": [
        "ID",
        "ID_SESION",
        "PLATAFORMA",
        "ORIGEN",
        "URL",
        "AUTOR",
        "ENGAGEMENT",
        "FECHA",
        "QUERY",
        "FECHA_EXTRACCION",
    ],
    "INVESTIGACION_PSICOLOGICA": [
        "ID_SEMANA",
        "TEMA",
        "DOLOR_PRINCIPAL",
        "PROBLEMA_RAIZ",
        "FRASES_POTENTES",
        "CREENCIAS",
        "SOLUCION_MIURA",
        "PLATAFORMA",
        "FECHA",
        "ARQUETIPO_SUGERIDO",
    ],
    "DOLORES_MASCULINOS": [
        "ID_DOLOR",
        "CATEGORIA",
        "DESCRIPCION",
        "CREENCIAS",
        "VERDAD",
        "INTENSIDAD",
        "FRECUENCIA",
        "EJEMPLO",
    ],
    "ARSENAL_GANCHOS": [
        "GANCHO",
        "PLANTILLA",
        "INTENSIDAD",
        "ID_SESION",
        "FECHA",
    ],
    "CLUSTERS_DOLOR": [
        "cluster_id",
        "nombre_cluster",
        "frecuencia",
        "temas_relacionados",
        "frase_dominante",
        "ultima_actualizacion",
        "freq_7d",
        "freq_30d",
        "tendencia_estado",
    ],
    "FRASES_VIRALES": [
        "id_frase",
        "frase",
        "dolor_asociado",
        "plataforma",
        "tema",
    ],
    "BLOG_CONTENIDO": [
        "ID",
        "Estado",
        "Título",
        "Slug",
        "Fecha",
        "Descripción",
        "Keywords",
        "Categoría",
        "Imagen_URL",
        "Enlace_Afiliado",
        "Cuerpo_Raw",
        "Tags",
        "ReadTime_Min",
        "Featured",
        "ANCLA_VERDAD",
        "LIBRO_ESTADO",
    ],
}

# Subset usado por herramientas de inspección/alineación (sin tablas auxiliares)
MAPEO_INSPECCION = {
    k: v
    for k, v in MAPEO_MAESTRO.items()
    if k
    in (
        "LOGISTICA",
        "PRODUCCION",
        "MEMORIA",
        "AUDITORIA",
        "FUENTES",
        "INVESTIGACION_PSICOLOGICA",
        "DOLORES_MASCULINOS",
        "ARSENAL_GANCHOS",
    )
}
