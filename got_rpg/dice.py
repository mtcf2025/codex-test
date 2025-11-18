"""Utilidades de rolagem de dados honestas."""
from __future__ import annotations

import random
from typing import List


def roll_dice(quantity: int, sides: int) -> List[int]:
    """Rola ``quantity`` dados de ``sides`` lados cada.

    A função utiliza o gerador pseudo-aleatório do Python sem ajustes narrativos, garantindo
    probabilidades uniformes como exigido pelas regras do D&D 5e.
    """

    if quantity <= 0 or sides <= 0:
        raise ValueError("Quantidade e lados precisam ser positivos")

    return [random.randint(1, sides) for _ in range(quantity)]
