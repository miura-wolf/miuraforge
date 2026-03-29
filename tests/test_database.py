import unittest
from unittest.mock import patch, MagicMock
from core.database import Database

class TestDatabase(unittest.TestCase):

    @patch('core.database.ServiceAccountCredentials.from_json_keyfile_name')
    @patch('core.database.gspread.authorize')
    def test_database_init(self, mock_authorize, mock_creds):
        # 🟢 Mockear el cliente de GSheets
        mock_client = MagicMock()
        mock_authorize.return_value = mock_client
        mock_sh = MagicMock()
        mock_client.open.return_value = mock_sh
        
        # Simular worksheets con todos los nombres esperados
        titulos = [
            "LOGISTICA", "PRODUCCION", "MEMORIA", "AUDITORIA", "DESPLIEGUE",
            "TERRITORIOS_DOCTRINALES", "DOLORES_MASCULINOS", "ARSENAL_GANCHOS",
            "FUENTES", "INVESTIGACION_PSICOLOGICA", "CLUSTERS_DOLOR",
            "FRASES_VIRALES", "BLOG_CONTENIDO"
        ]
        mock_sh.worksheets.return_value = [MagicMock(title=t) for t in titulos]

        with patch.object(Database, '_activar_escudo_estructura', return_value=None):
            db = Database()
            self.assertIsNotNone(db.client)
            self.assertIsNotNone(db.blog_contenido)

    @patch('core.database.ServiceAccountCredentials.from_json_keyfile_name')
    @patch('core.database.gspread.authorize')
    def test_escudo_estructura_sync(self, mock_authorize, mock_creds):
        """Verifica que el escudo detecte columnas faltantes y las agregue."""
        mock_client = MagicMock()
        mock_authorize.return_value = mock_client
        mock_sh = MagicMock()
        mock_client.open.return_value = mock_sh
        
        # 1. Crear el mock de la hoja
        mock_ws = MagicMock()
        mock_ws.title = "BLOG_CONTENIDO"
        mock_ws.row_values.return_value = ["ID_Sesion", "Titulo"] # Faltan columnas
        mock_ws.col_count = 10
        
        # 2. Asegurar que Database la encuentre durante el init
        mock_sh.worksheets.return_value = [mock_ws]

        # 3. Instanciar (esto ejecutará el escudo real)
        db = Database()
        
        # 4. Verificaciones
        # El escudo debió llamar a update_cell para ANCLA_VERDAD y LIBRO_ESTADO
        self.assertTrue(mock_ws.update_cell.called)
        # Verificar que se llamó con "ANCLA_VERDAD" (es una de las faltantes)
        args_list = [call.args for call in mock_ws.update_cell.call_args_list]
        headers_actualizados = [arg[2] for arg in args_list]
        self.assertIn("ANCLA_VERDAD", headers_actualizados)
        self.assertIn("LIBRO_ESTADO", headers_actualizados)

if __name__ == '__main__':
    unittest.main()
