"""Testes automatizados do Citizen Assist AI. Execute: python -m unittest -v testes.py"""
import csv
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from assistente import Assistente
from base_conhecimento import BaseConhecimento


ROOT = Path(__file__).resolve().parent


class TestCitizenAssistAI(unittest.TestCase):
    def setUp(self):
        self.base = BaseConhecimento(str(ROOT / "data" / "base_conhecimento.json"))
        self.assertTrue(self.base.carregar())

    def test_base_tem_minimo_de_orientacoes_e_categorias(self):
        self.assertGreaterEqual(len(self.base.orientacoes), 10)
        self.assertGreaterEqual(len(self.base.categorias()), 3)
        for orientacao in self.base.orientacoes:
            self.assertGreaterEqual(len(orientacao.palavras_chave), 3)

    def test_normalizacao_remove_acentos_e_pontuacao(self):
        self.assertEqual(self.base.normalizar("  TÍTULO, do CPF! "), " titulo do cpf ")

    def test_busca_carteira_trabalho_alta_confianca(self):
        resultados = self.base.buscar("Como acessar a Carteira de Trabalho Digital?")
        self.assertGreaterEqual(resultados[0][0], 6)
        self.assertIn("Carteira de Trabalho Digital", resultados[0][1].titulo)

    def test_busca_fgts(self):
        resultados = self.base.buscar("Como consultar meu FGTS?")
        self.assertGreaterEqual(resultados[0][0], 3)
        self.assertIn("FGTS", resultados[0][1].titulo)

    def test_bloqueio_dados_pessoais(self):
        self.assertTrue(Assistente.contem_dado_pessoal("Meu CPF 123.456.789-00"))
        self.assertTrue(Assistente.contem_dado_pessoal("meu email teste@exemplo.com"))
        self.assertTrue(Assistente.contem_dado_pessoal("telefone 11987654321"))
        self.assertFalse(Assistente.contem_dado_pessoal("Como conseguir primeiro emprego?"))
        self.assertFalse(Assistente.contem_dado_pessoal("Quero consultar FGTS"))

    def test_json_corrompido_nao_quebra_carregamento(self):
        with tempfile.TemporaryDirectory() as pasta:
            arquivo = Path(pasta) / "ruim.json"
            arquivo.write_text("{json inválido", encoding="utf-8")
            base = BaseConhecimento(str(arquivo))
            self.assertFalse(base.carregar())
            self.assertEqual(base.orientacoes, [])

    def test_registro_e_exportacao_csv(self):
        with tempfile.TemporaryDirectory() as pasta:
            assistente = Assistente("Teste", self.base)
            assistente.caminho_historico = str(Path(pasta) / "historico.json")
            assistente.caminho_csv = str(Path(pasta) / "atendimentos.csv")
            orientacao = self.base.orientacoes[0]
            assistente.registrar("pergunta", "pergunta de teste", orientacao, True, True, 1, 2.5)
            dados = json.loads(Path(assistente.caminho_historico).read_text(encoding="utf-8"))
            self.assertEqual(len(dados), 1)
            with open(assistente.caminho_csv, newline="", encoding="utf-8-sig") as arquivo:
                linhas = list(csv.DictReader(arquivo))
            self.assertEqual(len(linhas), 1)
            self.assertEqual(linhas[0]["pergunta"], "pergunta de teste")

    def test_pergunta_bloqueada_nao_e_registrada(self):
        with tempfile.TemporaryDirectory() as pasta:
            assistente = Assistente("Teste", self.base)
            assistente.caminho_historico = str(Path(pasta) / "historico.json")
            assistente.caminho_csv = str(Path(pasta) / "atendimentos.csv")
            with patch("builtins.input", side_effect=["meu cpf 12345678900", "0"]):
                assistente.perguntar()
            self.assertEqual(assistente.historico, [])

    def test_pergunta_valida_e_nota_de_facilidade(self):
        with tempfile.TemporaryDirectory() as pasta:
            assistente = Assistente("Teste", self.base)
            assistente.caminho_historico = str(Path(pasta) / "historico.json")
            assistente.caminho_csv = str(Path(pasta) / "atendimentos.csv")
            with patch("builtins.input", side_effect=["Como acessar carteira de trabalho digital?", "s"]):
                assistente.perguntar()
            self.assertEqual(len(assistente.historico), 1)
            self.assertTrue(assistente.historico[0]["encontrou"])
            self.assertIsNone(assistente.historico[0]["facilidade"])
            assistente._inicio_sessao = 0
            with patch("builtins.input", side_effect=["5"]):
                assistente._avaliar_facilidade()
            self.assertEqual(assistente.historico[0]["facilidade"], 5)

    def test_nota_nova_nao_altera_atendimentos_antigos(self):
        with tempfile.TemporaryDirectory() as pasta:
            assistente = Assistente("Teste", self.base)
            assistente.caminho_historico = str(Path(pasta) / "historico.json")
            assistente.caminho_csv = str(Path(pasta) / "atendimentos.csv")
            assistente.historico = [{"data": "anterior", "facilidade": 3}]
            assistente._inicio_sessao = 1
            assistente.registrar("pergunta", "nova", self.base.orientacoes[0], True, True, 1, 1)
            with patch("builtins.input", side_effect=["4"]):
                assistente._avaliar_facilidade()
            self.assertEqual(assistente.historico[0]["facilidade"], 3)
            self.assertEqual(assistente.historico[1]["facilidade"], 4)


if __name__ == "__main__":
    unittest.main(verbosity=2)
