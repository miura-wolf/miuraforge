# ⚔️ MIURA FORGE ENGINE - ORQUESTADOR SDD
# Main.py reestructurado para seguir las 9 fases del workflow SDD
# Documentación: Docs/MIURA_WORKFLOW_SD.md

import os
import datetime
from dotenv import load_dotenv
import sys
import json
import shutil
import platform
import subprocess
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from rich.table import Table
from rich import box

# Cargar variables de entorno
load_dotenv()

console = Console()

# ============================================================================
# ORQUESTADOR SDD - MENÚ PRINCIPAL
# ============================================================================


def mostrar_menu_orquestador():
    """Muestra el menú de las 9 fases SDD."""
    console.print("\n")

    # Banner
    console.print(
        Panel(
            "[bold red]MIURA FORGE ENGINE[/]\n[dim]Orquestador SDD - 9 Fases de Producción[/]",
            border_style="red",
            box=box.DOUBLE,
        )
    )

    # Tabla de Fases SDD
    table = Table(
        title="⚔️ PIPELINE SDD - SELECCIONE FASE",
        title_style="bold cyan",
        border_style="bright_black",
        box=box.ROUNDED,
    )

    table.add_column("Fase", justify="center", style="bold cyan", width=6)
    table.add_column("Nombre", style="white", width=20)
    table.add_column("Descripción", style="dim")
    table.add_column("Skill", style="green", width=20)

    # Fases 1-9
    table.add_row("1", "EXPLORE", "Investigación de tendencias", "sdd-explore")
    table.add_row("2", "PROPOSE", "Propuesta de contenido", "sdd-propose")
    table.add_row("3", "SPEC", "Especificación del guion", "sdd-spec")
    table.add_row("4", "DESIGN", "Diseño de assets", "sdd-design")
    table.add_row("5", "IMPLEMENT", "Generación de video", "sdd-implement")
    table.add_row("6", "VERIFY", "Auditoría de calidad", "sdd-verify")
    table.add_row("7", "SEO", "Optimización YouTube", "sdd-seo")
    table.add_row("8", "DEPLOY", "Publicación", "sdd-deploy")
    table.add_row("9", "ARCHIVE", "Memoria persistente", "sdd-archive")

    console.print(table)

    # Tabla de modos especiales
    table2 = Table(border_style="bright_black", box=box.ROUNDED)
    table2.add_column("Opción", justify="center", style="bold yellow", width=6)
    table2.add_column("Modo", style="white")
    table2.add_column("Descripción", style="dim")

    table2.add_row("10", "FORJA TOTAL", "Pipeline completo automático (Fases 1-9)")
    table2.add_row("11", "HERRAMIENTAS", "Utilidades y herramientas individuales")
    table2.add_row("12", "SALIR", "Cerrar la forja")

    console.print(table2)

    return input("\n[bold]Soberano, seleccione fase: [/]")


# ============================================================================
# FASE 1: EXPLORE (Investigación)
# ============================================================================


def fase_explore(tema=None, auto=False):
    """
    FASE 1 - EXPLORE: Investigación OSINT de tendencias y dolor masculino.

    INPUTS:
        - tema (str, opcional): Tema específico a investigar
        - auto (bool): Si True, usa Oráculo automático

    OUTPUTS:
        - Hallazgos validados con score de intensidad
        - Frases potentes extraídas
        - Tabla INVESTIGACION_PSICOLOGICA actualizada
        - Retorna: (plan_texto, timestamp, tema)

    Skill: sdd-explore
    Documentación: Docs/MIURA_WORKFLOW_SD.md - Fase 1
    """
    console.print(
        Panel(
            "[bold cyan]FASE 1: EXPLORE[/]\n"
            "[dim]Investigando tendencias y dolor en comunidades...[/]",
            border_style="cyan",
        )
    )

    from core.researcher import Researcher
    from core.database import Database
    from core.clusterizador import ClusterizadorDolores
    from core.tendencias import RadarTendencia
    from core.extractor_frases import ExtractorFrases

    if not tema and not auto:
        tema = console.input(
            "[bold yellow]🔍 ¿Qué debilidad humana investigamos? (vacío=Oráculo): [/]"
        )

    # Modo Oráculo automático
    if not tema or auto:
        console.print("[bold cyan]🔮 Invocando Oráculo Semanal...[/]")
        from tools.weekly_oracle import run_weekly_oracle

        run_weekly_oracle()

        db = Database(spreadsheet_name="BD_MiuraForge_Engine")
        tema = seleccionar_tema_sheets(db)
        if not tema:
            console.print("[red]❌ Oráculo no definió tema claro. Abortando.[/]")
            return None

    # Pipeline de investigación
    with Progress(
        SpinnerColumn(),
        BarColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True,
    ) as progress:
        task = progress.add_task("[cyan]Radar OSINT activo...", total=None)

        investigador = Researcher()
        hallazgos_validados, total_analizadas = investigador.buscar_dolor(tema)

        progress.update(task, description="[green]✅ Radar completado.")

    if not hallazgos_validados:
        console.print("[red]❌ No se encontraron testimonios válidos. Abortando.[/]")
        return None

    # Registro e inteligencia
    id_sesion = datetime.datetime.now().strftime("%Y%m%d_%H%M")
    db = Database(spreadsheet_name="BD_MiuraForge_Engine")

    with console.status("[bold magenta]Alquimia: Transmutando hallazgos..."):
        db.registrar_hallazgos(id_sesion, hallazgos_validados)
        db.registrar_investigacion_psicologica(id_sesion, hallazgos_validados, tema=tema)

        for h in hallazgos_validados:
            db.actualizar_dolor(h.get("dolor_principal"))

        # Análisis de clusters y tendencias
        clusterizador = ClusterizadorDolores(db)
        radar = RadarTendencia(db)
        extractor = ExtractorFrases(db)

        clusterizador.clusterizar_dolores()
        radar.calcular_tendencias()
        extractor.extraer_frases_memorables()

    # Reporte
    _mostrar_reporte_explore(tema, hallazgos_validados, id_sesion)

    return id_sesion, tema, hallazgos_validados


def _mostrar_reporte_explore(tema, hallazgos, id_sesion):
    """Muestra reporte de inteligencia MIURA."""
    conteo_dolores = {}
    frases = []

    for h in hallazgos:
        p = h.get("dolor_principal", "identidad")
        conteo_dolores[p] = conteo_dolores.get(p, 0) + 1
        frases.extend(h.get("frases_potentes", []))

    resumen = f"[bold white]NÚCLEOS DE DOLOR:[/]\n"
    for d, c in sorted(conteo_dolores.items(), key=lambda x: x[1], reverse=True):
        resumen += f"• {d.upper()}: {c} menciones\n"

    resumen += f"\n[bold white]FRASES MEMORABLES:[/]\n"
    for f in list(set(frases))[:3]:
        resumen += f'"{f[:90]}..."\n'

    resumen += f"\n[bold cyan]SESION:[/] {id_sesion}"

    console.print(Panel(resumen, title=f"📊 REPORTE EXPLORE - {tema.upper()}", border_style="cyan"))


# ============================================================================
# FASE 2: PROPOSE (Propuesta de Contenido)
# ============================================================================


def fase_propose(id_sesion, tema, hallazgos, modo="estandar", auto=False):
    """
    FASE 2 - PROPOSE: Transformar dolor en estructura narrativa.

    INPUTS:
        - id_sesion (str): Timestamp de la sesión
        - tema (str): Tema investigado
        - hallazgos (list): Hallazgos validados de EXPLORE
        - modo (str): "estandar" (30 títulos) o "backlog" (200 ideas)
        - auto (bool): Si True, salta aprobación humana

    OUTPUTS:
        - Estructura de 3 fases
        - 30 títulos virales (o 200 en modo backlog)
        - Categoría temática
        - JSON con propuesta completa

    Skill: sdd-propose
    Documentación: Docs/MIURA_WORKFLOW_SD.md - Fase 2
    """
    console.print(
        Panel(
            "[bold magenta]FASE 2: PROPOSE[/]\n"
            "[dim]Transmutando dolor en estructura narrativa...[/]",
            border_style="magenta",
        )
    )

    from core.alchemist import Alchemist
    from core.database import Database

    db = Database(spreadsheet_name="BD_MiuraForge_Engine")
    alquimista = Alchemist()

    # Preparar contexto
    texto_consolidado = "\n".join([h["content"] for h in hallazgos])
    memoria_global = db.obtener_memoria_global()

    # Ejecutar alquimia
    with console.status("[bold magenta]Alquimista: Forjando estructura..."):
        plan_raw = alquimista.transmutar_dolor(
            tema, context=texto_consolidado, banned_metaphors=", ".join(memoria_global)
        )

    # Procesar resultado
    categoria = "General"
    try:
        data = json.loads(plan_raw)
        categoria = data.get("categoria", "General")

        # Registrar títulos
        titulos = data.get("titulos_virales", {})
        if titulos:
            db.registrar_ganchos(id_sesion, titulos)
            console.print(f"🎯 [magenta]30 ganchos registrados.[/]")
    except Exception as e:
        console.print(f"[yellow]⚠️ Error parseando JSON: {e}[/]")

    db.registrar_sesion(id_sesion, tema, categoria)

    # Aprobación humana (a menos que auto)
    if not auto:
        console.print(f"\n[bold]Propuesta generada para: {tema}[/]")
        opcion = console.input(
            "\n[1] Enviar a SPEC (guion completo)\n"
            "[2] Modo BACKLOG (200 ideas)\n"
            "[n] Abortar\n\n"
            "Soberano: "
        ).lower()

        if opcion == "n":
            console.print("[yellow]⚠️ Abortado.[/]")
            return None

        if opcion == "2":
            return fase_propose_backlog(id_sesion, hallazgos, alquimista, db)

    console.print(
        Panel(
            f"✅ FASE 2 COMPLETADA\nID: [cyan]{id_sesion}[/]\nCategoría: [white]{categoria}[/]",
            border_style="green",
        )
    )

    return plan_raw, id_sesion


def fase_propose_backlog(id_sesion, hallazgos, alquimista, db):
    """Modo BACKLOG: Generar 200 ideas (10 por insight)."""
    console.print("🚀 [bold cyan]Modo BACKLOG: 10 ideas por insight...[/]")

    for i, insight in enumerate(hallazgos):
        console.print(f" ⚡ Insight {i + 1}/{len(hallazgos)}...")
        ideas = alquimista.generar_ideas_backlog(insight)
        db.registrar_ganchos(id_sesion, {f"Insight_{i + 1}": ideas})

    console.print(f"✅ [green]Backlog de {len(hallazgos) * 10} ideas registrado.[/]")
    return None, id_sesion


# ============================================================================
# FASE 3: SPEC (Especificación)
# ============================================================================


def fase_spec(id_sesion, tema, plan_texto, auto=False):
    """
    FASE 3 - SPEC: Redactar guion MASTER completo.

    INPUTS:
        - id_sesion (str): Timestamp
        - tema (str): Tema del contenido
        - plan_texto (str): Propuesta de PROPOSE (JSON)
        - auto (bool): Si True, salta aprobación

    OUTPUTS:
        - Guion MASTER (130-150 palabras)
        - Prompts visuales duales
        - Registro en Sheets (fase MASTER)

    Constraints:
        - Duración: 50-60 segundos
        - Palabras: 130-150 exactas
        - 0 verbos de duda
        - Tono: Inyección de Carbono

    Skill: sdd-spec
    Documentación: Docs/MIURA_WORKFLOW_SD.md - Fase 3
    """
    console.print(
        Panel(
            "[bold white]FASE 3: SPEC[/]\n[dim]Redactando guion MASTER de acero...[/]",
            border_style="white",
        )
    )

    from core.architect import Architect
    from core.database import Database
    from core.visual_director import VisualDirector
    from core.logger import iniciar_registro_combate

    db = Database(spreadsheet_name="BD_MiuraForge_Engine")
    arquitecto = Architect(db_manager=db)

    # Crear directorio de salida
    ruta_salida = os.path.join("output", f"sesion_{id_sesion}")
    os.makedirs(ruta_salida, exist_ok=True)
    iniciar_registro_combate(ruta_salida)

    # Generar guion
    with console.status(f"[bold white]Andrés: Forjando la verdad..."):
        guion_master = arquitecto.redactar_guion_completo(
            tema_global=tema, timestamp=id_sesion, data_estrategica=plan_texto, skip_approval=auto
        )

    # Loop de aprobación (si no auto)
    while not auto:
        console.print("\n" + "=" * 50)
        console.print(Panel(guion_master, title="📜 GUION MASTER", border_style="cyan"))

        console.print("\n[bold yellow]OPCIONES:[/]")
        console.print("[green]s[/]) Aprobar → Visuales/Voz")
        console.print("[red]n[/]) Reforjar (nueva versión)")
        console.print("[blue]e[/]) Editar manualmente")
        console.print("[bold red]a[/]) Enviar a Auditor")

        aprobacion = console.input("\n⚔️ Soberano: ").lower()

        if aprobacion == "s":
            break
        elif aprobacion == "a":
            # Auditoría
            db.registrar_auditoria_inicial(id_sesion, guion_master)
            subprocess.run(
                [sys.executable, "auditoria/miura_auditor_bunker.py", "--id", str(id_sesion)],
                check=False,
            )

            usar_opt = console.input("\n¿Cargar versión optimizada? (s/n): ")
            if usar_opt.lower() == "s":
                guion_opt = db.obtener_guion_optimizado(id_sesion)
                if guion_opt:
                    guion_master = guion_opt
            continue

        elif aprobacion == "e":
            # Edición manual
            ruta_temp = os.path.join("output", "temp", f"EDIT_{id_sesion}.txt")
            os.makedirs(os.path.dirname(ruta_temp), exist_ok=True)
            with open(ruta_temp, "w", encoding="utf-8") as f:
                f.write(guion_master)

            if platform.system() == "Windows":
                os.startfile(ruta_temp)
            elif platform.system() == "Darwin":
                subprocess.run(["open", ruta_temp])
            else:
                subprocess.run(["xdg-open", ruta_temp])

            console.input("\n⏳ Edita y presiona ENTER...")
            with open(ruta_temp, "r", encoding="utf-8") as f:
                guion_master = f.read().strip()
            os.remove(ruta_temp)
            continue

        elif aprobacion == "n":
            console.print("🔨 [Reforja] Nueva versión...")
            guion_master = arquitecto.redactar_guion_completo(tema, id_sesion, plan_texto)
            continue

    # Guardar aprobado
    db.guardar_fase(
        id_sesion, "MASTER", guion_master, "Visual pendiente", "aprobado", estado="aprobado"
    )

    # Narrativa visual
    console.print("🎨 [Visual] Generando estética...")
    director_v = VisualDirector(db_manager=db)
    visual_ia = director_v.diseñar_estetica(guion_master, tema_global=tema)

    # Guardar archivo físico
    ruta_entrega = os.path.join("output", f"ENTREGA_{id_sesion}")
    os.makedirs(ruta_entrega, exist_ok=True)
    ruta_master = os.path.join(ruta_entrega, f"{id_sesion}_MASTER.txt")

    with open(ruta_master, "w", encoding="utf-8") as f:
        f.write(guion_master)
        f.write(f"\n\n--- PROMPTS VISUALES ---\n{visual_ia}")

    db.guardar_fase(id_sesion, "MASTER", guion_master, visual_ia, ruta_master, estado="aprobado")

    console.print(
        Panel(f"✅ FASE 3 COMPLETADA\nGuion: [cyan]{ruta_master}[/]", border_style="green")
    )

    return guion_master, visual_ia, id_sesion


# ============================================================================
# FASE 4: DESIGN (Diseño de Assets)
# ============================================================================


def fase_design(id_sesion, guion_master, visual_ia, auto=False):
    """
    FASE 4 - DESIGN: Crear prompts visuales y audio.

    INPUTS:
        - id_sesion (str): Timestamp
        - guion_master (str): Guion aprobado
        - visual_ia (str): Directivas visuales
        - auto (bool): Si True, ejecuta sin confirmación

    OUTPUTS:
        - Prompts duales refinados
        - Audio .wav (Andrés)
        - Imágenes generadas (opcional)

    Skill: sdd-design
    Sub-skills: sdd-design-visual, sdd-design-audio
    Documentación: Docs/MIURA_WORKFLOW_SD.md - Fase 4
    """
    console.print(
        Panel(
            "[bold yellow]FASE 4: DESIGN[/]\n[dim]Creando assets visuales y auditivos...[/]",
            border_style="yellow",
        )
    )

    # Sub-fase 4a: Prompts Visuales (ya hecho en SPEC, pero refinamos)
    console.print("\n[bold]4a. Prompts Visuales[/]")

    if not auto:
        generar = console.input("¿Generar prompts masivos? (s/n): ").lower()
        if generar == "s":
            from tools.mass_visual_forge import mass_visual_forge

            mass_visual_forge(target_id=id_sesion)

    # Sub-fase 4b: Audio
    console.print("\n[bold]4b. Audio (Andrés)[/]")

    if not auto:
        generar_voz = console.input("¿Generar voz ahora? (s/n): ").lower()
        if generar_voz == "s":
            flujo_voz_sdd(id_sesion)

    console.print(Panel("✅ FASE 4 COMPLETADA", border_style="green"))
    return True


def flujo_voz_sdd(timestamp):
    """Generar voz para SDD (simplificado)."""
    from core.voice_director import VoiceDirector
    from core.database import Database

    db = Database(spreadsheet_name="BD_MiuraForge_Engine")
    andres = VoiceDirector()

    ruta_salida = os.path.join("output", f"sesion_{timestamp}")
    os.makedirs(ruta_salida, exist_ok=True)

    master_data = db.obtener_master_aprobado(timestamp)
    if master_data:
        titulo = db.obtener_titulo_video(timestamp) or "MASTER"
        archivo = os.path.join(ruta_salida, f"{titulo}_MASTER.wav")
        andres.generar_voz(master_data["guion"], archivo)
        console.print(f"✅ Audio: [cyan]{archivo}[/]")

    db.actualizar_estado_logistica(timestamp, "Voz Generada")


# ============================================================================
# FASE 5: IMPLEMENT (Generación de Video)
# ============================================================================


def fase_implement(id_sesion, auto=False):
    """
    FASE 5 - IMPLEMENT: Generar video animado y ensamblar.

    INPUTS:
        - id_sesion (str): Timestamp
        - auto (bool): Si True, procesa sin confirmación

    OUTPUTS:
        - Clips animados (.mp4)
        - Video final ensamblado
        - Subtítulos sincronizados

    Sub-fases:
        5a. Motion Generation (Meta AI)
        5b. Assembly (Short Assembler)

    Skill: sdd-implement
    Documentación: Docs/MIURA_WORKFLOW_SD.md - Fase 5
    """
    console.print(
        Panel(
            "[bold blue]FASE 5: IMPLEMENT[/]\n[dim]Generando video final...[/]", border_style="blue"
        )
    )

    # 5a. Motion Generation
    console.print("\n[bold]5a. Motion Generation (Meta AI)[/]")

    if not auto:
        motion = console.input("¿Ejecutar Motion Forge? (s/n): ").lower()
        if motion == "s":
            _ejecutar_motion_forge(id_sesion)
    else:
        _ejecutar_motion_forge(id_sesion)

    # 5b. Assembly
    console.print("\n[bold]5b. Assembly[/]")

    if not auto:
        assembly = console.input("¿Ensamblar video final? (s/n): ").lower()
        if assembly == "s":
            _ejecutar_assembly()
    else:
        _ejecutar_assembly()

    console.print(Panel("✅ FASE 5 COMPLETADA", border_style="green"))


def _ejecutar_motion_forge(id_sesion):
    """Ejecuta Motion Forge."""
    from pathlib import Path

    base_dir = Path("output/imagenes_shorts")
    if not base_dir.exists():
        console.print("[yellow]No hay imágenes para animar.[/]")
        return

    # Lógica simplificada - el motor real está en motion_forge_playwright.py
    console.print("[cyan]Delegando a Motion Forge...[/]")
    subprocess.run([sys.executable, "motion_forge/motion_forge_playwright.py", "--cola"])


def _ejecutar_assembly():
    """Ejecuta Short Assembler."""
    from motion_forge.short_assembler import modo_masivo

    modo_masivo()


# ============================================================================
# FASE 6: VERIFY (Auditoría)
# ============================================================================


def fase_verify(id_sesion, auto=False):
    """
    FASE 6 - VERIFY: Auditoría de calidad doctrinal y técnica.

    INPUTS:
        - id_sesion (str): Timestamp
        - auto (bool): Si True, solo registra sin revisión manual

    OUTPUTS:
        - Score de calidad (0-100)
        - Lista de problemas
        - Estado aprobado/rechazado

    Skill: sdd-verify
    Documentación: Docs/MIURA_WORKFLOW_SD.md - Fase 6
    """
    console.print(
        Panel(
            "[bold red]FASE 6: VERIFY[/]\n[dim]Auditando calidad doctrinal...[/]",
            border_style="red",
        )
    )

    if not auto:
        console.print("\n[bold]Checklist de Auditoría:[/]")
        console.print("[ ] No consuela ni humilla")
        console.print("[ ] Revela, diagnostica, ordena")
        console.print("[ ] Ataca autoengaño, no persona")
        console.print("[ ] Estructura 3 fases visible")
        console.print("[ ] CTA memorable")
        console.print("[ ] Sin verbos de duda")
        console.print("[ ] Calidad técnica 1080p")

        input("\nPresiona ENTER para continuar...")

    # Ejecutar auditor automático
    subprocess.run(
        [sys.executable, "auditoria/miura_auditor_bunker.py", "--id", str(id_sesion)], check=False
    )

    console.print(Panel("✅ FASE 6 COMPLETADA", border_style="green"))


# ============================================================================
# FASE 7: SEO (Optimización)
# ============================================================================


def fase_seo(id_sesion, auto=False):
    """
    FASE 7 - SEO: Optimizar metadatos para YouTube.

    INPUTS:
        - id_sesion (str): Timestamp
        - auto (bool): Si True, genera sin confirmación

    OUTPUTS:
        - Título optimizado (< 60 chars)
        - Descripción con timestamps
        - Hashtags (3-5)
        - Tags del video

    Skill: sdd-seo
    Documentación: Docs/MIURA_WORKFLOW_SD.md - Fase 7
    """
    console.print(
        Panel(
            "[bold green]FASE 7: SEO[/]\n[dim]Optimizando metadatos YouTube...[/]",
            border_style="green",
        )
    )

    from tools.youtube_forge import modo_masivo as modo_masivo_yt
    from tools.youtube_forge import leer_doctrina_youtube, get_brain

    doctrina = leer_doctrina_youtube()
    brain = get_brain()

    if doctrina and brain:
        modo_masivo_yt(brain, doctrina, target_id=id_sesion)

    console.print(Panel("✅ FASE 7 COMPLETADA", border_style="green"))


# ============================================================================
# FASE 8: DEPLOY (Publicación)
# ============================================================================


def fase_deploy(id_sesion, auto=False):
    """
    FASE 8 - DEPLOY: Publicar en YouTube como borrador.

    INPUTS:
        - id_sesion (str): Timestamp
        - auto (bool): Si True, sube sin confirmación

    OUTPUTS:
        - Video subido como borrador
        - URL del Studio
        - Estado actualizado en Sheets

    Skill: sdd-deploy
    Documentación: Docs/MIURA_WORKFLOW_SD.md - Fase 8
    """
    console.print(
        Panel(
            "[bold magenta]FASE 8: DEPLOY[/]\n[dim]Publicando en YouTube...[/]",
            border_style="magenta",
        )
    )

    if not auto:
        confirmar = console.input("¿Subir a YouTube? (s/n): ").lower()
        if confirmar != "s":
            console.print("[yellow]Publicación cancelada.[/]")
            return

    subprocess.run([sys.executable, "youtube_publisher/youtube_publisher.py", "--max", "10"])

    console.print(Panel("✅ FASE 8 COMPLETADA", border_style="green"))


# ============================================================================
# FASE 9: ARCHIVE (Memoria)
# ============================================================================


def fase_archive(id_sesion, tema="General"):
    """
    FASE 9 - ARCHIVE: Guardar lecciones y actualizar memoria global.
    """
    console.print(
        Panel("[bold cyan]FASE 9: ARCHIVE[/]\n[dim]Persistiendo memoria en el Búnker e Engram...[/]", border_style="cyan")
    )

    # 1. Crear carpeta de Entrega
    ruta_entrega = os.path.join("output", f"ENTREGA_{id_sesion}")
    os.makedirs(ruta_entrega, exist_ok=True)

    # 2. Recopilar activos
    console.print("📦 [Archive] Empaquetando activos...")
    source_dir = os.path.join("output", f"sesion_{id_sesion}")
    if os.path.exists(source_dir):
        for item in os.listdir(source_dir):
            shutil.copy2(os.path.join(source_dir, item), ruta_entrega)
    
    # 3. Guardar metadatos en memoria persistente
    metáfora = console.input("[yellow]¿Qué metáfora central se usó? [/]")
    leccion = console.input("[yellow]¿Qué lección aprendimos hoy? [/]")
    
    # 4. Actualizar Memoria Global (DB/Sheets)
    from core.database import Database
    db = Database(spreadsheet_name="BD_MiuraForge_Engine")
    if metáfora:
        db.agregar_a_memoria_global([metáfora])

    console.print(f"[bold green]✅ Sesión archivada en:[/] [cyan]{ruta_entrega}[/]")
    console.print(Panel("✅ FASE 9 COMPLETADA", border_style="green"))


def _save_session_state(id_sesion, tema):
    """Guarda el estado de la sesión actual."""
    os.makedirs("output/temp", exist_ok=True)
    with open("output/temp/session_state.json", "w") as f:
        json.dump({"id_sesion": id_sesion, "tema": tema}, f)


def _load_session_state():
    """Carga la última sesión activa."""
    try:
        with open("output/temp/session_state.json", "r") as f:
            return json.load(f)
    except:
        return {"id_sesion": None, "tema": None}


# ============================================================================
# FORJA TOTAL (Pipeline Completo)
# ============================================================================


def forja_total():
    """
    FORJA TOTAL: Ejecutar todas las fases automáticamente.

    Flujo: EXPLORE → PROPOSE → SPEC → DESIGN → IMPLEMENT → VERIFY → SEO

    Nota: DEPLOY y ARCHIVE requieren confirmación manual.
    """
    console.print(
        Panel(
            "[bold red on white]⚔️ FORJA TOTAL ⚔️[/]\n[dim]Pipeline completo activado[/]",
            border_style="red",
        )
    )

    # Fase 1: EXPLORE
    resultado = fase_explore(auto=True)
    if not resultado:
        return
    id_sesion, tema, hallazgos = resultado

    # Fase 2: PROPOSE
    plan, _ = fase_propose(id_sesion, tema, hallazgos, auto=True)
    if not plan:
        return

    # Fase 3: SPEC
    guion, visual, _ = fase_spec(id_sesion, tema, plan, auto=True)

    # Fase 4: DESIGN
    fase_design(id_sesion, guion, visual, auto=True)

    # Fase 5: IMPLEMENT
    fase_implement(id_sesion, auto=True)

    # Fase 6: VERIFY
    fase_verify(id_sesion, auto=True)

    # Fase 7: SEO
    fase_seo(id_sesion, auto=True)

    console.print(
        Panel(
            f"[bold green]✅ FORJA TOTAL COMPLETADA[/]\n\n"
            f"ID: [cyan]{id_sesion}[/]\n"
            f"Tema: [white]{tema}[/]\n\n"
            f"[dim]Video listo para revisión antes de DEPLOY.[/]",
            border_style="green",
        )
    )


# ============================================================================
# HERRAMIENTAS ADICIONALES
# ============================================================================


def menu_herramientas():
    """Menú de herramientas individuales (no SDD)."""
    console.print("\n[bold]⚒️ HERRAMIENTAS ADICIONALES[/]")

    table = Table(border_style="bright_black")
    table.add_column("N°", justify="center")
    table.add_column("Herramienta")
    table.add_column("Descripción", style="dim")

    table.add_row("1", "Motion Forge Manual", "Animar carpeta específica")
    table.add_row("2", "Image Forge", "Generar imágenes con motores")
    table.add_row("3", "Deployer", "Generar paquete de despliegue")
    table.add_row("4", "Auditor Manual", "Revisar guion específico")
    table.add_row("5", "Volver", "Volver al menú principal")

    console.print(table)

    opcion = input("\nSelección: ")

    if opcion == "1":
        # Motion Forge manual
        from motion_forge.motion_forge_playwright import MotionForgePlaywright

        mf = MotionForgePlaywright()
        mf.procesar_cola()
    elif opcion == "2":
        from tools.image_forge import main as image_forge_main

        image_forge_main()
    elif opcion == "3":
        console.print("[cyan]Deployer...[/]")
    elif opcion == "4":
        ts = input("ID de sesión: ")
        subprocess.run([sys.executable, "auditoria/miura_auditor_bunker.py", "--id", ts])


def seleccionar_tema_sheets(db):
    """Permite elegir un cluster de dolor de Sheets."""
    try:
        if not db.clusters:
            try:
                db.clusters = db.sheet.worksheet("CLUSTERS_DOLOR")
            except:
                return None

        records = db.clusters.get_all_records()
        if not records:
            return None

        table = Table(title="💎 CLUSTERS DETECTADOS")
        table.add_column("N°", justify="center")
        table.add_column("Cluster", style="white")
        table.add_column("Frecuencia")

        for i, r in enumerate(records[:10]):
            table.add_row(
                str(i + 1), r.get("nombre_cluster", "N/A").upper(), str(r.get("frecuencia", "0"))
            )

        console.print(table)
        idx = input("\nElija número o 'n' para manual: ")

        if idx.lower() == "n":
            return None

        return records[int(idx) - 1].get("nombre_cluster")
    except:
        return None


# ============================================================================
# MAIN - PUNTO DE ENTRADA
# ============================================================================


def main():
    """Orquestador principal SDD."""
    console.print("\n[bold red]⚔️ MIURA FORGE ENGINE - ORQUESTADOR SDD ⚔️[/]")
    console.print("[dim]Sistema de Producción de Contenido - 9 Fases[/]\n")

    while True:
        opcion = mostrar_menu_orquestador()

        # Fases 1-9
        state = _load_session_state()
        curr_id = state["id_sesion"]
        curr_tema = state["tema"]

        if opcion == "1":
            res = fase_explore()
            if res:
                _save_session_state(res[0], res[1])
        elif opcion == "2":
            id_sesion = curr_id or input("ID de sesión: ")
            tema = curr_tema or input("Tema: ")
            
            from core.database import Database
            db = Database(spreadsheet_name="BD_MiuraForge_Engine")
            hallazgos = db.obtener_investigacion_reciente(tema)
            
            if hallazgos:
                fase_propose(id_sesion, tema, hallazgos)
            else:
                console.print("[yellow]Ejecute FASE 1 primero para obtener hallazgos.[/]")
        elif opcion == "3":
            id_sesion = curr_id or input("ID de sesión: ")
            tema = curr_tema or input("Tema: ")
            
            # Cargar propuesta de Fase 2
            from core.database import Database
            db = Database(spreadsheet_name="BD_MiuraForge_Engine")
            # En modo manual, asumimos que si el Soberano llega aquí, quiere forjar el MASTER
            fase_spec(id_sesion, tema, "Plan manual de contingencia", auto=False)
        elif opcion == "4":
            id_sesion = curr_id or input("ID de sesión: ")
            fase_design(id_sesion, "", "", auto=False)
        elif opcion == "5":
            id_sesion = curr_id or input("ID de sesión: ")
            fase_implement(id_sesion, auto=False)
        elif opcion == "6":
            id_sesion = curr_id or input("ID de sesión: ")
            fase_verify(id_sesion, auto=False)
        elif opcion == "7":
            id_sesion = curr_id or input("ID de sesión: ")
            fase_seo(id_sesion, auto=False)
        elif opcion == "8":
            id_sesion = curr_id or input("ID de sesión: ")
            fase_deploy(id_sesion, auto=False)
        elif opcion == "9":
            id_sesion = curr_id or input("ID de sesión: ")
            tema = curr_tema or "General"
            fase_archive(id_sesion, tema=tema)

        # Modos especiales
        elif opcion == "10":
            forja_total()
        elif opcion == "11":
            menu_herramientas()
        elif opcion == "12":
            console.print("[bold red]Cerrando la forja. Hasta la próxima, Soberano.[/]")
            break
        else:
            console.print("[red]Opción inválida.[/]")


if __name__ == "__main__":
    main()
