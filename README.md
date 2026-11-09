# 🍔 Review Copilot — de avaliações soltas a plano de ação em minutos

> Projeto de portfólio para a trilha **AI Builder**: IA como alavanca para resolver um problema real de negócio, de ponta a ponta, sem backend pesado.

## O problema
Restaurantes parceiros recebem centenas de avaliações por mês. Ninguém lê tudo, e o padrão
("o *Burger do Zé* atrasa sempre", "o *Sushi Kenzo* esquece itens") fica escondido. Resultado: nota cai, cliente some.

## A solução
Um agente que **lê, classifica e prioriza** avaliações e entrega, por restaurante, os principais problemas com **ação recomendada**. Mais um fluxo em tempo real que alerta o time quando chega uma avaliação crítica.

```
reviews.csv ──► agent/analyze.py ──► dashboard/data.js ──► dashboard/index.html
                (Claude + fallback)                         (HTML estático, deploy em 1 clique)

nova avaliação ──► n8n webhook ──► Claude (urgência + resposta sugerida) ──► Slack / Google Sheets
```

## O que demonstra (alinhado à vaga)
| Requisito da vaga | Onde está |
|---|---|
| Prompt engineering avançado | [`prompts/classify.md`](prompts/classify.md): saída estruturada, taxonomia fechada, defesa contra prompt injection vinda do texto da avaliação |
| Orquestração de agentes (Claude) | `agent/analyze.py`: processamento em lotes, parsing de JSON e fallback automático se a API falhar |
| Automação n8n/Make/Zapier | [`n8n/workflow.json`](n8n/workflow.json): webhook → Claude → condição → Slack/Sheets (importe direto no n8n) |
| API sem backend profundo | Webhook do n8n vira a "API" de entrada, sem servidor próprio |
| Análise de dados com IA | KPIs, tendência mensal e temas por restaurante |
| Entrega rápida / vibe coding | Construído em um dia; dashboard sem build, abre com duplo clique |

## Rodando
```bash
python data/generate_data.py          # gera 600 avaliações sintéticas
python agent/analyze.py               # modo offline (regras)
ANTHROPIC_API_KEY=sk-... pip install anthropic && python agent/analyze.py   # modo Claude
# abra dashboard/index.html
```

## Resultado de exemplo
O agente identifica sozinho o ponto fraco de cada restaurante (ex.: **Burger do Zé → atraso, 26 menções**) e sugere a ação (revisar raio de entrega nos picos, aviso proativo de atraso).

## Impacto estimado (hipótese a validar)
Ler 600 avaliações manualmente ≈ 3h por ciclo. Com o agente: ~1 min. Em um time com 50 restaurantes, isso libera dezenas de horas por mês para agir em vez de ler.

## Próximos passos
- Medir acurácia do classificador contra 100 avaliações rotuladas à mão (LLM vs. regras).
- Resposta automática ao cliente com aprovação humana.
- Deploy do dashboard no Vercel/Netlify e dados reais via Google Sheets.

## Limitações honestas
Dados sintéticos; sem avaliação formal de qualidade ainda; fallback por regras é simples de propósito.
