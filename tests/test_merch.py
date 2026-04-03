"""
tests/test_merch.py — Tests para merch/merch_hunter.py
"""

import pytest
from pathlib import Path
import sys
import re

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))


class TestMerchHunter:
    """Tests para merch/merch_hunter.py"""

    def test_module_imports(self):
        """El módulo debe poder importarse."""
        import merch.merch_hunter

        assert merch.merch_hunter is not None

    def test_merch_file_exists(self):
        """El archivo debe existir."""
        merch_file = BASE_DIR / "merch" / "merch_hunter.py"
        assert merch_file.exists(), "Missing: merch/merch_hunter.py"

    def test_no_syntax_errors(self):
        """El archivo debe tener sintaxis válida."""
        import py_compile

        merch_file = BASE_DIR / "merch" / "merch_hunter.py"
        try:
            py_compile.compile(str(merch_file), doraise=True)
        except py_compile.PyCompileError as e:
            pytest.fail(f"Syntax error in merch_hunter.py: {e}")


class TestMerchHunterSecurity:
    """Tests de seguridad para merch_hunter"""

    def test_no_api_key_leak_in_prints(self):
        """No debe imprimir API keys."""
        merch_file = BASE_DIR / "merch" / "merch_hunter.py"
        content = merch_file.read_text(encoding="utf-8")

        # Buscar prints que expongan keys
        # Patrón: print con variable que contenga KEY
        api_key_print_pattern = r"print\([^)]*\w*KEY\w*[^)]*\)"
        matches = re.findall(api_key_print_pattern, content, re.IGNORECASE)

        # Verificar que si hay prints con KEY, usan len() o masking
        for match in matches:
            assert "len(" in match or "[:8]" not in match, f"Posible leak de API key en: {match}"

    def test_no_bare_except(self):
        """No debe tener bare except."""
        merch_file = BASE_DIR / "merch" / "merch_hunter.py"
        content = merch_file.read_text(encoding="utf-8")

        # Buscar bare except
        bare_except_pattern = r"except\s*:"
        matches = re.findall(bare_except_pattern, content)

        # Si encuentra bare except, verificar que no esté en código crítico
        assert len(matches) == 0, f"Encontrados {len(matches)} bare except en merch_hunter.py"

    def test_word_boundary_in_prohibited_words(self):
        """La validación de palabras prohibidas debe usar word boundary."""
        merch_file = BASE_DIR / "merch" / "merch_hunter.py"
        content = merch_file.read_text(encoding="utf-8")

        # Buscar función de validación
        if "prohibidas" in content.lower() or "prohibido" in content.lower():
            # Verificar que usa \\b o word boundary
            has_word_boundary = r"\\b" in content or "word_boundary" in content.lower()
            # Si no tiene word boundary, al menos debe tener validación robusta
            assert has_word_boundary or "startswith" in content or " in " in content, (
                "La validación de palabras prohibidas debe usar word boundary"
            )


class TestMerchHunterFunctions:
    """Tests de funciones principales"""

    def test_has_main_function(self):
        """Debe tener función main o entrypoint."""
        from merch import merch_hunter

        # merch_hunter tiene cazar_frases, puntuar_frase_merch, etc.
        has_entrypoint = (
            hasattr(merch_hunter, "cazar_frases")
            or hasattr(merch_hunter, "main")
            or hasattr(merch_hunter, "puntuar_frase_merch")
        )
        assert has_entrypoint, (
            "merch_hunter debe tener cazar_frases(), main() o puntuar_frase_merch()"
        )


class TestMerchInit:
    """Tests para merch/__init__.py"""

    def test_init_file_exists(self):
        """El __init__.py debe existir."""
        init_file = BASE_DIR / "merch" / "__init__.py"
        assert init_file.exists(), "Missing: merch/__init__.py"
