import unittest
from unittest.mock import patch, MagicMock
from core.blog_visualizer import crear_visual_blog

class TestBlogVisualizer(unittest.TestCase):

    @patch('core.blog_visualizer.LLMFactory.get_brain')
    @patch('core.blog_visualizer.forjar_imagen_blog')
    @patch('core.blog_visualizer.Path.mkdir')
    def test_crear_visual_blog_success(self, mock_mkdir, mock_forjar, mock_get_brain):
        # 🟢 Configurar Mocks
        mock_brain = MagicMock()
        mock_brain.generate.return_value = "Prompt cinematográfico forjado"
        mock_get_brain.return_value = mock_brain
        
        # Simular éxito en la forja de imagen
        mock_forjar.return_value = True

        titulo = "Libro de Prueba"
        resumen = "Resumen de prueba"
        slug = "slug-de-prueba"

        resultado = crear_visual_blog(titulo, resumen, slug)

        # 🎯 Verificaciones
        self.assertEqual(resultado, f"/images/blog/{slug}/hero.png")
        mock_get_brain.assert_called_with("merch") # Visualizer usa 'merch' (Gemma 3)
        mock_forjar.assert_called_once()
        
        # Verificar que el prompt enviado al diseñador visual contiene el título
        args, _ = mock_brain.generate.call_args
        self.assertIn(titulo, args[0])

    @patch('core.blog_visualizer.LLMFactory.get_brain')
    @patch('core.blog_visualizer.forjar_imagen_blog')
    def test_crear_visual_blog_fail(self, mock_forjar, mock_get_brain):
        # 🔴 Configurar falla en la generación
        mock_brain = MagicMock()
        mock_brain.generate.return_value = "Prompt forjado"
        mock_get_brain.return_value = mock_brain
        
        # Simular fallo en todos los motores
        mock_forjar.return_value = False

        resultado = crear_visual_blog("Test", "Resumen", "fail-slug")

        self.assertEqual(resultado, "")
        mock_forjar.assert_called_once()

if __name__ == '__main__':
    unittest.main()
