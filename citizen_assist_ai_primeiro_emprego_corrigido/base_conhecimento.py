import json
import re
import unicodedata
from orientacao import Orientacao


class BaseConhecimento:
    CAMPOS_OBRIGATORIOS = {
        "id", "categoria", "titulo", "palavras_chave", "resposta",
        "documentos", "onde", "fonte", "verificado_em"
    }

    def __init__(self, caminho):
        self.caminho = caminho
        self.orientacoes = []

    @staticmethod
    def normalizar(texto):
        texto = unicodedata.normalize("NFD", str(texto).lower().strip())
        texto = "".join(c for c in texto if unicodedata.category(c) != "Mn")
        texto = re.sub(r"[^a-z0-9]+", " ", texto)
        return " " + " ".join(texto.split()) + " "

    def carregar(self):
        try:
            with open(self.caminho, "r", encoding="utf-8") as arquivo:
                dados = json.load(arquivo)
            if not isinstance(dados, list):
                raise ValueError("A raiz do JSON precisa ser uma lista.")
            novas = []
            for numero, item in enumerate(dados, 1):
                if not isinstance(item, dict) or not self.CAMPOS_OBRIGATORIOS.issubset(item):
                    raise ValueError(f"Registro {numero}: existem campos obrigatórios ausentes.")
                if not isinstance(item["palavras_chave"], list) or len(item["palavras_chave"]) < 3:
                    raise ValueError(f"Registro {numero}: são necessárias pelo menos 3 palavras-chave.")
                if not all(isinstance(item[campo], str) and item[campo].strip()
                           for campo in ("categoria", "titulo", "resposta", "onde", "fonte", "verificado_em")):
                    raise ValueError(f"Registro {numero}: há campo textual vazio ou inválido.")
                if not all(isinstance(chave, str) and chave.strip() for chave in item["palavras_chave"]):
                    raise ValueError(f"Registro {numero}: palavra-chave inválida.")
                if not isinstance(item["documentos"], list) or not all(isinstance(x, str) for x in item["documentos"]):
                    raise ValueError(f"Registro {numero}: documentos deve ser uma lista de textos.")
                novas.append(Orientacao(item))
            self.orientacoes = novas
            return True
        except (OSError, json.JSONDecodeError, ValueError, TypeError, KeyError) as erro:
            self.orientacoes = []
            print(f"Aviso: não foi possível carregar a base de conhecimento: {erro}")
            print("O programa continuará funcionando, mas sem orientações até corrigir o JSON.")
            return False

    def categorias(self):
        return sorted({o.categoria for o in self.orientacoes})

    def por_categoria(self, categoria):
        return [o for o in self.orientacoes if o.categoria == categoria]

    def pontuar(self, pergunta, orientacao):
        pergunta_n = self.normalizar(pergunta)
        pontos = 0
        for chave in orientacao.palavras_chave:
            chave_n = self.normalizar(chave).strip()
            if chave_n and f" {chave_n} " in pergunta_n:
                pontos += 3
        palavras = set(pergunta_n.split())
        titulo = self.normalizar(orientacao.titulo)
        for palavra in palavras:
            if len(palavra) >= 4 and f" {palavra} " in titulo:
                pontos += 1
        return pontos

    def buscar(self, pergunta):
        resultados = [(self.pontuar(pergunta, orientacao), orientacao)
                      for orientacao in self.orientacoes]
        resultados.sort(key=lambda item: item[0], reverse=True)
        return resultados
