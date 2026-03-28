import os
import sys
import datetime
import re
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
UMBRAL_COHERENCIA = 8
UMBRAL_ADN        = 8
# ─────────────────────────────────────────────────────────────────────────────

def _evaluar_calidad(db, timestamp_video):
    def safe_int(val):
        try:
            if not val: return 0
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
        return "revision", 0, 0

def forja_masiva_variantes():
    console.print(Panel("⚔️ [bold magenta]MIURA FORGE ENGINE - FORJA DE VARIANTES (PROTEGIDA)[/]", border_style="magenta"))
    
    db = Database()
    architect = Architect(db_manager=db)
    auditor = MiuraAuditorBunker()
    
    # 1. Obtener Backlog de Ganchos
    console.print("\n[bold cyan]📡 Accediendo al Arsenal de Ganchos (Backlog)...[/]")
    ganchos = db.ganchos.get_all_records()
    
    if not ganchos:
        console.print("[yellow]⚠️ No hay ideas en el backlog.[/]")
        return

    sesiones = sorted(list(set([g.get('ID_SESION') for g in ganchos])), reverse=True)
    
    table = Table(title="💎 SESIONES EN EL BACKLOG", border_style="bright_black")
    table.add_column("N°", justify="center", style="cyan")
    table.add_column("ID Sesión", style="white")
    table.add_column("Ideas Disponibles", justify="center", style="green")
    
    for i, s in enumerate(sesiones[:10]):
        count = sum(1 for g in ganchos if g.get('ID_SESION') == s)
        table.add_row(str(i+1), s, str(count))
    
    console.print(table)
    opcion = console.input("\n[bold yellow]Soberano, elija una Sesión (N°) o [Enter] para la más reciente: [/]")
    
    id_elegido = sesiones[0]
    if opcion and opcion.isdigit() and int(opcion) <= len(sesiones):
        id_elegido = sesiones[int(opcion)-1]
    
    ideas_filtradas = [g for g in ganchos if g.get('ID_SESION') == id_elegido]
    
    # CREACIÓN DE MARCA DE VARIANTE (EVITA SOBREESCRITURAS)
    tag_variante = datetime.datetime.now().strftime("%H%M")
    console.print(f"\n🚀 [bold green]Iniciando Forja de VARIANTES para {len(ideas_filtradas)} ideas (Tag: {tag_variante})...[/]")
    
    confirmar = console.input(f"[bold yellow]¿Desea forjar los {len(ideas_filtradas)} guiones? No se sobreescribirán los anteriores. (s/n): [/]").lower()
    if confirmar != 's':
        console.print("[red]Aborta por mando humano.[/]")
        return

    aprobados = 0
    en_revision = 0
    metaforas_sesion = []

    for idx, idea in enumerate(ideas_filtradas):
        hook     = idea.get('GANCHO')
        plantilla = idea.get('PLANTILLA')
        
        # ID ÚNICO CON TAG DE VARIANTE
        timestamp_video = f"MASIVA_{id_elegido}_{idx+1}_{tag_variante}"
        
        console.print(f"\n[bold magenta]──────────────────────────────────────────────────────────────────[/]")
        console.print(f"🔥 [Variante {idx+1}/{len(ideas_filtradas)}] Procesando: [italic white]\"{hook}\"[/]")
        
        db.registrar_sesion(timestamp_video, hook, f"Variante ({plantilla})")
        
        banned = ", ".join(metaforas_sesion)
        with console.status(f"[bold white]Andrés: Forjando Variante para {hook}..."):
            guion_master = architect.redactar_guion_completo(
                tema_global=hook,
                timestamp=timestamp_video,
                data_estrategica=f"METÁFORAS PROHIBIDAS EN ESTA SESIÓN: {banned}" if banned else None
            )
        
        # Auditoría
        with console.status(f"[bold red]Auditor: Aplicando Protocolo de Calidad..."):
            db.registrar_auditoria_inicial(timestamp_video, guion_master)
            auditor.ejecutar_auditoria(id_master=timestamp_video)
            guion_final = db.obtener_guion_optimizado(timestamp_video) or guion_master
        
        estado_final, coherencia, adn = _evaluar_calidad(db, timestamp_video)
        
        if estado_final == "aprobado":
            aprobados += 1
            console.print(f"✅ [bold green][APROBADO][/] Coherencia: {coherencia} | ADN: {adn}")
        else:
            en_revision += 1
            console.print(f"⚠️  [bold yellow][REVISIÓN][/] Coherencia: {coherencia} | ADN: {adn}")

        db.guardar_fase(
            timestamp=timestamp_video,
            fase="MASTER",
            guion=guion_final,
            visual="Visual pendiente",
            ruta_local=f"output/{timestamp_video}.txt",
            estado=estado_final
        )
        
        estado_logistica = "Guiones Finalizados" if estado_final == "aprobado" else "Pendiente Revisión"
        db.actualizar_estado_logistica(timestamp_video, estado_logistica)

    console.print(f"\n[bold green]🏆 ¡Misión Cumplida! {len(ideas_filtradas)} variantes forjadas.[/]")

if __name__ == "__main__":
    forja_masiva_variantes()
