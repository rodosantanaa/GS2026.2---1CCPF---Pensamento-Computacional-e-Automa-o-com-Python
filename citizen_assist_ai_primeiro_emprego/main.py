import os
from base_conhecimento import BaseConhecimento
from assistente import Assistente

def main():
    os.makedirs("data", exist_ok=True)
    base = BaseConhecimento("data/base_conhecimento.json")
    base.carregar()
    assistente = Assistente("Citizen Assist AI – Primeiro Emprego", base)
    assistente.executar()

if __name__ == "__main__":
    main()
