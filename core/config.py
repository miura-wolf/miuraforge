"""
config.py — MiuraForgeEngine
===========================
Módulo central de configuración y gestión de rutas de credenciales.

Este módulo centraliza el acceso a archivos sensibles, asegurando que
las credenciales se lean desde el directorio seguro ~/.miura_forge/
en lugar de la raíz del repositorio.

Uso:
    from core.config import CREDENTIALS_PATH, META_STATE_PATH

    # Leer credenciales de Google
    creds = ServiceAccountCredentials.from_json_keyfile_name(
        CREDENTIALS_PATH, scope
    )

    # Leer estado de Meta AI
    with open(META_STATE_PATH, 'r') as f:
        state = json.load(f)
"""

import os
from pathlib import Path
from typing import Optional


def get_secrets_dir() -> Path:
    """
    Obtiene el directorio seguro para credenciales.

    El orden de prioridad es:
    1. Variable de entorno MIURA_FORGE_SECRETS
    2. ~/.miura_forge/ (directorio home del usuario, e.g., C:\\Users\\carja\\.miura_forge)
    3. C:\\Users\\carja\\.miura_forge (Hardcoded para Windows como ultra-seguridad)
    4. Directorio raíz del proyecto (fallback legacy)
    """
    # 1. Variable de entorno (más prioridad)
    env_path = os.getenv("MIURA_FORGE_SECRETS")
    if env_path:
        p = Path(env_path).expanduser().resolve()
        if p.exists():
            return p

    # 2. Directorio seguro en home (Dinámico)
    home_secrets = Path.home() / ".miura_forge"
    if home_secrets.exists():
        return home_secrets

    # 3. Ruta explícita solicitada por el usuario (Windows)
    if os.name == 'nt':
        explicit_path = Path("C:/Users/carja/.miura_forge")
        if explicit_path.exists():
            return explicit_path

    # 4. Fallback: raíz del proyecto (para compatibilidad)
    # Detectar raíz del proyecto
    current = Path(__file__).resolve().parent.parent
    return current



def ensure_secrets_dir() -> Path:
    """
    Asegura que el directorio de credenciales existe.
    Lo crea si no existe.

    Returns:
        Path al directorio de credenciales (creado si era necesario)
    """
    secrets_dir = Path.home() / ".miura_forge"
    secrets_dir.mkdir(parents=True, exist_ok=True)

    # Crear archivo .gitignore para asegurar que nunca se suba
    gitignore = secrets_dir / ".gitignore"
    if not gitignore.exists():
        gitignore.write_text("*\n!.gitignore\n")

    return secrets_dir


# ============================================================================
# RUTAS DE CREDENCIALES
# ============================================================================

# Directorio base de credenciales
SECRETS_DIR = get_secrets_dir()

# Google OAuth & Service Account
CLIENT_SECRETS_PATH: Path = SECRETS_DIR / "client_secrets.json"
CREDENTIALS_PATH: Path = SECRETS_DIR / "credentials.json"

# Estados de sesión
META_STATE_PATH: Path = SECRETS_DIR / "meta_state.json"
YOUTUBE_STATE_PATH: Path = SECRETS_DIR / "youtube_state.json"

# Directorio de tokens adicionales
TOKENS_DIR: Path = SECRETS_DIR / "tokens"


# ============================================================================
# FUNCIONES DE UTILIDAD
# ============================================================================


def get_meta_state_path(index: Optional[int] = None) -> Path:
    """
    Obtiene la ruta al archivo de estado de Meta AI.

    Args:
        index: Número de cuenta (1, 2, 3...) para rotación de cuentas.
               Si es None, retorna meta_state.json (cuenta principal)

    Returns:
        Path al archivo de estado

    Ejemplo:
        >>> get_meta_state_path()  # ~/.miura_forge/meta_state.json
        >>> get_meta_state_path(1)  # ~/.miura_forge/meta_state_1.json
        >>> get_meta_state_path(2)  # ~/.miura_forge/meta_state_2.json
    """
    if index is None:
        return META_STATE_PATH
    return SECRETS_DIR / f"meta_state_{index}.json"


def get_youtube_state_path(index: Optional[int] = None) -> Path:
    """
    Obtiene la ruta al archivo de estado de YouTube.

    Args:
        index: Número de cuenta para rotación

    Returns:
        Path al archivo de estado
    """
    if index is None:
        return YOUTUBE_STATE_PATH
    return SECRETS_DIR / f"youtube_state_{index}.json"


def list_available_meta_accounts() -> list:
    """
    Lista todas las cuentas de Meta AI disponibles.

    Returns:
        Lista de tuplas (index, path) para cada cuenta disponible
    """
    accounts = []

    # Cuenta principal
    if META_STATE_PATH.exists():
        accounts.append((None, META_STATE_PATH))

    # Cuentas adicionales (meta_state_1.json, meta_state_2.json, etc.)
    for i in range(1, 10):  # Soporta hasta 9 cuentas
        path = get_meta_state_path(i)
        if path.exists():
            accounts.append((i, path))

    return accounts


def credentials_exist() -> dict:
    """
    Verifica qué credenciales existen en el sistema.

    Returns:
        Diccionario con estado de cada credencial
    """
    return {
        "client_secrets": CLIENT_SECRETS_PATH.exists(),
        "credentials": CREDENTIALS_PATH.exists(),
        "meta_state": META_STATE_PATH.exists(),
        "youtube_state": YOUTUBE_STATE_PATH.exists(),
        "secrets_dir": SECRETS_DIR.exists(),
        "tokens_dir": TOKENS_DIR.exists(),
    }


def print_credentials_status():
    """
    Imprime el estado de las credenciales de forma legible.
    """
    from rich.console import Console
    from rich.table import Table

    console = Console()
    status = credentials_exist()

    table = Table(title="🔐 Estado de Credenciales Miura Forge")
    table.add_column("Credencial", style="cyan")
    table.add_column("Estado", justify="center")
    table.add_column("Ruta", style="dim")

    items = [
        ("Client Secrets (OAuth)", status["client_secrets"], CLIENT_SECRETS_PATH),
        ("Credentials (Sheets)", status["credentials"], CREDENTIALS_PATH),
        ("Meta State", status["meta_state"], META_STATE_PATH),
        ("YouTube State", status["youtube_state"], YOUTUBE_STATE_PATH),
        ("Tokens Dir", status["tokens_dir"], TOKENS_DIR),
    ]

    for name, exists, path in items:
        icon = "✅" if exists else "❌"
        status_text = "[green]Existe[/]" if exists else "[red]No existe[/]"
        table.add_row(name, f"{icon} {status_text}", str(path))

    console.print(table)

    # Verificar cuentas Meta disponibles
    meta_accounts = list_available_meta_accounts()
    if meta_accounts:
        console.print(f"\n[green]Cuentas Meta AI disponibles: {len(meta_accounts)}[/]")
        for idx, path in meta_accounts:
            name = f"Cuenta {idx}" if idx else "Cuenta Principal"
            console.print(f"  • {name}: {path}")
    else:
        console.print("\n[yellow]No se encontraron cuentas Meta AI configuradas[/]")


# ============================================================================
# SCRIPT DE MIGRACIÓN
# ============================================================================


def migrate_credentials_from_legacy():
    """
    Migra credenciales desde la raíz del proyecto al directorio seguro.

    Este es un helper para facilitar la transición de la estructura antigua
    a la nueva estructura segura.

    Uso:
        python -c "from core.config import migrate_credentials_from_legacy; migrate_credentials_from_legacy()"
    """
    import shutil
    from rich.console import Console

    console = Console()
    legacy_dir = Path(__file__).resolve().parent.parent

    console.print("[cyan]Iniciando migración de credenciales...[/]")

    # Asegurar que existe el directorio seguro
    secrets_dir = ensure_secrets_dir()

    files_to_migrate = [
        ("client_secrets.json", "OAuth Client Secrets"),
        ("credentials.json", "Google Sheets Credentials"),
        ("meta_state.json", "Meta AI Session State"),
        ("youtube_state.json", "YouTube Session State"),
    ]

    migrated = []
    skipped = []

    for filename, description in files_to_migrate:
        legacy_path = legacy_dir / filename
        new_path = secrets_dir / filename

        if legacy_path.exists():
            if not new_path.exists():
                shutil.copy2(legacy_path, new_path)
                migrated.append((filename, description))
                console.print(f"  [green]✓[/] Migrado: {description}")
            else:
                skipped.append((filename, "Ya existe en destino"))
                console.print(f"  [yellow]![/] Omitido: {description} (ya existe)")

    # Migrar directorio tokens si existe
    legacy_tokens = legacy_dir / "tokens"
    if legacy_tokens.exists() and legacy_tokens.is_dir():
        if not TOKENS_DIR.exists():
            shutil.copytree(legacy_tokens, TOKENS_DIR)
            migrated.append(("tokens/", "Tokens directory"))
            console.print(f"  [green]✓[/] Migrado: Directorio de tokens")
        else:
            skipped.append(("tokens/", "Ya existe en destino"))

    # Resumen
    console.print(f"\n[bold]Resumen de migración:[/]")
    console.print(f"  [green]Migrados: {len(migrated)}[/]")
    console.print(f"  [yellow]Omitidos: {len(skipped)}[/]")
    console.print(f"\n[dim]Credenciales ahora en: {secrets_dir}[/]")

    return migrated, skipped


if __name__ == "__main__":
    # Si se ejecuta directamente, mostrar estado y ofrecer migración
    print_credentials_status()

    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "--migrate":
        print("\n")
        migrate_credentials_from_legacy()
