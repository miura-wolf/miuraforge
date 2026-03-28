import os
import sys
import json
import re
import argparse
import datetime
from rich.console import Console
from rich.panel import Panel

# Configuración de rutas
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from llm.factory import LLMFactory
from core.database import Database

console = Console()

class MiuraDeployer:
    def __init__(self):
        self.db = Database()
        self.brain = LLMFactory.get_brain("deployer")
        self.temperature = 0.25
        self.reasoning_effort = "low"
        
        self.prompt_path = os.path.join("prompts", "deployer.txt")

    def cargar_prompts(self):
        if os.path.exists(self.prompt_path):
            with open(self.prompt_path, "r", encoding="utf-8") as f:
                return f.read()
        return "Actúa como estratega de marketing industrial. Genera metadata de lanzamiento."

    def ejecutar_despliegue(self, id_master=None, ruta_local=None):
        console.print(Panel("🚀 [bold green]MIURA DEPLOYER[/] - Preparando Lanzamiento", border_style="green"))
        
        guion_master = ""
        
        if id_master:
            console.print(f"📡 [Sheets] Recuperando MASTER para despliegue: [bold cyan]{id_master}[/]")
            master_data = self.db.obtener_master_aprobado(id_master)
            if master_data:
                guion_master = master_data['guion']
            else:
                console.print("[red]❌ Error: No se encontró un MASTER aprobado para este ID.[/]")
                return
        elif ruta_local:
            if os.path.exists(ruta_local):
                with open(ruta_local, "r", encoding="utf-8") as f:
                    guion_master = f.read()
            else:
                console.print("[red]❌ Error: Archivo local no encontrado.[/]")
                return
        else:
            console.print("[red]❌ Error: Se requiere un ID o una ruta de archivo.[/]")
            return

        # Generación con LLM
        with console.status("[bold cyan]Generando paquete de despliegue estratégico...[/]"):
            prompt_base = self.cargar_prompts()
            full_prompt = f"{prompt_base}\n\nGUION MASTER:\n{guion_master}"
            
            try:
                respuesta = self.brain.generate(
                    full_prompt, 
                    temperature=self.temperature, 
                    reasoning_effort=self.reasoning_effort
                )
                
                # Limpiar la respuesta si la IA mete markdown blocks
                json_str = re.search(r'\{.*\}', respuesta, re.DOTALL)
                if json_str:
                    metadata = json.loads(json_str.group())
                else:
                    metadata = json.loads(respuesta)
            except Exception as e:
                console.print(f"[red]❌ Error procesando metadata: {e}[/]")
                # Fallback manual o error
                return

        # Mostrar Resultados
        console.print("\n[bold yellow]📋 PAQUETE DE LANZAMIENTO GENERADO:[/]")
        console.print(f"[bold white]Títulos sugeridos:[/]\n - " + "\n - ".join(metadata.get("titulos", [])))
        console.print(f"[bold white]Gancho Visual (0-3s):[/] {metadata.get('gancho')}")
        console.print(f"[bold white]Descripción:[/]\n{metadata.get('descripcion')}")
        console.print(f"[bold white]Hashtags:[/] {metadata.get('hashtags')}")
        console.print(f"[bold white]CTA:[/] {metadata.get('cta')}")
        console.print(f"[bold white]Territorio:[/] {metadata.get('territorio')}")

        titulos = metadata.get("titulos", [])
        titulo_principal = titulos[0] if titulos else ""
        subtitulos = " / ".join(titulos[1:]) if len(titulos) > 1 else ""

        # Guardar en Sheets
        data_sheets = {
            "id_master": id_master if id_master else "LOCAL_" + datetime.datetime.now().strftime("%Y%m%d"),
            "titulo": titulo_principal,
            "subtitulo": subtitulos,
            "descripcion": metadata.get("descripcion"),
            "hashtags": metadata.get("hashtags"),
            "gancho": metadata.get("gancho"),
            "cta": metadata.get("cta"),
            "territorio": metadata.get("territorio")
        }
        
        self.db.registrar_despliegue(data_sheets)
        
        # Guardar archivo local de respaldo
        output_dir = os.path.join("output", f"DEPLOY_{id_master or 'LOCAL'}")
        os.makedirs(output_dir, exist_ok=True)
        with open(os.path.join(output_dir, "metadata_despliegue.json"), "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=4)
        
        console.print(f"\n[bold green]✅ Despliegue completado y registrado. Archivo guardado en {output_dir}[/]")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Miura Deployer")
    parser.add_argument("--id", help="ID de Sesión / ID_MASTER")
    parser.add_argument("--file", help="Ruta local del guion Master")
    args = parser.parse_args()

    deployer = MiuraDeployer()
    deployer.ejecutar_despliegue(id_master=args.id, ruta_local=args.file)
