import csv
import json
import os
import re
import time
from datetime import datetime
from base_conhecimento import BaseConhecimento


class Assistente:
    AVISO = "Aviso: este assistente NÃO é um canal oficial."

    def __init__(self, nome, base):
        self.nome = nome
        self.base = base
        self.historico = []
        self.caminho_historico = "data/historico.json"
        self.caminho_csv = "data/atendimentos.csv"
        self.facilidade = None
        self._inicio_sessao = 0
        self._carregar_historico()

    def _carregar_historico(self):
        try:
            with open(self.caminho_historico, "r", encoding="utf-8") as arquivo:
                dados = json.load(arquivo)
            self.historico = dados if isinstance(dados, list) else []
        except (OSError, json.JSONDecodeError):
            self.historico = []

    @staticmethod
    def contem_dado_pessoal(texto):
        """Bloqueia e-mails e qualquer sequência com 8 ou mais dígitos."""
        if "@" in texto:
            return True
        digitos = re.sub(r"\D", "", texto)
        return len(digitos) >= 8

    @staticmethod
    def _sim_nao(mensagem):
        while True:
            valor = input(mensagem).strip().lower()
            if valor in ("s", "sim"):
                return True
            if valor in ("n", "nao", "não"):
                return False
            print("Entrada inválida. Digite apenas s ou n.")

    @staticmethod
    def _opcao_numerica(mensagem, minimo, maximo):
        while True:
            valor = input(mensagem).strip()
            if valor.isdigit() and minimo <= int(valor) <= maximo:
                return int(valor)
            print(f"Opção inválida. Digite um número entre {minimo} e {maximo}.")

    def registrar(self, origem, pergunta, orientacao, encontrou, ajudou, tentativas, tempo):
        registro = {
            "data": datetime.now().isoformat(timespec="seconds"),
            "origem": origem,
            "pergunta": pergunta,
            "id_orientacao": orientacao.id if orientacao else None,
            "encontrou": bool(encontrou),
            "ajudou": ajudou,
            "tentativas": tentativas,
            "tempo_segundos": round(tempo, 1),
            "facilidade": None,
        }
        self.historico.append(registro)
        os.makedirs(os.path.dirname(self.caminho_historico) or ".", exist_ok=True)
        with open(self.caminho_historico, "w", encoding="utf-8") as arquivo:
            json.dump(self.historico, arquivo, ensure_ascii=False, indent=4)
        self.exportar_csv()

    def exportar_csv(self):
        campos = ["data", "origem", "pergunta", "id_orientacao", "encontrou",
                  "ajudou", "tentativas", "tempo_segundos", "facilidade"]
        os.makedirs(os.path.dirname(self.caminho_csv) or ".", exist_ok=True)
        with open(self.caminho_csv, "w", newline="", encoding="utf-8-sig") as arquivo:
            escritor = csv.DictWriter(arquivo, fieldnames=campos, extrasaction="ignore")
            escritor.writeheader()
            for registro in self.historico:
                escritor.writerow({campo: registro.get(campo) for campo in campos})

    def _mostrar_resultado(self, resultados):
        if not resultados:
            print("\nA base de conhecimento está vazia. Tente novamente mais tarde.")
            return None, 0
        pontos, orientacao = resultados[0]
        if pontos < 3:
            print("\nNão encontrei uma orientação com pontuação suficiente.")
            print("Tente usar outras palavras ou navegue pelas categorias.")
            return None, pontos
        confianca = "ALTA" if pontos >= 6 else "MÉDIA"
        print(f"\nConfiança da resposta: {confianca} ({pontos} pontos)")
        orientacao.exibir()
        alternativas = [(p, o) for p, o in resultados[1:3] if p >= 3]
        if alternativas:
            print("\nOutras orientações que podem ajudar:")
            for p, alternativa in alternativas:
                print(f"- {alternativa.titulo} ({p} pontos)")
        return orientacao, pontos

    def perguntar(self):
        inicio = time.time()
        tentativas = 0
        while True:
            pergunta = input("\nDigite sua dúvida (0 para voltar): ").strip()
            if pergunta == "0":
                return
            if not pergunta:
                print("A pergunta não pode ficar vazia.")
                continue
            if self.contem_dado_pessoal(pergunta):
                print("Atenção: não digite CPF, telefone ou e-mail. Reescreva. A entrada não será registrada.")
                continue
            tentativas += 1
            resultados = self.base.buscar(pergunta)
            orientacao, pontos = self._mostrar_resultado(resultados)
            ajudou = self._sim_nao("\nEssa orientação respondeu sua dúvida? (s/n): ") if orientacao else None
            self.registrar("pergunta", pergunta, orientacao, orientacao is not None,
                           ajudou, tentativas, time.time() - inicio)
            return

    def navegar(self):
        categorias = self.base.categorias()
        if not categorias:
            print("Não há categorias disponíveis.")
            return
        while True:
            print("\n=== CATEGORIAS ===")
            for i, categoria in enumerate(categorias, 1):
                print(f"{i}. {categoria}")
            print("0. Voltar")
            opcao = self._opcao_numerica("Escolha uma categoria: ", 0, len(categorias))
            if opcao == 0:
                return
            categoria = categorias[opcao - 1]
            orientacoes = self.base.por_categoria(categoria)
            while True:
                print(f"\n=== {categoria.upper()} ===")
                for i, orientacao in enumerate(orientacoes, 1):
                    print(f"{i}. {orientacao.titulo}")
                print("0. Voltar")
                escolha = self._opcao_numerica("Escolha uma orientação: ", 0, len(orientacoes))
                if escolha == 0:
                    break
                inicio = time.time()
                orientacao = orientacoes[escolha - 1]
                orientacao.exibir()
                ajudou = self._sim_nao("\nEssa orientação respondeu sua dúvida? (s/n): ")
                self.registrar("categoria", orientacao.titulo, orientacao, True,
                               ajudou, 1, time.time() - inicio)

    def indicadores(self):
        total = len(self.historico)
        if total == 0:
            print("\nAinda não existem atendimentos registrados.")
            return
        encontrados = sum(1 for r in self.historico if r.get("encontrou", False))
        avaliados = [r for r in self.historico if r.get("ajudou") is not None]
        acertos = sum(1 for r in avaliados if r.get("ajudou") is True)
        tempos = [r.get("tempo_segundos", 0) for r in self.historico
                  if isinstance(r.get("tempo_segundos", 0), (int, float))]
        tentativas_lista = [r.get("tentativas", 0) for r in self.historico
                            if isinstance(r.get("tentativas", 0), (int, float))]
        notas = [r.get("facilidade") for r in self.historico
                 if isinstance(r.get("facilidade"), int) and 1 <= r["facilidade"] <= 5]
        print("\n=== INDICADORES ===")
        print(f"Resposta encontrada: {encontrados / total * 100:.1f}%")
        print(f"Taxa de acerto (ajudou): {acertos / len(avaliados) * 100:.1f}%" if avaliados else "Taxa de acerto: sem avaliações")
        print(f"Tempo médio para encontrar: {sum(tempos) / len(tempos):.1f} segundos" if tempos else "Tempo médio: sem dados")
        print(f"Tentativas por atendimento: {sum(tentativas_lista) / len(tentativas_lista):.1f}" if tentativas_lista else "Tentativas: sem dados")
        print(f"Facilidade de uso (1 a 5): {sum(notas) / len(notas):.1f}" if notas else "Facilidade de uso: ainda sem notas")
        sem_solucao = [r.get("pergunta", "(pergunta não informada)") for r in self.historico
                       if not r.get("encontrou", False)]
        print("Dúvidas sem solução:")
        if sem_solucao:
            for duvida in sem_solucao:
                print(f"- {duvida}")
        else:
            print("- Nenhuma registrada.")

    def _avaliar_facilidade(self):
        print("\nAntes de sair, avalie a facilidade de uso de 1 a 5.")
        self.facilidade = self._opcao_numerica("Nota (1 = difícil; 5 = muito fácil): ", 1, 5)
        # Aplica a nota somente aos atendimentos desta sessão, sem alterar sessões antigas.
        for registro in self.historico[self._inicio_sessao:]:
            registro["facilidade"] = self.facilidade
        with open(self.caminho_historico, "w", encoding="utf-8") as arquivo:
            json.dump(self.historico, arquivo, ensure_ascii=False, indent=4)
        self.exportar_csv()

    def executar(self):
        self._inicio_sessao = len(self.historico)
        print(f"\n=== {self.nome} ===")
        print("Orientação para jovens no primeiro emprego.")
        print("Não informe dados pessoais. Este assistente não é canal oficial.")
        while True:
            print("\nMENU PRINCIPAL")
            print("1. Fazer uma pergunta")
            print("2. Navegar por categorias")
            print("3. Ver indicadores")
            print("0. Sair")
            opcao = self._opcao_numerica("Escolha uma opção: ", 0, 3)
            if opcao == 1:
                self.perguntar()
            elif opcao == 2:
                self.navegar()
            elif opcao == 3:
                self.indicadores()
            else:
                self._avaliar_facilidade()
                print("Atendimentos salvos em data/historico.json e data/atendimentos.csv.")
                print("Até mais!")
                break
