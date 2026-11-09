# Review Copilot

Agente de IA que lê avaliações de restaurantes, identifica os problemas mais frequentes de cada um e recomenda uma ação concreta. Um fluxo em n8n alerta o time quando chega uma avaliação crítica.

Projeto de portfólio para a trilha **AI Builder**: usar IA como alavanca para resolver um problema de negócio de ponta a ponta, sem backend próprio.

## Sumário
- [O problema](#o-problema)
- [A solução](#a-solução)
- [Arquitetura](#arquitetura)
- [Requisitos da vaga atendidos](#requisitos-da-vaga-atendidos)
- [Stack](#stack)
- [Estrutura do repositório](#estrutura-do-repositório)
- [Como rodar](#como-rodar)
- [Decisões técnicas](#decisões-técnicas)
- [Exemplo de resultado](#exemplo-de-resultado)
- [Limitações](#limitações)
- [Próximos passos](#próximos-passos)
- [Autora](#autora)

## O problema
Restaurantes parceiros recebem centenas de avaliações. Ninguém lê todas, e os padrões ficam escondidos: um restaurante que atrasa sempre, outro que esquece itens. A nota cai e o cliente deixa de pedir.

## A solução
1. O agente classifica cada avaliação por **tema** (atraso, item faltando, embalagem, sabor, preço, atendimento, entrega) e **sentimento**.
2. Agrega os resultados por restaurante e lista os três principais problemas, com a **ação recomendada** para cada um.
3. Um dashboard mostra nota média, tendência mensal e o plano de ação por restaurante.
4. Um workflow n8n classifica avaliações novas em tempo real e envia alerta quando a urgência é alta.

## Arquitetura
```
Lote (batch)
reviews.csv ──► agent/analyze.py ──► dashboard/data.js ──► dashboard/index.html
                 │ Claude API (lotes de 40)
                 └ fallback por regras se a API falhar ou não houver chave

Tempo real
nova avaliação ──► Webhook n8n ──► Claude (tema, urgência, resposta sugerida)
                                      ├─ urgência alta ──► alerta no Slack
                                      └─ demais ─────────► registro no Google Sheets
```

## Requisitos da vaga atendidos
| Requisito | Onde está |
|---|---|
| Prompt engineering avançado | [`prompts/classify.md`](prompts/classify.md): saída em JSON, lista fechada de temas, instrução para ignorar comandos escondidos no texto das avaliações |
| Orquestração de agentes (Claude) | [`agent/analyze.py`](agent/analyze.py): processamento em lotes, parsing de JSON, fallback automático |
| Automação com n8n | [`n8n/workflow.json`](n8n/workflow.json): webhook, Claude, condição, Slack e Sheets |
| APIs sem backend profundo | O webhook do n8n funciona como API de entrada |
| Análise de dados com IA | Temas por restaurante, tendência mensal e percentual de avaliações negativas |
| Ferramentas de vibe coding | Dashboard em HTML estático, sem build |

## Stack
Python 3.10+, Claude API (Anthropic SDK), n8n, HTML/CSS/JS puro.

## Estrutura do repositório
```
ifood-review-copilot/
├── agent/analyze.py        # classificação, agregação e plano de ação
├── data/generate_data.py   # gera 600 avaliações sintéticas
├── dashboard/index.html    # dashboard estático
├── n8n/workflow.json       # fluxo para importar no n8n
├── prompts/classify.md     # prompt de classificação
├── requirements.txt
└── LICENSE
```

## Como rodar
```bash
git clone https://github.com/GiuColucci/ifood-review-copilot.git
cd ifood-review-copilot
python data/generate_data.py     # cria data/reviews.csv
python agent/analyze.py          # modo offline (regras), cria dashboard/data.js
```
Abra `dashboard/index.html` no navegador.

**Modo Claude (opcional):**
```bash
pip install -r requirements.txt
```
Defina a chave e rode de novo:
- Linux/Mac: `export ANTHROPIC_API_KEY=sua-chave`
- PowerShell: `$env:ANTHROPIC_API_KEY="sua-chave"`

```bash
python agent/analyze.py
```
O rodapé do dashboard indica qual modo gerou os dados. O modelo pode ser trocado com a variável `MODEL`.

**Workflow n8n:** importe `n8n/workflow.json`, configure as credenciais do Anthropic, Slack e Google Sheets e envie um POST ao webhook com `restaurante`, `nota` e `texto`.

## Decisões técnicas
- **Fallback por regras:** o projeto roda sem chave de API, então qualquer pessoa consegue reproduzir o resultado. Também protege o pipeline contra falha da API.
- **Taxonomia fechada de temas:** permite agregar e comparar restaurantes. Temas livres gerariam centenas de rótulos diferentes.
- **Lotes de 40 avaliações:** reduz o número de chamadas e mantém a resposta curta o bastante para o parsing de JSON.
- **Dashboard estático:** sem servidor nem build, qualquer pessoa abre o arquivo e pode hospedá-lo em qualquer lugar.
- **n8n para o tempo real:** evita escrever e manter um backend para um fluxo de três passos.

## Exemplo de resultado
Com o dataset sintético, o agente aponta sozinho o ponto fraco de cada restaurante. Por exemplo, o Burger do Zé tem **atraso** como principal problema (26 menções) e a ação sugerida é revisar o raio de entrega e o tempo de preparo nos horários de pico e ativar aviso proativo de atraso.

## Limitações
- Os dados são sintéticos.
- A qualidade da classificação ainda não foi medida contra avaliações rotuladas manualmente.
- O fallback por regras é simples de propósito e só cobre as frases do dataset de exemplo.
- O workflow n8n não foi executado com credenciais reais.

## Próximos passos
- Medir acurácia: comparar Claude e regras contra avaliações rotuladas à mão.
- Resposta automática ao cliente com aprovação humana.
- Dados reais via Google Sheets e dashboard hospedado.

## Autora
Giulia Colucci · [GitHub](https://github.com/GiuColucci)

Licença: [MIT](LICENSE)
