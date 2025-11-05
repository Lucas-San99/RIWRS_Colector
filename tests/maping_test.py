# ==============================================================================
# tests/test_mapeamento.py
# Teste unitário para a funcionalidade de mapeamento de DocID para URL.
# ==============================================================================
import unittest
import os
import sys

# Garante que o diretório 'src' está no path para que o SearchEngine possa ser importado
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

# Importa a classe de produção
from SearchEngine import SearchEngine

class TestMapeamentoResultados(unittest.TestCase):
    """Testa a classe SearchEngine, focando no método de mapeamento."""
    
    # 1. Pré-condição: Carregar o mapa uma vez para ser usado em todos os testes
    @classmethod
    def setUpClass(cls):
        """Método executado uma vez antes de todos os testes."""
        # A própria classe SearchEngine fará o carregamento do JSON
        cls.doc_map = SearchEngine.carregar_document_map()
        cls.map_is_loaded = cls.doc_map is not None
        
        if not cls.map_is_loaded:
            print("\nAVISO: document_map.json não carregado. Pulando testes de mapeamento.")

    def setUp(self):
        """Método executado antes de cada teste individual."""
        if not self.map_is_loaded:
            self.skipTest("document_map.json não carregado, pulando o teste.")
            
    # --- Casos de Teste ---

    def test_01_retorna_lista_vazia_se_entrada_vazia(self):
        """Testa se a função retorna [] quando recebe []."""
        resultados = SearchEngine.mapear_resultados_para_urls([])
        self.assertEqual(resultados, [])
        
    def test_02_mapeamento_de_docs_validos(self):
        """Testa se os primeiros 5 DocIDs (que devem existir) são mapeados."""
        # Pega as primeiras 5 chaves válidas do mapa carregado
        doc_ids_validos = list(self.doc_map.keys())[:5]
        self.assertGreaterEqual(len(doc_ids_validos), 5, "O mapa precisa ter pelo menos 5 DocIDs para este teste.")

        resultados = SearchEngine.mapear_resultados_para_urls(doc_ids_validos)
        
        # O resultado deve ter o mesmo tamanho da entrada (todas as URLs devem ter sido encontradas)
        self.assertEqual(len(resultados), len(doc_ids_validos))
        
        # Verifica se o primeiro resultado é uma string (URL)
        self.assertIsInstance(resultados[0], str)
        self.assertTrue(resultados[0].startswith('http')) # URLs devem começar com http

    def test_03_ignora_doc_ids_invalidos(self):
        """Testa se a função ignora DocIDs que não existem no mapa sem falhar."""
        # Pega uma chave válida e mistura com uma inválida
        doc_id_valido = list(self.doc_map.keys())[0]
        doc_ids_para_teste = [doc_id_valido, 999999999, doc_id_valido] # 2 válidos, 1 inválido

        resultados = SearchEngine.mapear_resultados_para_urls(doc_ids_para_teste)
        
        # A lista de resultados deve ter apenas 2 itens (ignorando o inválido)
        self.assertEqual(len(resultados), 2)
        
        # Verifica se a URL mapeada está correta
        url_esperada = self.doc_map.get(doc_id_valido)
        self.assertEqual(resultados[0], url_esperada)


# Bloco de execução do teste
if __name__ == '__main__':
    # Necessário configurar o logging para que o SearchEngine possa logar o carregamento
    try:
        from Logging import setup_logging
        setup_logging()
    except ImportError:
        # Se o logging não for encontrado, usa um logger básico
        pass 
        
    unittest.main()