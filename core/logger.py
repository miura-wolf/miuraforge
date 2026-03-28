import sys
import os

class CombatLogger:
    """
    Proxy de salida para el Registro de Combate.
    Escribe simultáneamente en la terminal y en un archivo de log.
    """
    def __init__(self, log_file_path):
        self.terminal = sys.stdout
        self.log_file = open(log_file_path, "a", encoding="utf-8")
        
        # Encabezado del log
        self.log_file.write(f"\n{'='*50}\n")
        self.log_file.write(f"⚔️ REGISTRO DE COMBATE EMPEZADO\n")
        self.log_file.write(f"{'='*50}\n\n")

    def write(self, message):
        self.terminal.write(message)
        self.log_file.write(message)
        self.log_file.flush() # Asegurar que se escribe en disco

    def flush(self):
        self.terminal.flush()
        self.log_file.flush()

    def close(self):
        self.log_file.write(f"\n{'='*50}\n")
        self.log_file.write(f"🏁 FIN DEL REGISTRO\n")
        self.log_file.write(f"{'='*50}\n")
        self.log_file.close()

def iniciar_registro_combate(ruta_carpeta):
    """Activa el redireccionamiento de la salida al archivo de logs de la sesión."""
    log_path = os.path.join(ruta_carpeta, "registro_combate.log")
    logger = CombatLogger(log_path)
    sys.stdout = logger
    return logger
