"""Gera um dataset sintético de avaliações de restaurantes (estilo iFood).
Dados 100% fictícios — usados só para demonstrar o pipeline."""
import csv, random
from datetime import date, timedelta

random.seed(42)
RESTAURANTS = ["Burger do Zé", "Sushi Kenzo", "Pizzaria Bella Napoli", "Marmita da Vovó", "Açaí Tropical"]

# (tema, frases) — cada tema tem tom típico
POS = {
    "sabor": ["Comida deliciosa, tempero perfeito", "Melhor hambúrguer da região, muito saboroso", "Sabor incrível, repetiria com certeza"],
    "entrega": ["Chegou rapidinho e quentinho", "Entregador super educado e pontual"],
    "embalagem": ["Embalagem muito bem feita, nada vazou"],
    "preço": ["Ótimo custo-benefício, porção generosa"],
}
NEG = {
    "atraso": ["Demorou mais de 1 hora para chegar", "Pedido atrasou muito e chegou frio", "Esperei quase 90 minutos, absurdo"],
    "item_faltando": ["Faltou a bebida do meu pedido", "Veio sem o molho que pedi", "Pedido incompleto, faltou um item"],
    "embalagem": ["Embalagem abriu e vazou tudo na sacola", "Tudo amassado, o açaí derreteu e vazou"],
    "sabor": ["Comida sem sal e sem graça", "Carne estava seca e dura"],
    "preço": ["Muito caro para a quantidade que veio"],
    "atendimento": ["Ninguém respondeu minha reclamação no chat", "Atendimento ruim, fui ignorado"],
}
# cada restaurante tem um "ponto fraco" para o agente descobrir
WEAK = {"Burger do Zé": "atraso", "Sushi Kenzo": "item_faltando", "Pizzaria Bella Napoli": "sabor",
        "Marmita da Vovó": "preço", "Açaí Tropical": "embalagem"}

rows, start = [], date(2026, 8, 1)
for i in range(600):
    r = random.choice(RESTAURANTS)
    d = start + timedelta(days=random.randint(0, 90))
    negative = random.random() < 0.38
    if negative:
        theme = WEAK[r] if random.random() < 0.55 else random.choice(list(NEG))
        text, stars = random.choice(NEG[theme]), random.choice([1, 1, 2, 2, 3])
    else:
        theme = random.choice(list(POS))
        text, stars = random.choice(POS[theme]), random.choice([4, 5, 5, 5])
    rows.append({"id": i + 1, "restaurante": r, "data": d.isoformat(), "nota": stars, "texto": text})

with open("data/reviews.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=rows[0].keys())
    w.writeheader(); w.writerows(rows)
print(f"{len(rows)} avaliações geradas em data/reviews.csv")
