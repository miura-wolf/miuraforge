#!/usr/bin/env python3
"""
migrar_credenciales.py — MiuraForgeEngine
============================================
Script de migración para mover credenciales desde la raíz del proyecto
al directorio seguro ~/.miura_forge/

Este script migra:
- credentials.json (Google Sheets)
- client_secrets.json (OAuth Google)
- meta_state.json (Meta AI)
- youtube_state.json (YouTube)
- tokens/ (directorio de tokens)

Uso:
    python migrar_credenciales.py [--ejecutar]

Sin --ejecutar: solo muestra qué se migraría (modo simulación)
Con --ejecutar: realiza la migración real
"""

import os
import sys
import shutil
import argparse
from pathlib import Path
from datetime import datetime


def print_header():
    print("=" * 70)
    print("🔐 MIURA FORGE - MIGRACIÓN DE CREDENCIALES")
    print("=" * 70)
    print()


def get_project_root():
    """Obtiene la raíz del proyecto (donde está este script)"""
    return Path(__file__).resolve().parent


def get_secrets_dir():
    """Obtiene el directorio seguro de credenciales"""
    secrets_dir = Path.home() / ".miura_forge"
    return secrets_dir


def ensure_secrets_dir():
    """Asegura que existe el directorio de credenciales"""
    secrets_dir = get_secrets_dir()
    secrets_dir.mkdir(parents=True, exist_ok=True)

    # Crear .gitignore para proteger el directorio
    gitignore = secrets_dir / ".gitignore"
    if not gitignore.exists():
        gitignore.write_text("*\n!.gitignore\n")

    return secrets_dir


def detect_credentials(project_root):
    """Detecta qué credenciales existen en el proyecto"""
    credenciales = []

    files_to_check = [
        ("credentials.json", "Google Sheets (Service Account)"),
        ("client_secrets.json", "Google OAuth (Client Secrets)"),
        ("meta_state.json", "Meta AI (Session State)"),
        ("youtube_state.json", "YouTube (Session State)"),
    ]

    for filename, description in files_to_check:
        filepath = project_root / filename
        if filepath.exists():
            size = filepath.stat().st_size
            credenciales.append(
                {
                    "file": filename,
                    "description": description,
                    "path": filepath,
                    "size": size,
                    "exists": True,
                }
            )

    # Verificar directorio tokens
    tokens_dir = project_root / "tokens"
    if tokens_dir.exists() and tokens_dir.is_dir():
        credenciales.append(
            {
                "file": "tokens/",
                "description": "Directorio de tokens",
                "path": tokens_dir,
                "size": sum(f.stat().st_size for f in tokens_dir.rglob("*") if f.is_file()),
                "exists": True,
                "is_dir": True,
            }
        )

    return credenciales


def check_existing_in_secrets(secrets_dir, credenciales):
    """Verifica si las credenciales ya existen en el directorio seguro"""
    conflicts = []

    for cred in credenciales:
        dest_path = secrets_dir / cred["file"]
        if dest_path.exists():
            conflicts.append(
                {
                    "file": cred["file"],
                    "source": cred["path"],
                    "dest": dest_path,
                    "is_dir": cred.get("is_dir", False),
                }
            )

    return conflicts


def migrate_file(source, dest, dry_run=True):
    """Migra un archivo o directorio"""
    if dry_run:
        return True

    try:
        if source.is_dir():
            if dest.exists():
                # Si el destino existe, fusionar
                for item in source.iterdir():
                    dest_item = dest / item.name
                    if item.is_dir():
                        shutil.copytree(item, dest_item, dirs_exist_ok=True)
                    else:
                        shutil.copy2(item, dest_item)
            else:
                shutil.copytree(source, dest)
        else:
            shutil.copy2(source, dest)
        return True
    except Exception as e:
        print(f"  ❌ Error al migrar {source.name}: {e}")
        return False


def update_env_file(project_root, dry_run=True):
    """Actualiza el archivo .env para incluir MIURA_FORGE_SECRETS"""
    env_file = project_root / ".env"

    if not env_file.exists():
        return False

    secrets_dir = get_secrets_dir()
    line_to_add = f"\n# Directorio de credenciales seguro\nMIURA_FORGE_SECRETS={secrets_dir}\n"

    if dry_run:
        return True

    try:
        with open(env_file, "r", encoding="utf-8") as f:
            content = f.read()

        # Verificar si ya existe la variable
        if "MIURA_FORGE_SECRETS" in content:
            return True

        # Añadir al final
        with open(env_file, "a", encoding="utf-8") as f:
            f.write(line_to_add)

        return True
    except Exception as e:
        print(f"  ⚠️  No se pudo actualizar .env: {e}")
        return False


def create_backup(project_root, credenciales, dry_run=True):
    """Crea un backup de las credenciales originales"""
    if dry_run:
        return True

    backup_dir = project_root / f"credenciales_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    backup_dir.mkdir(exist_ok=True)

    try:
        for cred in credenciales:
            source = cred["path"]
            dest = backup_dir / cred["file"]

            if source.is_dir():
                shutil.copytree(source, dest, dirs_exist_ok=True)
            else:
                shutil.copy2(source, dest)

        print(f"  ✅ Backup creado en: {backup_dir}")
        return True
    except Exception as e:
        print(f"  ⚠️  No se pudo crear backup: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(
        description="Migra credenciales de Miura Forge al directorio seguro ~/.miura_forge/"
    )
    parser.add_argument(
        "--ejecutar", action="store_true", help="Realiza la migración real (sin esto solo simula)"
    )
    parser.add_argument(
        "--backup",
        action="store_true",
        default=True,
        help="Crea backup antes de migrar (default: True)",
    )
    parser.add_argument(
        "--eliminar-originales",
        action="store_true",
        help="Elimina los archivos originales después de migrar (CUIDADO)",
    )
    args = parser.parse_args()

    print_header()

    project_root = get_project_root()
    secrets_dir = ensure_secrets_dir()

    print(f"📁 Proyecto: {project_root}")
    print(f"🔐 Destino:  {secrets_dir}")
    print()

    # Detectar credenciales
    credenciales = detect_credentials(project_root)

    if not credenciales:
        print("✅ No se encontraron credenciales para migrar en el proyecto.")
        print("   Parece que ya están en el directorio seguro o no existen.")
        return 0

    print(f"📋 Credenciales encontradas ({len(credenciales)}):")
    for cred in credenciales:
        size_str = f"({cred['size']:,} bytes)" if not cred.get("is_dir") else "(directorio)"
        print(f"  • {cred['file']:<20} - {cred['description']:<35} {size_str}")
    print()

    # Verificar conflictos
    conflicts = check_existing_in_secrets(secrets_dir, credenciales)
    if conflicts:
        print("⚠️  ALERTA: Los siguientes archivos ya existen en el destino:")
        for conf in conflicts:
            print(f"  • {conf['file']}")
        print()
        if not args.ejecutar:
            print("   En modo ejecución, se omitirán estos archivos.")
        print()

    # Modo simulación
    if not args.ejecutar:
        print("🔍 MODO SIMULACIÓN - No se realizarán cambios")
        print("   Usa --ejecutar para migrar realmente")
        print()
        print("Resumen de la migración:")
        print(f"  - Se migrarían {len(credenciales)} credenciales")
        if args.backup:
            print(f"  - Se crearía backup en: {project_root}/credenciales_backup_...")
        print(f"  - Se actualizaría: {project_root}/.env")
        print(f"  - Destino: {secrets_dir}")
        return 0

    # MODO EJECUCIÓN REAL
    print("🚀 INICIANDO MIGRACIÓN REAL")
    print()

    # Crear backup
    if args.backup:
        print("📦 Creando backup...")
        create_backup(project_root, credenciales, dry_run=False)
        print()

    # Migrar credenciales
    print("📤 Migrando credenciales...")
    migrados = 0
    omitidos = 0

    for cred in credenciales:
        dest_path = secrets_dir / cred["file"]

        # Verificar si ya existe
        if dest_path.exists():
            print(f"  ⏭️  Omitido (ya existe): {cred['file']}")
            omitidos += 1
            continue

        if migrate_file(cred["path"], dest_path, dry_run=False):
            print(f"  ✅ Migrado: {cred['file']}")
            migrados += 1
        else:
            print(f"  ❌ Falló: {cred['file']}")

    print()

    # Actualizar .env
    print("📝 Actualizando .env...")
    if update_env_file(project_root, dry_run=False):
        print("  ✅ .env actualizado con MIURA_FORGE_SECRETS")
    print()

    # Eliminar originales (opcional)
    if args.eliminar_originales and migrados > 0:
        print("🗑️  Eliminando originales...")
        for cred in credenciales:
            try:
                if cred["path"].is_dir():
                    shutil.rmtree(cred["path"])
                else:
                    cred["path"].unlink()
                print(f"  ✅ Eliminado: {cred['file']}")
            except Exception as e:
                print(f"  ⚠️  No se pudo eliminar {cred['file']}: {e}")
        print()

    # Resumen final
    print("=" * 70)
    print("📊 RESUMEN DE MIGRACIÓN")
    print("=" * 70)
    print(f"  Migrados:   {migrados}")
    print(f"  Omitidos:   {omitidos}")
    print(f"  Total:      {len(credenciales)}")
    print()
    print(f"🔐 Credenciales ahora en: {secrets_dir}")
    print()

    if migrados > 0:
        print("✅ Migración completada exitosamente!")
        print()
        print("Próximos pasos:")
        print("  1. Verifica que los scripts funcionan correctamente")
        print("  2. Los archivos originales siguen en su ubicación")
        print("  3. Para eliminarlos manualmente, hazlo con cuidado")
        print()
        print("📖 Documentación:")
        print("  - core/config.py contiene la lógica de rutas")
        print("  - Usa python core/config.py para verificar estado")
    else:
        print("ℹ️  No se migró nada nuevo (todo ya estaba en el destino)")

    return 0


if __name__ == "__main__":
    sys.exit(main())
