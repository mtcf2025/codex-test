"""Estruturas para representar a ficha do personagem."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List

from .constants import ABILITIES, PROFICIENCY_BY_LEVEL, SKILL_TO_ABILITY


def ability_modifier(score: int) -> int:
    """Calcula o modificador de habilidade padrão do D&D 5e."""

    return (score - 10) // 2


@dataclass
class Character:
    nome: str
    epoca: str
    reino: str
    historia: str
    nivel: int
    classe: str
    antecedente: str
    divindade: str
    habilidades: Dict[str, int]
    pericias_treinadas: List[str]
    equipamentos: List[str]
    inspiracao: bool = False
    xp: int = 0
    capitulos_concluidos: int = 0

    def __post_init__(self) -> None:
        for habilidade in ABILITIES:
            self.habilidades.setdefault(habilidade, 10)
        self.pericias_treinadas = [p for p in self.pericias_treinadas if p in SKILL_TO_ABILITY]
        self.equipamentos = self.equipamentos or ["armadura de couro batido", "arma simples"]

    @property
    def bonus_proficiencia(self) -> int:
        return PROFICIENCY_BY_LEVEL.get(self.nivel, 2)

    def habilidade_mod(self, habilidade: str) -> int:
        return ability_modifier(self.habilidades.get(habilidade, 10))

    def pericia_bonus(self, pericia: str) -> int:
        habilidade = SKILL_TO_ABILITY.get(pericia, "Sabedoria")
        bonus = self.habilidade_mod(habilidade)
        if pericia in self.pericias_treinadas:
            bonus += self.bonus_proficiencia
        return bonus

    def ganhar_xp(self, quantidade: int) -> None:
        self.xp += quantidade

    def registrar_capitulo(self) -> None:
        self.capitulos_concluidos += 1

    def resumo(self) -> str:
        linhas = [
            f"Personagem: {self.nome} (Nível {self.nivel} {self.classe})",
            f"Casa/Origem: {self.reino} | Época: {self.epoca}",
            f"Divindade: {self.divindade}",
            f"História: {self.historia}",
            f"XP atual: {self.xp} | Capítulos concluídos: {self.capitulos_concluidos}",
            "Habilidades:",
        ]
        linhas.extend(f"  - {hab}: {valor} (mod {self.habilidade_mod(hab):+})" for hab, valor in self.habilidades.items())
        linhas.append("Perícias treinadas:")
        linhas.extend(f"  - {p} ({self.pericia_bonus(p):+})" for p in self.pericias_treinadas)
        linhas.append("Equipamentos:")
        linhas.extend(f"  - {eq}" for eq in self.equipamentos)
        return "\n".join(linhas)
