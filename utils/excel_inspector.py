import pandas as pd
import os
import sys

def inspeccionar_excel(file_path):
    """
    Inspecciona un archivo Excel y muestra un resumen de su contenido.
    """
    if not os.path.exists(file_path):
        print(f"❌ Error: El archivo no existe en {file_path}")
        return

    print(f"\n{'='*50}")
    print(f"🔍 INSPECTOR MIURA: {os.path.basename(file_path)}")
    print(f"{'='*50}")

    try:
        xl = pd.ExcelFile(file_path)
        print(f"📦 Hojas detectadas: {', '.join(xl.sheet_names)}")
        
        for sheet in xl.sheet_names:
            df = pd.read_excel(file_path, sheet_name=sheet)
            print(f"\n--- 📑 Hoja: {sheet} | Filas: {len(df)} | Columnas: {len(df.columns)} ---")
            
            if df.empty:
                print("    (Hoja vacía)")
                continue

            # Mostrar columnas
            print(f"    Columnas: {list(df.columns)}")
            
            # Mostrar muestra de datos (máximo 5 filas)
            print("\n    Muestra de datos:")
            # Ajustar pandas para mostrar bien en consola
            pd.set_option('display.max_colwidth', 50)
            print(df.head(5).to_string(index=False))
            print("-" * 30)

    except Exception as e:
        print(f"❌ Error al procesar el Excel: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        inspeccionar_excel(sys.argv[1])
    else:
        print("💡 Uso: python utils/excel_inspector.py \"ruta/al/archivo.xlsx\"")
