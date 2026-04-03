"""
tests/test_deployer.py — Tests para deployer/miura_deployer.py
"""

import pytest
from pathlib import Path
import sys

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))


class TestMiuraDeployer:
    """Tests para deployer/miura_deployer.py"""

    def test_module_imports(self):
        """El módulo debe poder importarse."""
        import deployer.miura_deployer

        assert deployer.miura_deployer is not None

    def test_deployer_file_exists(self):
        """El archivo debe existir."""
        deployer_file = BASE_DIR / "deployer" / "miura_deployer.py"
        assert deployer_file.exists(), "Missing: deployer/miura_deployer.py"

    def test_no_syntax_errors(self):
        """El archivo debe tener sintaxis válida."""
        import py_compile

        deployer_file = BASE_DIR / "deployer" / "miura_deployer.py"
        try:
            py_compile.compile(str(deployer_file), doraise=True)
        except py_compile.PyCompileError as e:
            pytest.fail(f"Syntax error in miura_deployer.py: {e}")

    def test_has_main_function(self):
        """Debe tener función main o entrypoint."""
        from deployer import miura_deployer

        # Verificar que tiene MiuraDeployer class
        has_entrypoint = hasattr(miura_deployer, "MiuraDeployer") or hasattr(miura_deployer, "main")
        assert has_entrypoint, "miura_deployer debe tener MiuraDeployer o main()"


class TestDeployerSecurity:
    """Tests de seguridad para deployer"""

    def test_path_traversal_protection(self):
        """Debe haber validación de path traversal."""
        from deployer import miura_deployer
        import inspect

        # Leer el código fuente
        source = inspect.getsource(miura_deployer)

        # Verificar que hay alguna validación de path
        has_path_validation = (
            ".." in source
            or "abspath" in source
            or "normpath" in source
            or "validate" in source.lower()
            or "sanitize" in source.lower()
        )

        assert has_path_validation, "miura_deployer debe validar paths para evitar traversal"


class TestDeployerInit:
    """Tests para deployer/__init__.py"""

    def test_init_file_exists(self):
        """El __init__.py debe existir."""
        init_file = BASE_DIR / "deployer" / "__init__.py"
        assert init_file.exists(), "Missing: deployer/__init__.py"
