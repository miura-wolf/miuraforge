import os
import sys
import datetime
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn

# Sincronizar rutas
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.database import Database
from core.architect import Architect
from auditoria.miura_auditor_bunker import MiuraAuditorBunker

console = Console()

# ─── UMBRAL DE CALIDAD PARA DATASET DE FINE-TUNING ───────────────────────────
# Solo guiones con Coherencia >= 8 Y ADN >= 8 se marcan como "aprobado".
# El resto queda en "revision" para revisión manual del Soberano.
UMBRAL_COHERENCIA = 8
UMBRAL_ADN        = 8
# ─────────────────────────────────────────────────────────────────────────────

def _evaluar_calidad(db, timestamp_video):
    """
    Lee las métricas del Auditor desde Sheets y determina el estado final.
    Retorna: ("aprobado", coherencia, adn) o ("revision", coherencia, adn)
    """
    def safe_int(val):
        try:
            if not val: return 0
            # Limpiar posibles caracteres no numéricos
            limpio = re.sub(r'\D', '', str(val))
            return int(limpio) if limpio else 0
        except:
            return 0

    try:
        resultado = db.obtener_resultados_auditoria(timestamp_video)
        coherencia = safe_int(resultado.get('coherencia'))
        adn        = safe_int(resultado.get('adn_acero'))
        
        if coherencia >= UMBRAL_COHERENCIA and adn >= UMBRAL_ADN:
            return "aprobado", coherencia, adn
        else:
            return "revision", coherencia, adn
    except Exception as e:
        console.print(f"[yellow]⚠️ No se pudieron leer métricas del Auditor para {timestamp_video}: {e}[/]")
        # Si no se pueden leer métricas, va a revisión por precaución
        return "revision", 0, 0


def forja_masiva():
    console.print(Panel("⚔️ [bold red]MIURA FORGE ENGINE - FORJA MASIVA DE GUIONES[/]", border_style="red"))
    
    db = Database()
    architect = Architect(db_manager=db)
    auditor = MiuraAuditorBunker()
    
    # 1. Obtener Backlog de Ganchos
    console.print("\n[bold cyan]📡 Accediendo al Arsenal de Ganchos (Backlog)...[/]")
    ganchos = db.ganchos.get_all_records()
    
    if not ganchos:
        console.print("[yellow]⚠️ No hay ideas en el backlog. Inicia una investigación primero (Opción 1).[/]")
        return

    # Mostrar sesiones únicas en el backlog
    sesiones = sorted(list(set([g.get('ID_SESION') for g in ganchos])), reverse=True)
    
    table = Table(title="💎 SESIONES EN EL BACKLOG", border_style="bright_black")
    table.add_column("N°", justify="center", style="cyan")
    table.add_column("ID Sesión", style="white")
    table.add_column("Ideas Disponibles", justify="center", style="green")
    
    for i, s in enumerate(sesiones[:10]):  # Mostrar últimas 10
        count = sum(1 for g in ganchos if g.get('ID_SESION') == s)
        table.add_row(str(i+1), s, str(count))
    
    console.print(table)
    opcion = console.input("\n[bold yellow]Soberano, elija una Sesión (N°) o [Enter] para la más reciente: [/]")
    
    id_elegido = sesiones[0]
    if opcion and opcion.isdigit() and int(opcion) <= len(sesiones):
        id_elegido = sesiones[int(opcion)-1]
    
    ideas_filtradas = [g for g in ganchos if g.get('ID_SESION') == id_elegido]
    
    console.print(f"\n🚀 [bold green]Iniciando Forja Masiva para {len(ideas_filtradas)} ideas de la sesión {id_elegido}...[/]")
    
    confirmar = console.input(f"[bold yellow]¿Desea forjar los {len(ideas_filtradas)} guiones ahora? (s/n): [/]").lower()
    if confirmar != 's':
        console.print("[red]Aborta por mando humano.[/]")
        return

    # Contadores de sesión
    aprobados = 0
    en_revision = 0
    metaforas_sesion = []

    for idx, idea in enumerate(ideas_filtradas):
        hook     = idea.get('GANCHO')
        plantilla = idea.get('PLANTILLA')
        
        # Generar un ID único para este video masivo
        timestamp_video = f"MASIVA_{id_elegido}_{idx+1}"
        
        console.print(f"\n[bold magenta]──────────────────────────────────────────────────────────────────[/]")
        console.print(f"🔥 [Forja {idx+1}/{len(ideas_filtradas)}] Procesando Idea: [italic white]\"{hook}\"[/]")
        
        # 2. Registrar en Logística
        db.registrar_sesion(timestamp_video, hook, f"Masiva ({plantilla})")
        
        # 3. Arquitecto: Generar Guion Master
        banned = ", ".join(metaforas_sesion)
        if banned:
            console.print(f"[dim]🧠 Metáforas bloqueadas esta sesión: {banned}[/]")

        with console.status(f"[bold white]Andrés: Forjando Guion para {hook}..."):
            guion_master = architect.redactar_guion_completo(
                tema_global=hook,
                timestamp=timestamp_video,
                data_estrategica=f"METÁFORAS PROHIBIDAS EN ESTA SESIÓN: {banned}" if banned else None
            )
        
        # 3.1 Actualizar memoria de la sesión
        try:
            extract_prompt = f"Extrae solo 3 metáforas clave de este texto (ej: 'anestesia', 'tumba'). Solo palabras, separadas por coma: {guion_master}"
            nuevas = architect.brain.generate(extract_prompt, temperature=0.1, reasoning_effort="low")
            if nuevas:
                metaforas_sesion.extend([m.strip().lower() for m in nuevas.split(',') if m.strip()])
                metaforas_sesion = list(set(metaforas_sesion)) # Deduplicar
        except Exception as e:
            console.print(f"[dim yellow]⚠️ No se pudo extraer metáforas: {e}[/]")
        
        # 4. Auditor: Refinamiento y Control de Calidad
        with console.status(f"[bold red]Auditor: Aplicando Protocolo de Calidad..."):
            db.registrar_auditoria_inicial(timestamp_video, guion_master)
            auditor.ejecutar_auditoria(id_master=timestamp_video)
            
            # Recuperar la versión optimizada si existe
            guion_final = db.obtener_guion_optimizado(timestamp_video) or guion_master
        
        # 5. FIX — Filtro de calidad para dataset de fine-tuning
        # Solo entra como "aprobado" si supera los umbrales doctrinales.
        # Estado "revision" = requiere revisión manual antes de ir al dataset.
        estado_final, coherencia, adn = _evaluar_calidad(db, timestamp_video)
        
        if estado_final == "aprobado":
            aprobados += 1
            console.print(f"✅ [bold green][APROBADO][/] Coherencia: {coherencia} | ADN: {adn} — Entra al dataset.")
        else:
            en_revision += 1
            console.print(f"⚠️  [bold yellow][REVISIÓN][/] Coherencia: {coherencia} | ADN: {adn} — Requiere revisión manual.")

        # 6. Guardar en Producción con el estado determinado por el Auditor
        db.guardar_fase(
            timestamp=timestamp_video,
            fase="MASTER",
            guion=guion_final,
            visual="Visual pendiente (Forja Masiva)",
            ruta_local=f"output/MASIVA_{timestamp_video}.txt",
            estado=estado_final  # "aprobado" o "revision"
        )
        
        # Actualizar logística
        estado_logistica = "Guiones Finalizados" if estado_final == "aprobado" else "Pendiente Revisión"
        db.actualizar_estado_logistica(timestamp_video, estado_logistica)

    # ─── REPORTE FINAL DE SESIÓN ─────────────────────────────────────────────
    console.print(f"\n[bold green]🏆 ¡Misión Cumplida! {len(ideas_filtradas)} guiones procesados.[/]")
    console.print(f"   ✅ [green]Aprobados (dataset ready):[/]  {aprobados}")
    console.print(f"   ⚠️  [yellow]En revisión manual:[/]         {en_revision}")
    console.print("\n[cyan]Revise el estado de cada guion en la hoja PRODUCCION de Google Sheets.[/]")
    console.print("[cyan]Los guiones en 'revision' necesitan su aprobación antes de ir al dataset.[/]")

if __name__ == "__main__":
    forja_masiva()
