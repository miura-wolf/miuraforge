import os
import sys
from dotenv import load_dotenv

# Asegurar que el script encuentre los módulos de la carpeta 'core' y 'llm'
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from core.visual_director import VisualDirector
from core.database import Database
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm

load_dotenv()
console = Console()

from rich.table import Table

def listar_registros_produccion(db):
    """Muestra una tabla con los últimos MASTERs en producción."""
    console.print("\n[bold cyan]📡 Escaneando Puente de Mando (PRODUCCIÓN)...[/]")
    try:
        rows = db.produccion.get_all_values()
        if len(rows) <= 1:
            console.print("[red]⚠️ No hay registros en la tabla PRODUCCION.[/]")
            return None
        
        headers = rows[0]
        # Identificamos columnas
        try:
            idx_id = headers.index('ID_Sesion') if 'ID_Sesion' in headers else 0
            idx_fase = headers.index('Fase') if 'Fase' in headers else 1
            idx_guion = headers.index('Guion') if 'Guion' in headers else 2
            idx_estado = headers.index('Estado') if 'Estado' in headers else 5
        except:
            idx_id, idx_fase, idx_guion, idx_estado = 0, 1, 2, 5

        # Filtramos solo los MASTER
        masters = [r for r in rows[1:] if str(r[idx_fase]).strip().upper() == "MASTER"]
        # Tomamos los últimos 10
        masters = masters[-10:]

        table = Table(title="💎 ÚLTIMOS GUIONES MASTER EN PRODUCCIÓN", title_style="bold magenta")
        table.add_column("N°", style="cyan")
        table.add_column("ID Sesión", style="white")
        table.add_column("Guion (Fragmento)", style="italic yellow")
        table.add_column("Estado", style="green")

        for i, m in enumerate(masters):
            fragmento = f"“{m[idx_guion][:50]}...”"
            table.add_row(str(i+1), m[idx_id], fragmento, m[idx_estado])

        console.print(table)
        return masters, idx_guion
    except Exception as e:
        console.print(f"[red]❌ Error leyendo Sheets: {e}[/]")
        return None, None

def visual_lab():
    console.print(Panel("🧪 [bold cyan]MIURA VISUAL LAB[/]\n[white]Laboratorio independiente para experimentación estética y prompts visuales.[/]", border_style="cyan"))

    db = Database()
    director_v = VisualDirector(db_manager=db)

    while True:
        console.print("\n[bold yellow]--- MENÚ DE EXPERIMENTACIÓN ---[/]")
        console.print("1) Pegar texto manualmente (Guion, Letras, etc.)")
        console.print("2) Cargar desde archivo .txt")
        console.print("3) [bold cyan]Cargar desde Google Sheets (Explorar PRODUCCIÓN)[/]")
        console.print("4) Salir")
        
        opc = Prompt.ask("Seleccione entrada", choices=["1", "2", "3", "4"])

        texto_input = ""
        tema_sugerido = "General"

        if opc == "1":
            texto_input = console.input("[bold green]📝 Pegue el texto aquí (Presione Enter al terminar):[/]\n")
        elif opc == "2":
            ruta = Prompt.ask("[bold green]📂 Ingrese la ruta del archivo .txt[/]")
            if os.path.exists(ruta):
                with open(ruta, "r", encoding="utf-8") as f:
                    texto_input = f.read()
            else:
                console.print("[red]❌ Archivo no encontrado.[/]")
                continue
        elif opc == "3":
            masters, idx_guion = listar_registros_produccion(db)
            if masters:
                idx = Prompt.ask("\n[bold yellow]Seleccione el guion para re-visualizar (N°) o [n] para cancelar[/]")
                if idx.lower() != 'n' and idx.isdigit():
                    seleccion = masters[int(idx)-1]
                    texto_input = seleccion[idx_guion]
                    # Intentar detectar tema desde el ID o dejar general
                    console.print(f"[green]✅ Guion cargado correctamente: {seleccion[0]}[/]")
                else:
                    continue
            else:
                continue
        elif opc == "4":
            break

        if not texto_input:
            console.print("[red]⚠️ No hay texto para procesar.[/]")
            continue

        # --- SECCIÓN DE ESTILO ---
        console.print("\n" + "-"*30)
        console.print("[bold magenta]🎨 CONFIGURACIÓN DE ESTILO[/]")
        console.print("0) Estilo Industrial Base (Por defecto)")
        console.print("1) Cyberpunk Industrial (Neones + Vapor)")
        console.print("2) Cinematic Noir (Cine Negro 1940, Alto contraste)")
        console.print("3) Abstracto/Simbólico (Metáforas visuales puras)")
        console.print("4) Letras de Canción (Estilo videoclip onírico)")
        console.print("5) PERSONALIZADO (Definir manualmente)")

        estilo_opc = Prompt.ask("Seleccione atmósfera", choices=["0", "1", "2", "3", "4", "5"])
        
        modificador_estilo = ""
        if estilo_opc == "1":
            modificador_estilo = "Estética Cyberpunk Industrial. Neones naranja brasa en la penumbra, cables oxidados, lluvia ácida, vapor saliendo de tuberías."
        elif estilo_opc == "2":
            modificador_estilo = "Estética Film Noir clásico. Granulado de película 35mm, sombras dramáticas (venetian blinds), humedad en el pavimento, humo de cigarrillo industrial."
        elif estilo_opc == "3":
            modificador_estilo = "Estética abstracta y minimalista. Fondo negro infinito, objetos aislados flotando, iluminación cenital dramática, simbolismo puro."
        elif estilo_opc == "4":
            modificador_estilo = "Estética de videoclip onírico. Movimientos de cámara lentos, desenfoques artísticos, colores desaturados, atmósfera melancólica pero potente."
        elif estilo_opc == "5":
            modificador_estilo = Prompt.ask("[bold yellow]Describa el estilo deseado (en español)[/]")

        # --- CÁLCULO DINÁMICO DE CLIPS ---
        duracion_est = director_v.estimar_duracion_segundos(texto_input)
        console.print(f"\n[bold yellow]⏱️ Duración estimada por locución (155 ppm): {duracion_est}s[/]")
        
        if Confirm.ask("¿Desea ingresar el tiempo REAL manualmente? (Recomendado para canciones/música)"):
            m = int(Prompt.ask("Minutos"))
            s = int(Prompt.ask("Segundos"))
            duracion = (m * 60) + s
        else:
            duracion = duracion_est

        num_clips = max(8, round(duracion / 4))
        
        console.print(f"\n🚀 [cyan]Generando {num_clips} prompts visuales para una duración real de {duracion}s...[/]")
        
        # Obtenemos la doctrina base pero le inyectamos el modificador
        doctrina_base = director_v.leer_doctrina()
        
        prompt_final = f"""
        {doctrina_base}
        
        --- MODIFICADOR DE ESTILO ADICIONAL (PRIORIDAD) ---
        {modificador_estilo}
        
        --- MISIÓN TÉCNICA (CÁLCULO DINÁMICO) ---
        El texto analizado tiene una duración estimada de {duracion} segundos.
        DEBES generar exactamente {num_clips} prompts visuales numerados.
        Distribuye la narrativa visual de forma equilibrada a lo largo de todo el contenido.
        
        --- TEXTO A ANALIZAR ---
        {texto_input}
        """

        try:
            resultado = director_v.brain.generate(prompt_final)
            
            console.print("\n" + "="*40)
            console.print(Panel(resultado, title="🧪 RESULTADO DEL LABORATORIO VISUAL", border_style="magenta"))
            
            save = Confirm.ask("¿Desea guardar este resultado en un archivo?")
            if save:
                filename = f"output/LAB_VISUAL_{estilo_opc}.txt"
                os.makedirs("output", exist_ok=True)
                with open(filename, "w", encoding="utf-8") as f:
                    f.write(f"--- TEXTO INPUT ---\n{texto_input}\n\n")
                    f.write(f"--- ESTILO ---\n{modificador_estilo if modificador_estilo else 'Industrial Base'}\n\n")
                    f.write(f"--- RESULTADO ---\n{resultado}")
                console.print(f"[green]✅ Guardado en: {filename}[/]")
                
        except Exception as e:
            console.print(f"[red]❌ Error en la forja visual: {e}[/]")

if __name__ == "__main__":
    visual_lab()
