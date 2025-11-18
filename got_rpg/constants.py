"""Constantes e tabelas utilitárias para o RPG ambientado em Westeros."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List

ABILITIES: List[str] = [
    "Força",
    "Destreza",
    "Constituição",
    "Inteligência",
    "Sabedoria",
    "Carisma",
]

SKILL_TO_ABILITY: Dict[str, str] = {
    "Atletismo": "Força",
    "Acrobacia": "Destreza",
    "Furtividade": "Destreza",
    "Prestidigitação": "Destreza",
    "Arcanismo": "Inteligência",
    "História": "Inteligência",
    "Investigação": "Inteligência",
    "Natureza": "Inteligência",
    "Religião": "Inteligência",
    "Intuição": "Sabedoria",
    "Percepção": "Sabedoria",
    "Sobrevivência": "Sabedoria",
    "Animais": "Sabedoria",
    "Enganação": "Carisma",
    "Intimidação": "Carisma",
    "Atuação": "Carisma",
    "Persuasão": "Carisma",
}

# tabela oficial de bônus de proficiência por nível em D&D 5e
PROFICIENCY_BY_LEVEL: Dict[int, int] = {
    **{level: 2 for level in range(1, 5)},
    **{level: 3 for level in range(5, 9)},
    **{level: 4 for level in range(9, 13)},
    **{level: 5 for level in range(13, 17)},
    **{level: 6 for level in range(17, 21)},
}

CHAPTER_DIFFICULTY_XP: Dict[str, int] = {
    "trivial": 150,
    "fácil": 300,
    "médio": 600,
    "difícil": 1200,
    "mortal": 2200,
}

@dataclass
class LootTable:
    difficulty: str
    coins: int
    curios: List[str]


LOOT_TABLES: List[LootTable] = [
    LootTable("trivial", 10, ["alguns vinténs de cobre", "um broche enferrujado"]),
    LootTable("fácil", 50, ["um punhal comum", "um mapa incompleto de vilarejo"]),
    LootTable("médio", 125, ["um anel com brasão menor", "frasco de veneno basilisca"]),
    LootTable("difícil", 300, ["espada valiriana danificada", "livro de segredos septões"]),
    LootTable("mortal", 750, ["arco de osso de dragão", "frasco de fogo vivo"]),
]
