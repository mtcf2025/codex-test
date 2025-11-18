"""Utilitários para capítulos e narrativa."""
from __future__ import annotations

from dataclasses import dataclass
from typing import List


@dataclass
class Chapter:
    numero: int
    titulo: str
    descricao: str
    concluido: bool = False

    def introducao(self) -> str:
        return f"Capítulo {self.numero} - {self.titulo}\n{self.descricao}"


def criar_primeiro_capitulo(epoca: str, reino: str) -> Chapter:
    titulo = "Sussurros entre as muralhas"
    descricao = (
        "Os ventos de {reino} sopram carregados de preságios. Enquanto o mundo observa, "
        "vozes no salão ecoam sobre alianças quebradas e perigos além da muralha. "
        "No alvorecer dessa época — {epoca} — o destino começa a se entrelaçar com sua espada."
    ).format(epoca=epoca, reino=reino)
    return Chapter(1, titulo, descricao)


def gerar_titulo_para_capitulo(numero: int) -> str:
    nomes = [
        "Fogo sobre a Neve",
        "O Eco dos Corvos",
        "Banquete de Facas",
        "Segredos no Sepulcro",
        "Luz das Velas no Setentrião",
    ]
    return nomes[(numero - 1) % len(nomes)]
