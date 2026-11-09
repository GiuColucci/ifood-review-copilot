"""Review Copilot — agente que lê avaliações, classifica com LLM e gera plano de ação por restaurante.

Dois modos:
  * Com ANTHROPIC_API_KEY  -> usa Claude (saída estruturada em JSON, em lotes).
  * Sem chave (padrão)     -> fallback por regras, para o demo rodar offline.
Saída: dashboard/data.js (consumido pelo dashboard estático).
"""
import csv, json, os, re, sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PROMPT = (ROOT / "prompts" / "classify.md").read_text(encoding="utf-8")
THEMES = ["atraso", "item_faltando", "embalagem", "sabor", "preço", "atendimento", "entrega"]

RULES = {
    "atraso": r"demor|atras|esperei|frio|\d+ minutos",
    "item_faltando": r"faltou|sem o |incompleto|veio sem",
    "embalagem": r"embalagem|vazou|amassad|derreteu",
    "preço": r"caro|custo|porção|preço",
    "atendimento": r"atendimento|reclama|ignorad|chat",
    "entrega": r"entregador|pontual|rapidinho",
    "sabor": r"sabor|tempero|delicios|seca|sem sal|saboros",
}

def classify_rules(batch):
    out = []
    for r in batch:
        t = r["texto"].lower()
        theme = next((k for k, p in RULES.items() if re.search(p, t)), "sabor")
        out.append({"id": int(r["id"]), "tema": theme, "sentimento": "negativo" if int(r["nota"]) <= 3 else "positivo"})
    return out

def classify_llm(batch):
    import anthropic
    client = anthropic.Anthropic()
    payload = json.dumps([{"id": r["id"], "nota": r["nota"], "texto": r["texto"]} for r in batch], ensure_ascii=False)
    msg = client.messages.create(
        model=os.environ.get("MODEL", "claude-haiku-5-5"), max_tokens=4000,
        system=PROMPT.replace("{{THEMES}}", ", ".join(THEMES)),
        messages=[{"role": "user", "content": payload}],
    )
    text = msg.content[0].text
    return json.loads(text[text.index("["): text.rindex("]") + 1])

def action_plan(theme, n):
    plans = {
        "atraso": "Revisar raio de entrega e tempo de preparo nos horários de pico; ativar aviso proativo de atraso.",
        "item_faltando": "Adotar checklist de conferência antes de lacrar a sacola; foto do pedido na saída.",
        "embalagem": "Trocar para embalagem com vedação e lacre; testar com pedidos de longa distância.",
        "sabor": "Revisar receita/ponto da cocção dos itens mais citados; coletar feedback guiado.",
        "preço": "Reavaliar tamanho de porção vs. preço; criar combo de entrada.",
        "atendimento": "Definir SLA de resposta no chat (ex.: < 10 min) com respostas-modelo.",
        "entrega": "Reconhecer e replicar boas práticas da logística.",
    }
    return plans.get(theme, "Investigar.")

def main():
    rows = list(csv.DictReader(open(ROOT / "data" / "reviews.csv", encoding="utf-8")))
    use_llm = bool(os.environ.get("ANTHROPIC_API_KEY"))
    print("Modo:", "Claude API" if use_llm else "fallback por regras (defina ANTHROPIC_API_KEY para usar LLM)")
    labels = {}
    for i in range(0, len(rows), 40):
        batch = rows[i:i + 40]
        try:
            res = classify_llm(batch) if use_llm else classify_rules(batch)
        except Exception as e:
            print("LLM falhou, usando regras neste lote:", e, file=sys.stderr)
            res = classify_rules(batch)
        labels.update({x["id"]: x for x in res})

    per = defaultdict(lambda: {"n": 0, "soma": 0, "neg": Counter()})
    monthly = defaultdict(lambda: [0, 0])
    for r in rows:
        l, p = labels[int(r["id"])], per[r["restaurante"]]
        p["n"] += 1; p["soma"] += int(r["nota"])
        if l["sentimento"] == "negativo":
            p["neg"][l["tema"]] += 1
        m = monthly[r["data"][:7]]; m[0] += int(r["nota"]); m[1] += 1

    restaurants = []
    for name, p in per.items():
        top = p["neg"].most_common(3)
        restaurants.append({
            "nome": name, "avaliacoes": p["n"], "nota_media": round(p["soma"] / p["n"], 2),
            "pct_negativas": round(100 * sum(p["neg"].values()) / p["n"], 1),
            "problemas": [{"tema": t, "qtd": q, "acao": action_plan(t, q)} for t, q in top],
        })
    restaurants.sort(key=lambda x: x["nota_media"])
    out = {"modo": "claude" if use_llm else "regras", "total": len(rows),
           "tendencia": [{"mes": k, "nota": round(v[0] / v[1], 2)} for k, v in sorted(monthly.items())],
           "restaurantes": restaurants}
    (ROOT / "dashboard" / "data.js").write_text("window.DATA = " + json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    print("OK -> dashboard/data.js")

if __name__ == "__main__":
    main()
