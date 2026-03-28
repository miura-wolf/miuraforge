import json
import os

notebook_path = r"d:\YT\MiuraForge\Docs\Wan2.1_Miura_Renderer.ipynb"

with open(notebook_path, "r", encoding="utf-8") as f:
    nb = json.load(f)

for cell in nb.get("cells", []):
    if cell.get("cell_type") == "code":
        sources = cell.get("source", [])
        for i, line in enumerate(sources):
            if "!pip install -q diffusers" in line:
                sources[i] = line.replace("!pip install -q diffusers", "!pip install -q git+https://github.com/huggingface/diffusers.git")

with open(notebook_path, "w", encoding="utf-8") as f:
    json.dump(nb, f, indent=2, ensure_ascii=False)

print("✅ Notebook corregido exitosamente para descargar Diffusers desde GitHub.")
