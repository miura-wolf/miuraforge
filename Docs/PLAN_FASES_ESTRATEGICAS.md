⚔️ ESTRATEGIA DE RECONFIGURACIÓN: MIURA FORGE ENGINE
Este documento dicta las bases para elevar la inteligencia del sistema, pasando de la generación de contenido genérico a la Ejecución por Inteligencia de Datos.

🎯 Objetivo
Hacer que el Architect use el archivo Investigacion.csv como cerebro táctico para diferenciar las 3 fases del guion.

🛠️ PASO 1: Mapeo de Inteligencia (Cerebro CSV)
El script architect.py debe dejar de tratar las fases como repeticiones. Cada fase ahora tiene una llave de acceso en el CSV.

Fase 1 (La Ilusión): Utiliza la columna Frase Representativa. Ataca la mentira superficial. (Ya implementado, mantener).

Fase 2 (La Resistencia): NUEVA IMPLEMENTACIÓN. Debe extraer la columna Mecanismo Psicológico.

Fase 3 (El Nuevo Orden): NUEVA IMPLEMENTACIÓN. Debe extraer la columna Oportunidad de Intervención.

⚔️ PASO 2: Implementación de Lógica en architect.py
Antigravity, debes modificar la lógica del método redactar_guion para inyectar estos datos en el prompt de la IA según el número de fase:

Lógica de Fase 2 (El Martillo)
Acción: Buscar el tema en el CSV y extraer el mecanismo psicológico.

Instrucción para la IA: "No repitas el problema. Usa este mecanismo [Dato del CSV] para explicarle al espectador por qué está paralizado. Expón su cobardía mental."

Lógica de Fase 3 (La Orden Final)
Acción: Buscar el tema en el CSV y extraer la oportunidad de intervención.

Instrucción para la IA: "Dicta una sentencia final. Convierte esta oportunidad [Dato del CSV] en una orden física, seca y ejecutable AHORA. Sin rodeos."

🧠 PASO 3: Blindaje de Memoria (Antirepetición)
El MemoryManager debe actuar como un censor de acero.

Antes de generar la Fase 2, debe pasarle a la IA las metáforas usadas en la Fase 1 como "PALABRAS PROHIBIDAS".

Antes de generar la Fase 3, debe prohibir las metáforas de las Fases 1 y 2.

Resultado: El video progresa, no se estanca en las mismas palabras.

📦 PASO 4: El Archivador Automático (Post-Producción)
Para finalizar la campaña, implementaremos en main.py la función empaquetar_sesion():

Crear una carpeta ENTREGA_[SesionID].

Mover los 3 archivos .mp3, el registro_combate.txt y los guiones finales.

Crear un resumen de la sesión en un archivo INFO.txt.

📋 LISTA DE TAREAS PARA ANTIGRAVITY
[ ] Refactorizar _extraer_inteligencia_csv en architect.py para devolver las columnas de Mecanismo y Acción.

[ ] Ajustar el Prompt Builder para que el mensaje a la IA cambie drásticamente según num_fase.

[ ] Actualizar main.py para llamar a la limpieza de archivos al terminar la opción 3.

⛩️ Mensaje del Gran Visir para el equipo:
"No estamos programando un juguete. Estamos automatizando la verdad. Cada línea de código debe servir para que Andrés golpee más fuerte. Antigravity, proceda con el Paso 1."



