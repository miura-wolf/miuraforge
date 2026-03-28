from core.database import Database

if __name__ == "__main__":
    db = Database()
    if db.blog_contenido:
        print("✅ Pestaña BLOG_CONTENIDO verificada y lista para forjar.")
    else:
        print("❌ Error: No se pudo verificar BLOG_CONTENIDO.")
