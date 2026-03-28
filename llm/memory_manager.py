import json
import os
import datetime

class MemoryManager:
    def __init__(self, file_path="output/metaphor_memory.json", db=None):
        self.file_path = file_path
        self.db = db
        self.memory = self.load_memory()

    def load_memory(self):
        """Carga el historial de metáforas, priorizando Sheets si hay DB."""
        local_data = {"recent_metaphors": [], "recent_banned_words_visual": ["epic", "cinematic"]}
        
        if os.path.exists(self.file_path):
            try:
                with open(self.file_path, 'r', encoding='utf-8') as f:
                    local_data = json.load(f)
            except: pass

        if self.db:
            try:
                global_metaphors = self.db.obtener_memoria_global()
                if global_metaphors:
                    # Mezclar local y global
                    combined = list(set(local_data.get("recent_metaphors", []) + global_metaphors))
                    local_data["recent_metaphors"] = combined
            except Exception as e:
                print(f"⚠️ [Memory] Error sincronizando con Sheets: {e}")
        
        return local_data

    def save_memory(self, data):
        os.makedirs(os.path.dirname(self.file_path), exist_ok=True)
        with open(self.file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        self.memory = data

    def get_banned_str(self, additional_global=None):
        """Devuelve las metáforas prohibidas."""
        # Recargar para asegurar frescura si hay DB
        if self.db: self.memory = self.load_memory()
        
        local_banned = self.memory.get("recent_metaphors", [])
        if additional_global:
            combined = list(set(local_banned + additional_global))
            return ", ".join(combined)
        return ", ".join(local_banned)

    def update_metaphors(self, new_metaphors):
        """Añade las metáforas usadas al registro local y global."""
        data = self.load_memory()
        current = data.get("recent_metaphors", [])
        updated = list(set(new_metaphors + current))
        data["recent_metaphors"] = updated[-25:] # Expandimos un poco el historial
        data["last_updated"] = datetime.datetime.now().isoformat()
        self.save_memory(data)
        
        if self.db:
            try:
                self.db.agregar_a_memoria_global(new_metaphors)
            except: pass