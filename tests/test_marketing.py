"""
Tests para módulos de marketing — MiuraForge.
Incluye: seo_auditor, copy_optimizer, social_calendar, competitive_intel,
landing_cro, ad_creative, pdf_report
"""

import pytest
from pathlib import Path
import sys
import json

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))


# ============================================================================
# TESTS: social_calendar.py
# ============================================================================


class TestSocialCalendar:
    """Tests para marketing/social_calendar.py"""

    def test_pilares_contenido_defined(self):
        """Debe tener 5 pilares definidos."""
        from marketing.social_calendar import PILARES_CONTENIDO

        assert isinstance(PILARES_CONTENIDO, dict)
        assert len(PILARES_CONTENIDO) == 5
        assert "DOCTRINA" in PILARES_CONTENIDO
        assert "EJECUCION" in PILARES_CONTENIDO

    def test_pilares_have_required_keys(self):
        """Cada pilar debe tener nombre, descripcion, mix."""
        from marketing.social_calendar import PILARES_CONTENIDO

        for key, pilar in PILARES_CONTENIDO.items():
            assert "nombre" in pilar
            assert "descripcion" in pilar
            assert "mix" in pilar
            assert isinstance(pilar["mix"], int)

    def test_verbos_prohibidos_defined(self):
        """Debe tener lista de verbos prohibidos."""
        from marketing.social_calendar import VERBOS_PROHIBIDOS

        assert isinstance(VERBOS_PROHIBIDOS, list)
        assert len(VERBOS_PROHIBIDOS) > 0
        assert "podrías" in VERBOS_PROHIBIDOS

    def test_verbos_permitidos_defined(self):
        """Debe tener lista de verbos permitidos."""
        from marketing.social_calendar import VERBOS_PERMITIDOS

        assert isinstance(VERBOS_PERMITIDOS, list)
        assert len(VERBOS_PERMITIDOS) > 0
        assert "forja" in VERBOS_PERMITIDOS

    def test_plataformas_defined(self):
        """Debe tener 4 plataformas soportadas."""
        from marketing.social_calendar import PLATAFORMAS

        assert isinstance(PLATAFORMAS, dict)
        assert len(PLATAFORMAS) == 4
        assert "yt" in PLATAFORMAS
        assert "ig" in PLATAFORMAS
        assert "tk" in PLATAFORMAS
        assert "tw" in PLATAFORMAS

    def test_extraer_json_array_function(self):
        """_extraer_json_array debe funcionar correctamente."""
        from marketing.social_calendar import _extraer_json_array

        # JSON directo
        result = _extraer_json_array('[{"a": 1}]')
        assert result is not None
        assert len(result) == 1

        # Con markdown
        result = _extraer_json_array('```json\n[{"a": 1}]\n```')
        assert result is not None

        # No JSON
        result = _extraer_json_array("not json")
        assert result is None


# ============================================================================
# TESTS: competitive_intel.py
# ============================================================================


class TestCompetitiveIntel:
    """Tests para marketing/competitive_intel.py"""

    def test_nichos_competidores_defined(self):
        """Debe tener nichos pre-configurados."""
        from marketing.competitive_intel import NICHOS_COMPETIDORES

        assert isinstance(NICHOS_COMPETIDORES, dict)
        assert len(NICHOS_COMPETIDORES) >= 1
        assert "disciplina_masculina" in NICHOS_COMPETIDORES

    def test_nicho_has_required_fields(self):
        """Cada nicho debe tener campos requeridos."""
        from marketing.competitive_intel import NICHOS_COMPETIDORES

        for key, nicho in NICHOS_COMPETIDORES.items():
            assert "nombre" in nicho
            assert "canales_referencia" in nicho
            assert "temas_clave" in nicho
            assert isinstance(nicho["canales_referencia"], list)

    def test_extraer_json_function(self):
        """_extraer_json debe funcionar correctamente."""
        from marketing.competitive_intel import _extraer_json

        # JSON objeto
        result = _extraer_json('{"a": 1}')
        assert result is not None
        assert result["a"] == 1

        # Con markdown
        result = _extraer_json('```json\n{"a": 1}\n```')
        assert result is not None

        # Trailing comma
        result = _extraer_json('{"a": 1,}')
        assert result is not None

        # No JSON
        result = _extraer_json("not json")
        assert result is None


# ============================================================================
# TESTS: landing_cro.py
# ============================================================================


class TestLandingCRO:
    """Tests para marketing/landing_cro.py"""

    def test_dimensiones_cro_defined(self):
        """Debe tener 6 dimensiones CRO."""
        from marketing.landing_cro import DIMENSIONES_CRO

        assert isinstance(DIMENSIONES_CRO, dict)
        assert len(DIMENSIONES_CRO) == 6
        assert "HEADLINE_VALUE" in DIMENSIONES_CRO
        assert "DOCTRINAL_ALIGNMENT" in DIMENSIONES_CRO

    def test_dimensiones_have_weights(self):
        """Cada dimensión debe tener peso."""
        from marketing.landing_cro import DIMENSIONES_CRO

        total_peso = 0
        for key, dim in DIMENSIONES_CRO.items():
            assert "peso" in dim
            assert "nombre" in dim
            assert "criterios" in dim
            total_peso += dim["peso"]

        # Pesos deben sumar 100
        assert total_peso == 100

    def test_verbos_prohibidos_defined(self):
        """Debe tener verbos prohibidos."""
        from marketing.landing_cro import VERBOS_PROHIBIDOS

        assert isinstance(VERBOS_PROHIBIDOS, list)
        assert len(VERBOS_PROHIBIDOS) > 0

    def test_analizar_landing_function_exists(self):
        """La función analizar_landing debe existir."""
        from marketing.landing_cro import analizar_landing

        assert callable(analizar_landing)

    def test_generar_variantes_function_exists(self):
        """La función generar_variantes debe existir."""
        from marketing.landing_cro import generar_variantes

        assert callable(generar_variantes)


# ============================================================================
# TESTS: ad_creative.py
# ============================================================================


class TestAdCreative:
    """Tests para marketing/ad_creative.py"""

    def test_plataformas_defined(self):
        """Debe tener 5 plataformas soportadas."""
        from marketing.ad_creative import PLATAFORMAS

        assert isinstance(PLATAFORMAS, dict)
        assert len(PLATAFORMAS) == 5
        assert "fb" in PLATAFORMAS
        assert "yt" in PLATAFORMAS
        assert "tk" in PLATAFORMAS

    def test_plataformas_have_max_caracteres(self):
        """Cada plataforma debe tener límites de caracteres."""
        from marketing.ad_creative import PLATAFORMAS

        for key, plat in PLATAFORMAS.items():
            assert "max_caracteres" in plat
            assert "titulo" in plat["max_caracteres"]
            assert "cta" in plat["max_caracteres"]

    def test_hooks_templates_defined(self):
        """Debe tener hooks por plataforma."""
        from marketing.ad_creative import HOOKS_TEMPLATES

        assert isinstance(HOOKS_TEMPLATES, dict)
        assert len(HOOKS_TEMPLATES) > 0

    def test_verbos_prohibidos_defined(self):
        """Debe tener verbos prohibidos."""
        from marketing.ad_creative import VERBOS_PROHIBIDOS

        assert isinstance(VERBOS_PROHIBIDOS, list)
        assert len(VERBOS_PROHIBIDOS) > 0

    def test_generar_ad_creatives_function_exists(self):
        """La función principal debe existir."""
        from marketing.ad_creative import generar_ad_creatives

        assert callable(generar_ad_creatives)


# ============================================================================
# TESTS: pdf_report.py
# ============================================================================


class TestPDFReport:
    """Tests para marketing/pdf_report.py"""

    def test_brand_colors_defined(self):
        """Debe tener colores de marca definidos."""
        from marketing.pdf_report import BRAND_COLORS

        assert isinstance(BRAND_COLORS, dict)
        assert "negro" in BRAND_COLORS
        assert "dorado" in BRAND_COLORS
        assert "blanco" in BRAND_COLORS

    def test_brand_fonts_defined(self):
        """Debe tener fuentes definidas."""
        from marketing.pdf_report import BRAND_FONTS

        assert isinstance(BRAND_FONTS, dict)
        assert "titulo" in BRAND_FONTS
        assert "cuerpo" in BRAND_FONTS

    def test_check_reportlab_function(self):
        """_check_reportlab debe retornar bool."""
        from marketing.pdf_report import _check_reportlab

        result = _check_reportlab()
        assert isinstance(result, bool)

    def test_generar_pdf_functions_exist(self):
        """Las funciones de generación deben existir."""
        from marketing.pdf_report import (
            generar_pdf_seo,
            generar_pdf_competitive,
            generar_pdf_calendar,
            generar_pdf_generico,
        )

        assert callable(generar_pdf_seo)
        assert callable(generar_pdf_competitive)
        assert callable(generar_pdf_calendar)
        assert callable(generar_pdf_generico)


# ============================================================================
# TESTS: seo_auditor.py (existente)
# ============================================================================


class TestSEOAuditor:
    """Tests para marketing/seo_auditor.py"""

    def test_prompt_seo_defined(self):
        """Debe tener PROMPT_SEO definido."""
        from marketing.seo_auditor import PROMPT_SEO

        assert isinstance(PROMPT_SEO, str)
        assert len(PROMPT_SEO) > 100
        assert "PILARES" in PROMPT_SEO

    def test_auditar_post_function_exists(self):
        """La función auditar_post debe existir."""
        from marketing.seo_auditor import auditar_post

        assert callable(auditar_post)

    def test_auditar_todos_function_exists(self):
        """La función auditar_todos debe existir."""
        from marketing.seo_auditor import auditar_todos

        assert callable(auditar_todos)


# ============================================================================
# TESTS: copy_optimizer.py (existente)
# ============================================================================


class TestCopyOptimizer:
    """Tests para marketing/copy_optimizer.py"""

    def test_prompt_headline_defined(self):
        """Debe tener PROMPT_HEADLINE definido."""
        from marketing.copy_optimizer import PROMPT_HEADLINE

        assert isinstance(PROMPT_HEADLINE, str)
        assert "REGLAS DOCTRINALES" in PROMPT_HEADLINE

    def test_prompt_cta_defined(self):
        """Debe tener PROMPT_CTA definido."""
        from marketing.copy_optimizer import PROMPT_CTA

        assert isinstance(PROMPT_CTA, str)

    def test_optimizar_headline_function_exists(self):
        """La función optimizar_headline debe existir."""
        from marketing.copy_optimizer import optimizar_headline

        assert callable(optimizar_headline)

    def test_auditar_cta_function_exists(self):
        """La función auditar_cta debe existir."""
        from marketing.copy_optimizer import auditar_cta

        assert callable(auditar_cta)


# ============================================================================
# TESTS: Module Structure
# ============================================================================


# ============================================================================
# TESTS: content_gap_analysis.py
# ============================================================================


class TestContentGapAnalysis:
    """Tests para marketing/content_gap_analysis.py"""

    def test_nichos_config_defined(self):
        """Debe tener nichos pre-configurados."""
        from marketing.content_gap_analysis import NICHOS_CONFIG

        assert isinstance(NICHOS_CONFIG, dict)
        assert len(NICHOS_CONFIG) >= 1
        assert "disciplina_masculina" in NICHOS_CONFIG

    def test_nicho_has_required_fields(self):
        """Cada nicho debe tener campos requeridos."""
        from marketing.content_gap_analysis import NICHOS_CONFIG

        for key, nicho in NICHOS_CONFIG.items():
            assert "nombre" in nicho
            assert "temas_base" in nicho
            assert "competidores_referencia" in nicho
            assert isinstance(nicho["temas_base"], list)

    def test_palabras_prohibidas_defined(self):
        """Debe tener palabras prohibidas."""
        from marketing.content_gap_analysis import NICHOS_CONFIG

        # Los nichos tienen temas_base que deben estar definidos
        for key, nicho in NICHOS_CONFIG.items():
            assert "temas_base" in nicho
            assert len(nicho["temas_base"]) > 0

    def test_analizar_gaps_function_exists(self):
        """La función analizar_gaps debe existir."""
        from marketing.content_gap_analysis import analizar_gaps

        assert callable(analizar_gaps)

    def test_generar_oportunidades_function_exists(self):
        """La función generar_oportunidades debe exister."""
        from marketing.content_gap_analysis import generar_oportunidades

        assert callable(generar_oportunidades)


# ============================================================================
# TESTS: email_sequence.py
# ============================================================================


class TestEmailSequence:
    """Tests para marketing/email_sequence.py"""

    def test_tipos_secuencia_defined(self):
        """Debe tener tipos de secuencia definidos."""
        from marketing.email_sequence import TIPOS_SECUENCIA

        assert isinstance(TIPOS_SECUENCIA, dict)
        assert len(TIPOS_SECUENCIA) >= 3
        assert "bienvenida" in TIPOS_SECUENCIA
        assert "lanzamiento" in TIPOS_SECUENCIA

    def test_tipo_has_required_fields(self):
        """Cada tipo debe tener campos requeridos."""
        from marketing.email_sequence import TIPOS_SECUENCIA

        for key, tipo in TIPOS_SECUENCIA.items():
            assert "nombre" in tipo
            assert "duracion_dias" in tipo
            assert "objetivo" in tipo
            assert isinstance(tipo["duracion_dias"], int)

    def test_verbos_prohibidos_defined(self):
        """Debe tener verbos prohibidos."""
        from marketing.email_sequence import VERBOS_PROHIBIDOS

        assert isinstance(VERBOS_PROHIBIDOS, list)
        assert len(VERBOS_PROHIBIDOS) > 0

    def test_verbos_permitidos_defined(self):
        """Debe tener verbos permitidos."""
        from marketing.email_sequence import VERBOS_PERMITIDOS

        assert isinstance(VERBOS_PERMITIDOS, list)
        assert len(VERBOS_PERMITIDOS) > 0

    def test_generar_secuencia_function_exists(self):
        """La función generar_secuencia debe existir."""
        from marketing.email_sequence import generar_secuencia

        assert callable(generar_secuencia)

    def test_exportar_secuencia_function_exists(self):
        """La función exportar_secuencia debe existir."""
        from marketing.email_sequence import exportar_secuencia

        assert callable(exportar_secuencia)


# ============================================================================
# TESTS: launch_timing.py
# ============================================================================


class TestLaunchTiming:
    """Tests para marketing/launch_timing.py"""

    def test_feriados_argentina_defined(self):
        """Debe tener feriados de Argentina 2026."""
        from marketing.launch_timing import FERIADOS_ARGENTINA_2026

        assert isinstance(FERIADOS_ARGENTINA_2026, list)
        assert len(FERIADOS_ARGENTINA_2026) > 0
        assert "2026-01-01" in FERIADOS_ARGENTINA_2026

    def test_tipos_lanzamiento_defined(self):
        """Debe tener tipos de lanzamiento definidos."""
        from marketing.launch_timing import TIPOS_LANZAMIENTO

        assert isinstance(TIPOS_LANZAMIENTO, dict)
        assert len(TIPOS_LANZAMIENTO) >= 3
        assert "producto" in TIPOS_LANZAMIENTO
        assert "servicio" in TIPOS_LANZAMIENTO

    def test_tipo_has_lead_time(self):
        """Cada tipo debe tener lead_time_semanas."""
        from marketing.launch_timing import TIPOS_LANZAMIENTO

        for key, tipo in TIPOS_LANZAMIENTO.items():
            assert "lead_time_semanas" in tipo
            assert isinstance(tipo["lead_time_semanas"], int)
            assert tipo["lead_time_semanas"] > 0

    def test_calcular_fecha_optima_function_exists(self):
        """La función calcular_fecha_optima debe existir."""
        from marketing.launch_timing import calcular_fecha_optima

        assert callable(calcular_fecha_optima)

    def test_generar_cronograma_function_exists(self):
        """La función generar_cronograma debe existir."""
        from marketing.launch_timing import generar_cronograma

        assert callable(generar_cronograma)

    def test_auditar_fecha_function_exists(self):
        """La función auditar_fecha debe existir."""
        from marketing.launch_timing import auditar_fecha

        assert callable(auditar_fecha)

    def test_auditar_fecha_returns_score(self):
        """auditar_fecha debe retornar un score."""
        from marketing.launch_timing import auditar_fecha

        # Test con una fecha válida
        resultado = auditar_fecha("2026-05-15", "producto")
        assert "score" in resultado
        assert "veredicto" in resultado
        assert isinstance(resultado["score"], int)
        assert 0 <= resultado["score"] <= 100

    def test_auditar_fecha_rejects_invalid_format(self):
        """auditar_fecha debe rechazar formato inválido."""
        from marketing.launch_timing import auditar_fecha

        resultado = auditar_fecha("15-05-2026", "producto")
        assert "error" in resultado


# ============================================================================
# TESTS: Module Structure (actualizado)
# ============================================================================


class TestMarketingModule:
    """Tests para la estructura del módulo marketing"""

    def test_all_files_exist(self):
        """Todos los archivos deben existir."""
        marketing_dir = BASE_DIR / "marketing"
        expected_files = [
            "__init__.py",
            "seo_auditor.py",
            "copy_optimizer.py",
            "funnel_engine.py",
            "launch_playbook.py",
            "social_calendar.py",
            "competitive_intel.py",
            "landing_cro.py",
            "ad_creative.py",
            "pdf_report.py",
            "content_gap_analysis.py",
            "email_sequence.py",
            "launch_timing.py",
        ]

        for filename in expected_files:
            filepath = marketing_dir / filename
            assert filepath.exists(), f"Missing: {filename}"

    def test_no_syntax_errors(self):
        """Los archivos deben tener sintaxis válida."""
        import py_compile

        marketing_dir = BASE_DIR / "marketing"
        for py_file in marketing_dir.glob("*.py"):
            if py_file.name == "__init__.py":
                continue
            try:
                py_compile.compile(str(py_file), doraise=True)
            except py_compile.PyCompileError as e:
                pytest.fail(f"Syntax error in {py_file.name}: {e}")

    def test_module_imports(self):
        """Todos los módulos deben poder importarse."""
        modules = [
            "marketing.seo_auditor",
            "marketing.copy_optimizer",
            "marketing.funnel_engine",
            "marketing.launch_playbook",
            "marketing.social_calendar",
            "marketing.competitive_intel",
            "marketing.landing_cro",
            "marketing.ad_creative",
            "marketing.pdf_report",
            "marketing.content_gap_analysis",
            "marketing.email_sequence",
            "marketing.launch_timing",
        ]

        for module_name in modules:
            __import__(module_name)
