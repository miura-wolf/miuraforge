import unittest
from unittest.mock import patch, MagicMock
from core.blog_alchemist import invocar_blog_alchemist

class TestBlogAlchemist(unittest.TestCase):

    @patch('core.blog_alchemist.LLMFactory.get_brain')
    def test_invocar_blog_alchemist_success(self, mock_get_brain):
        # Configurar Mock del cerebro
        mock_brain = MagicMock()
        mock_brain.generate.return_value = "Contenido transformado con Voz del Soberano"
        mock_get_brain.return_value = mock_brain

        titulo = "Libro de Prueba"
        cuerpo = "Este es un cuerpo de prueba"
        ancla = "Mi ancla de verdad intacta"
        amazon = "https://amazon.com/prueba"

        resultado = invocar_blog_alchemist(titulo, cuerpo, ancla, amazon)

        self.assertIn("Contenido transformado", resultado)
        mock_get_brain.assert_called_with("research") # Blog Alchemist usa 'research' (DeepSeek)
        mock_brain.generate.assert_called_once()
        
        # Verificar que el prompt enviado contiene el ancla
        args, kwargs = mock_brain.generate.call_args
        prompt_sent = args[0]
        self.assertIn(ancla, prompt_sent)
        self.assertIn(amazon, prompt_sent)

    def test_invocar_blog_alchemist_fallback(self):
        # Probar que si falla el LLM, devuelve el cuerpo original (Resiliencia)
        with patch('core.blog_alchemist.LLMFactory.get_brain', side_effect=Exception("API Down")):
            titulo = "Libro de Prueba"
            cuerpo = "Este es un cuerpo de prueba"
            resultado = invocar_blog_alchemist(titulo, cuerpo)
            self.assertEqual(resultado, cuerpo)

if __name__ == '__main__':
    unittest.main()
