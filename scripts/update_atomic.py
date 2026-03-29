import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from core.database import Database

def update_atomic_habits():
    db = Database()
    registros = db.blog_contenido.get_all_records()
    headers = db.blog_contenido.row_values(1)
    
    col_estado = headers.index("LIBRO_ESTADO") + 1
    col_cuerpo = headers.index("Cuerpo_Raw") + 1
    col_ancla = headers.index("ANCLA_VERDAD") + 1
    
    ancla_social = '"Me pareció mal escrito, bastante clasista y asume que eres neurotípico. La vibra que me dio fue «¡oye, amigo, simplemente mejora tu vida y todos tus problemas desaparecerán!». Ojalá nunca lo hubiera comprado" — Usuario de Reddit / explodyhead'
    
    briefing = """**DIAGNOSTICO DEL LIBRO**

*Hábitos Atómicos* promete una **fórmula seductoramente simple** para la transformación: que los cambios pequeños del 1% se acumulan de forma exponencial hasta lograr resultados masivos. Vende la idea de que puedes rediseñar tu vida mediante cuatro leyes mecánicas: hacerlo obvio, atractivo, sencillo y satisfactorio. Sin embargo, carece de una **base científica rigurosa**, siendo para muchos investigadores una simplificación excesiva o una recopilación de "derivados de segunda mano" que ignora la complejidad de la conducta humana. El libro está saturado de anécdotas y rellenos que, según críticos, podrían reducirse en un 75% sin perder la esencia. Lo más grave es que carece de herramientas para enfrentar **estados internos profundos** como el trauma, el estrés crónico o la fatiga emocional, asumiendo que el entorno es el único factor determinante.

**EL VACÍO (ADN DOLOROSO)**

Este libro falla en hombres verdaderamente rotos porque **asume una capacidad base de consistencia** que alguien en el abismo no posee. La teoría del "interés compuesto" de los hábitos solo funciona si dejas el dinero en la cuenta; para el hombre perdido, la motivación es variable y dependiente del contexto, no constante. Cuando la "identidad basada en hábitos" choca con la realidad del fracaso, se activa un **botón de vergüenza**: fallar un día no se ve como un simple error, sino como una confirmación de que "no sirves para nada", alimentando una espiral de autodesprecio en lugar de una reconstrucción. El libro promueve lo "fácil", pero el hombre que necesita acero requiere disciplina para enfrentar tareas que son, de hecho, difíciles y dolorosas. Existe un abismo entre "hacerlo sencillo" y la **exigencia brutal** de quien debe forjar su carácter desde las cenizas.

**SOLUCIÓN DE ACERO (PUENTE A MIURA)**

Dentro de la Disciplina del Acero, este libro no es el plano maestro, sino un **bloque lego menor** útil solo por sus tácticas de "carpintería" conductual:
*   **Diseño de Entorno:** Utilizar el "scaffolding" (andamios) externos para que el ambiente cargue con el peso que la voluntad aún no puede sostener.
*   **Apilamiento de Hábitos:** Usar disparadores visuales y rutinas existentes para insertar pequeñas victorias.
*   **La Regla de los Dos Minutos:** Como una forma de vencer la inercia inicial y simplemente "aparecer".

Sin embargo, **la estructura la da el Acero**: la identidad no debe basarse en la perfección de una rutina, sino en la **persistencia de un experimentador** que sabe que fallará y tiene el sistema para regresar. La verdadera transformación nace del **esfuerzo consciente**, no de trucos de productividad."""

    for i, r in enumerate(registros):
        if "Atomic Habits" in str(r.get("Título", "")):
            row_idx = i + 2
            db.blog_contenido.update_cell(row_idx, col_cuerpo, briefing)
            db.blog_contenido.update_cell(row_idx, col_ancla, ancla_social)
            db.blog_contenido.update_cell(row_idx, col_estado, "ancla_lista")
            print(f"✅ Fila de Atomic Habits actualizada (Fila {row_idx})")
            return

if __name__ == "__main__":
    update_atomic_habits()
