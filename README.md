# Citizen Assist AI – Primeiro Emprego

## Público e problema
Jovens que estão buscando o primeiro emprego ou iniciando a vida profissional. O projeto organiza orientações básicas sobre documentação, direitos trabalhistas e serviços públicos de emprego em linguagem simples.

## ODS relacionados
- **ODS 4 – Educação de qualidade:** apoio ao acesso a informações para a formação e inserção profissional.
- **ODS 8 – Trabalho decente e crescimento econômico:** orientação inicial sobre trabalho, aprendizagem e direitos.
- **ODS 10 – Redução das desigualdades:** facilita o acesso a informações públicas.

## Como executar
Requer Python 3.10 ou superior. Não utiliza bibliotecas externas.

No terminal, dentro da pasta do projeto:
```bash
python main.py
```

## Classes e composição
- `Orientacao`: guarda os campos de um registro JSON e apresenta a orientação.
- `BaseConhecimento`: carrega o JSON, lista categorias, filtra por categoria, normaliza texto, pontua e ordena resultados.
- `Assistente`: conduz o atendimento, navega, registra o histórico, calcula indicadores e exporta CSV.
- Composição: `Assistente` possui uma `BaseConhecimento`, que contém uma lista de objetos `Orientacao`.

## Regra de pontuação
- Cada palavra-chave encontrada na pergunta: **+3 pontos**.
- Cada palavra da pergunta com 4 letras ou mais encontrada no título: **+1 ponto**.
- 6 pontos ou mais: confiança **ALTA**.
- De 3 a 5 pontos: confiança **MÉDIA**.
- Menos de 3 pontos: orientação não encontrada.
- São exibidas até duas alternativas com pelo menos 3 pontos.
- A normalização remove acentos, pontuação e diferenças entre maiúsculas/minúsculas.

## Segurança e transparência
O assistente não solicita nome, CPF, telefone ou e-mail. Perguntas contendo `@` ou sequência de 8 ou mais dígitos são recusadas e não são registradas. Todas as orientações mostram fonte, data de verificação e o aviso de que o assistente não é canal oficial. O sistema não substitui atendimento jurídico, trabalhista ou governamental.

## Base de conhecimento e fontes
A base independente `data/base_conhecimento.json` contém 12 orientações em três categorias. As informações foram conferidas em 18/11/2026 nas fontes oficiais indicadas em cada registro, incluindo gov.br, Ministério do Trabalho e Emprego, TSE, INSS e Caixa. Como regras e serviços podem mudar, consulte sempre a página oficial antes de tomar decisões.

## Histórico, indicadores e CSV
Cada atendimento é registrado em `data/historico.json` com data, origem, pergunta, ID da orientação, resultado, avaliação de ajuda, tentativas e tempo. O CSV `data/atendimentos.csv` é gerado com `csv.DictWriter`. Ao sair, o programa solicita nota de facilidade de 1 a 5. O menu apresenta percentual de respostas encontradas, taxa de ajuda, tempo médio, tentativas, facilidade e dúvidas sem solução.

## Teste com usuários

### Cenário simulado
Foram considerados 3 participantes, representando jovens em busca do primeiro emprego, que realizaram 12 atendimentos simulados.

| Indicador | Resultado |
|---|---:|
| Participantes | 3 |
| Total de atendimentos | 12 |
| Respostas encontradas | 10 de 12 (83,3%) |
| Taxa de ajuda entre as respostas encontradas | 8 de 10 (80,0%) |
| Tempo médio para encontrar orientação | 18,4 segundos |
| Tentativas médias por atendimento | 1,2 |
| Facilidade média de uso | 4,3 de 5 |
| Dúvidas sem solução | 2 |

### Dúvidas que não foram solucionadas na simulação
- Como faço para conseguir estágio sem experiência?
- A empresa pode exigir experiência para uma vaga de jovem aprendiz?

### Melhoria após o teste
Durante os testes, uma pergunta sobre o primeiro registro profissional não foi localizada. Como melhoria proposta, adicionar a expressão **“primeiro registro”** às palavras-chave da orientação sobre Carteira de Trabalho Digital em `data/base_conhecimento.json`. A equipe deve validar essa alteração durante o teste real e demonstrá-la no vídeo técnico.

Os dados da simulação estão separados em `data/relatorio_teste_simulado.json`. Eles não foram inseridos em `historico.json` nem em `atendimentos.csv`, evitando misturar dados fictícios com atendimentos efetivamente realizados.


## Limitações
- A busca é baseada em regras e palavras, não em um modelo de IA generativa.
- O sistema só responde ao conteúdo do JSON; não consulta a internet durante o atendimento.
- A pontuação pode não compreender sinônimos ou perguntas muito diferentes das palavras-chave cadastradas.
- O conteúdo não substitui orientação oficial individualizada.
- A equipe deve revisar as datas e fontes antes da apresentação.

## Integração com outras disciplinas
Não há integração com APIs ou modelos externos. A busca por regras é a funcionalidade obrigatória e central desta entrega.
