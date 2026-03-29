"""
Tests para el Oráculo Híbrido Miura.
Verifica la lógica de orquestación sin llamadas reales a NotebookLM.
"""
import pytest
from unittest.mock import patch, MagicMock
from core.hybrid_oracle import HybridOracle, PROMPT_CONSULTA_DOCTRINAL


class TestHybridOracleInit:
    """Tests de inicialización."""

    def test_init_default(self):
        oracle = HybridOracle()
        assert oracle.mcp_exe is not None
        assert oracle.notebook_cache == {}

    def test_init_custom_path(self):
        oracle = HybridOracle(mcp_exe_path="/custom/path/notebooklm-mcp")
        assert oracle.mcp_exe == "/custom/path/notebooklm-mcp"


class TestInvestigarTema:
    """Tests del flujo de investigación por tema."""

    @patch("core.hybrid_oracle.HybridOracle._consultar_cuaderno")
    @patch("core.hybrid_oracle.HybridOracle._importar_fuentes")
    @patch("core.hybrid_oracle.HybridOracle._esperar_investigacion")
    @patch("core.hybrid_oracle.HybridOracle._iniciar_investigacion")
    @patch("core.hybrid_oracle.HybridOracle._crear_cuaderno")
    def test_investigar_tema_flujo_completo(
        self, mock_crear, mock_iniciar, mock_esperar, mock_importar, mock_consultar
    ):
        mock_crear.return_value = "nb-test-123"
        mock_iniciar.return_value = "task-456"
        mock_esperar.return_value = True
        mock_importar.return_value = 15
        mock_consultar.return_value = "## Reporte de prueba\nDolor: Identidad Perdida"

        oracle = HybridOracle()
        result = oracle.investigar_tema("crisis masculina 2026")

        assert result["exito"] is True
        assert result["notebook_id"] == "nb-test-123"
        assert result["fuentes_importadas"] == 15
        assert "Identidad Perdida" in result["reporte"]
        
        mock_crear.assert_called_once()
        mock_iniciar.assert_called_once()
        mock_esperar.assert_called_once()
        mock_importar.assert_called_once()
        mock_consultar.assert_called_once()

    @patch("core.hybrid_oracle.HybridOracle._crear_cuaderno")
    def test_investigar_tema_fallo_cuaderno(self, mock_crear):
        mock_crear.return_value = None

        oracle = HybridOracle()
        result = oracle.investigar_tema("tema fallido")

        assert result["exito"] is False
        assert result["notebook_id"] is None

    @patch("core.hybrid_oracle.HybridOracle._iniciar_investigacion")
    @patch("core.hybrid_oracle.HybridOracle._crear_cuaderno")
    def test_investigar_tema_fallo_investigacion(self, mock_crear, mock_iniciar):
        mock_crear.return_value = "nb-ok-789"
        mock_iniciar.return_value = None

        oracle = HybridOracle()
        result = oracle.investigar_tema("tema sin research")

        assert result["exito"] is False
        assert result["notebook_id"] == "nb-ok-789"

    @patch("core.hybrid_oracle.HybridOracle._consultar_cuaderno")
    @patch("core.hybrid_oracle.HybridOracle._importar_fuentes")
    @patch("core.hybrid_oracle.HybridOracle._esperar_investigacion")
    @patch("core.hybrid_oracle.HybridOracle._iniciar_investigacion")
    def test_investigar_tema_notebook_existente(
        self, mock_iniciar, mock_esperar, mock_importar, mock_consultar
    ):
        """Verifica que se reutiliza un notebook_id pasado."""
        mock_iniciar.return_value = "task-x"
        mock_esperar.return_value = True
        mock_importar.return_value = 5
        mock_consultar.return_value = "Reporte reutilizado"

        oracle = HybridOracle()
        result = oracle.investigar_tema(
            "tema existente", notebook_id="nb-existente-001"
        )

        assert result["notebook_id"] == "nb-existente-001"
        assert result["exito"] is True


class TestInvestigarLibro:
    """Tests del flujo de investigación para reseñas de libros."""

    @patch("core.hybrid_oracle.HybridOracle._consultar_cuaderno")
    @patch("core.hybrid_oracle.HybridOracle._agregar_url")
    @patch("core.hybrid_oracle.HybridOracle._crear_cuaderno")
    def test_libro_con_urls(self, mock_crear, mock_url, mock_consultar):
        mock_crear.return_value = "nb-libro-001"
        mock_url.return_value = True
        mock_consultar.return_value = "## Briefing: Atomic Habits"

        oracle = HybridOracle()
        result = oracle.investigar_libro(
            "Atomic Habits",
            urls_fuentes=["https://example.com/review1", "https://example.com/review2"]
        )

        assert result["exito"] is True
        assert result["libro"] == "Atomic Habits"
        assert mock_url.call_count == 2

    @patch("core.hybrid_oracle.HybridOracle._consultar_cuaderno")
    @patch("core.hybrid_oracle.HybridOracle._importar_fuentes")
    @patch("core.hybrid_oracle.HybridOracle._esperar_investigacion")
    @patch("core.hybrid_oracle.HybridOracle._iniciar_investigacion")
    @patch("core.hybrid_oracle.HybridOracle._crear_cuaderno")
    def test_libro_sin_urls_autopiloto(
        self, mock_crear, mock_iniciar, mock_esperar, mock_importar, mock_consultar
    ):
        """Sin URLs, el oráculo hace Deep Research automáticamente."""
        mock_crear.return_value = "nb-libro-002"
        mock_iniciar.return_value = "task-libro"
        mock_esperar.return_value = True
        mock_importar.return_value = 8
        mock_consultar.return_value = "## Briefing automático"

        oracle = HybridOracle()
        result = oracle.investigar_libro("El Hombre que Dejó de Mentirse")

        assert result["exito"] is True
        mock_iniciar.assert_called_once()


class TestOracleDoctrinalPrompts:
    """Verifica la integridad de los prompts doctrinales."""

    def test_prompt_contiene_secciones_clave(self):
        assert "DOLORES DETECTADOS" in PROMPT_CONSULTA_DOCTRINAL
        assert "FRASES DE ACERO" in PROMPT_CONSULTA_DOCTRINAL
        assert "GANCHOS DE MARKETING" in PROMPT_CONSULTA_DOCTRINAL
        assert "TENDENCIA DOMINANTE" in PROMPT_CONSULTA_DOCTRINAL
        assert "SOLUCIÓN MIURA" in PROMPT_CONSULTA_DOCTRINAL

    def test_prompt_blog_template(self):
        from core.hybrid_oracle import PROMPT_CONSULTA_BLOG
        assert "{titulo_libro}" in PROMPT_CONSULTA_BLOG
        assert "ANCLA DE VERDAD" in PROMPT_CONSULTA_BLOG
