"""
db_singleton.py — Singleton de Database para MiuraForge
========================================================
Reemplaza las 11 instancias de `db = Database()` a nivel de módulo
por UNA sola conexión compartida.

Uso:
    from core.db_singleton import get_db
    db = get_db()  # Primera llamada crea la conexión, siguientes reutilizan

Soberano: Andres | Gran Visir: Mehmed 2
Fix: H1 — Auditoría 2026-04-01
"""

from core.database import Database

_db_instance = None


def get_db():
    """
    Retorna la instancia singleton de Database.
    La crea la primera vez que se llama, reutiliza en llamadas siguientes.
    """
    global _db_instance
    if _db_instance is None:
        _db_instance = Database()
    return _db_instance


def reset_db():
    """
    Fuerza recreación de la instancia en el próximo get_db().
    Usar solo en testing o si necesitás reconectar con otro spreadsheet.
    """
    global _db_instance
    _db_instance = None
