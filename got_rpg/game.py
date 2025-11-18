"""Núcleo do aplicativo de RPG inspirado em Westeros."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional

from .character import Character
from .constants import (
    ABILITIES,
    CHAPTER_DIFFICULTY_XP,
    LOOT_TABLES,
    SKILL_TO_ABILITY,
)
from .dice import roll_dice
from .story import Chapter, criar_primeiro_capitulo, gerar_titulo_para_capitulo


@dataclass
class ActionRequest:
    descricao: str
    tipo_teste: str
    dado_quantidade: int
    dado_faces: int
    dificuldade: int
    bonus: int
    dano: Optional[str] = None


class GameMaster:
    """Gerencia a sessão de RPG respeitando as regras fornecidas."""

    def __init__(self) -> None:
        self.personagem: Optional[Character] = None
        self.capitulo_atual: Optional[Chapter] = None
        self.capitulos: List[Chapter] = []

    # ----- criação de ficha -----
    def iniciar_criacao_personagem(self) -> None:
        print("Vamos forjar sua lenda nas terras de Westeros.")
        epoca = input(
            "Em qual época você gostaria de começar a campanha? (padrão: Livro 1) "
        ) or "Livro 1 - A Guerra dos Tronos"
        reino = input("De qual reino ou casa seu personagem vem? ")
        historia = input("Conte quem é e qual é a história do seu personagem: ")
        nivel = int(input("Qual é o nível inicial do seu personagem? (1-20) ") or "1")
        classe = input("Qual arquétipo adapta a classe D&D? (guerreiro do Norte, espadachim de Essos, etc.) ")
        antecedente = input("Qual é o antecedente/posição social? (ex.: bastardo, meistre, mercenário) ")
        divindade = input(
            "Seu personagem segue alguma divindade de Westeros? (ex.: Sete, Antigos Deuses, Senhor da Luz) "
        )
        habilidades = self._coletar_habilidades()
        pericias = self._escolher_pericias()
        equipamentos = self._definir_equipamentos()

        self.personagem = Character(
            nome=input("Qual o nome do personagem? "),
            epoca=epoca,
            reino=reino,
            historia=historia,
            nivel=nivel,
            classe=classe,
            antecedente=antecedente,
            divindade=divindade,
            habilidades=habilidades,
            pericias_treinadas=pericias,
            equipamentos=equipamentos,
        )
        print("Ficha criada. Resumo:")
        print(self.personagem.resumo())
        print("Guarde essa ficha; ela será usada em todas as cenas.")

    def _coletar_habilidades(self) -> Dict[str, int]:
        print("Vamos definir os atributos conforme D&D 5e. Informe valores entre 3 e 20.")
        habilidades: Dict[str, int] = {}
        for habilidade in ABILITIES:
            valor = int(input(f"{habilidade}: ") or "10")
            habilidades[habilidade] = max(3, min(20, valor))
        return habilidades

    def _escolher_pericias(self) -> List[str]:
        print("Escolha até quatro perícias treinadas dentro das opções adaptadas de D&D 5e.")
        opcoes = list(SKILL_TO_ABILITY.keys())
        for idx, nome in enumerate(opcoes, start=1):
            print(f"{idx:02d} - {nome}")
        indices = input("Informe os números separados por vírgula: ")
        escolhidas = []
        if indices:
            for parte in indices.split(","):
                try:
                    idx = int(parte.strip())
                except ValueError:
                    continue
                if 1 <= idx <= len(opcoes):
                    escolhidas.append(opcoes[idx - 1])
        return escolhidas[:4]

    def _definir_equipamentos(self) -> List[str]:
        print("Liste equipamentos iniciais coerentes com Westeros (ex.: cota de couro, espada bastarda).")
        itens = input(
            "Separe itens com vírgula. Se deixar vazio, assumiremos equipamentos básicos. "
        )
        if not itens:
            return ["cota de couro", "espada longa", "adaga escondida"]
        return [item.strip() for item in itens.split(",") if item.strip()]

    # ----- narrativa -----
    def iniciar_capitulo(self) -> None:
        if not self.personagem:
            raise RuntimeError("Crie um personagem antes de iniciar a aventura.")
        if not self.capitulos:
            capitulo = criar_primeiro_capitulo(self.personagem.epoca, self.personagem.reino)
        else:
            numero = len(self.capitulos) + 1
            capitulo = Chapter(
                numero,
                gerar_titulo_para_capitulo(numero),
                "Os caminhos se bifurcam e novas intrigas despontam na distância.",
            )
        self.capitulo_atual = capitulo
        self.capitulos.append(capitulo)
        print(capitulo.introducao())

    # ----- testes e rolagens -----
    def solicitar_acao(self) -> None:
        if not self.personagem or not self.capitulo_atual:
            print("Você precisa iniciar um capítulo antes de agir.")
            return
        descricao = input("Descreva sua ação: ")
        tipo = self._selecionar_tipo_teste()
        dificuldade = self._selecionar_dificuldade()
        request = self._montar_acao(tipo, dificuldade)
        request.descricao = descricao
        self._executar_acao(request)

    def _selecionar_tipo_teste(self) -> str:
        opcoes = ["Perícia", "Ataque", "Magia"]
        for idx, nome in enumerate(opcoes, start=1):
            print(f"{idx} - {nome}")
        escolha = int(input("Qual o tipo de teste? ") or "1")
        return opcoes[escolha - 1]

    def _selecionar_dificuldade(self) -> int:
        print("Dificuldades sugeridas (Livro do Mestre D&D 5e): 10 fácil, 15 médio, 20 difícil.")
        valor = int(input("Informe a CD desejada: ") or "15")
        return max(5, min(30, valor))

    def _montar_acao(self, tipo: str, dificuldade: int) -> ActionRequest:
        assert self.personagem
        if tipo == "Perícia":
            pericia = self._escolher_pericia_para_teste()
            bonus = self.personagem.pericia_bonus(pericia)
            return ActionRequest(
                descricao="",
                tipo_teste=f"Teste de {pericia}",
                dado_quantidade=1,
                dado_faces=20,
                dificuldade=dificuldade,
                bonus=bonus,
            )
        if tipo == "Ataque":
            arma = input("Qual arma está sendo usada? ") or "espada longa"
            habilidade = "Força" if "arco" not in arma.lower() else "Destreza"
            bonus = self.personagem.habilidade_mod(habilidade) + self.personagem.bonus_proficiencia
            dano = input("Qual é o dado de dano da arma? (ex.: 1d8) ") or "1d8"
            return ActionRequest(
                descricao="",
                tipo_teste=f"Ataque com {arma}",
                dado_quantidade=1,
                dado_faces=20,
                dificuldade=dificuldade,
                bonus=bonus,
                dano=dano,
            )
        # magia
        escola = input("Qual tipo de magia? (piromancia de R'hllor, feitiços dos Filhos da Floresta, etc.) ")
        habilidade = input("Usa qual habilidade base? (Inteligência, Sabedoria ou Carisma) ") or "Sabedoria"
        bonus = self.personagem.habilidade_mod(habilidade) + self.personagem.bonus_proficiencia
        dano = input("Qual é o efeito/dado de dano da magia? (ex.: 2d6 fogo vivo) ") or "2d6 fogo vivo"
        return ActionRequest(
            descricao="",
            tipo_teste=f"Conjuração: {escola}",
            dado_quantidade=1,
            dado_faces=20,
            dificuldade=dificuldade,
            bonus=bonus,
            dano=dano,
        )

    def _escolher_pericia_para_teste(self) -> str:
        print("Escolha a perícia pertinente à ação.")
        opcoes = list(SKILL_TO_ABILITY.keys())
        for idx, nome in enumerate(opcoes, start=1):
            print(f"{idx:02d} - {nome}")
        escolha = int(input("Número da perícia: ") or "1")
        return opcoes[escolha - 1]

    def _executar_acao(self, request: ActionRequest) -> None:
        assert self.personagem
        print(f"Tipo de teste: {request.tipo_teste}")
        print(
            f"Rolagem necessária: {request.dado_quantidade}d{request.dado_faces} + {request.bonus:+} "
            f"contra dificuldade {request.dificuldade}"
        )
        consentimento = input("Posso rolar os dados? (s/n) ")
        if consentimento.strip().lower().startswith("s"):
            resultado = roll_dice(request.dado_quantidade, request.dado_faces)
            total = sum(resultado) + request.bonus
            dados_texto = " + ".join(str(r) for r in resultado)
            print(f"Resultado da rolagem: {dados_texto} + {request.bonus:+} = {total}")
            if total >= request.dificuldade:
                print(
                    "Sucesso! O destino favorece seus passos, como diria George Martin: cada açoite "
                    "de neve ecoa em sua vitória."
                )
                if request.dano:
                    self._resolver_dano(request.dano)
            else:
                print(
                    "Fracasso. A canção dos Sete Reinos lembra que nem todo aço encontra o alvo, e "
                    "consequências surgirão."
                )
        else:
            print("Você optou por não rolar. Descreva outra abordagem.")

    def _resolver_dano(self, dano: str) -> None:
        if "d" not in dano:
            print(f"Efeito narrativo: {dano}")
            return
        partes = dano.lower().split("d")
        try:
            quantidade = int(partes[0])
            resto = partes[1].split()
            faces = int(resto[0])
        except (ValueError, IndexError):
            print(f"Não foi possível interpretar o dado de dano '{dano}'.")
            return
        rolagens = roll_dice(quantidade, faces)
        total = sum(rolagens)
        detalhes = " + ".join(str(r) for r in rolagens)
        efeito = " ".join(resto[1:]) if len(resto) > 1 else "dano"
        print(f"Dano causado: {detalhes} = {total} ({efeito})")

    # ----- XP e recompensas -----
    def concluir_capitulo(self) -> None:
        if not self.personagem or not self.capitulo_atual:
            print("Nenhum capítulo ativo para concluir.")
            return
        dificuldade = input(
            "Qual foi a dificuldade geral do capítulo? (trivial/fácil/médio/difícil/mortal) "
        ).strip().lower() or "médio"
        xp = CHAPTER_DIFFICULTY_XP.get(dificuldade, 600)
        self.personagem.ganhar_xp(xp)
        self.personagem.registrar_capitulo()
        self.capitulo_atual.concluido = True
        print(
            f"Capítulo concluído. Distribuindo {xp} XP conforme as tabelas do Livro do Mestre D&D 5e."
        )
        self._entregar_recompensas(dificuldade)
        self.capitulo_atual = None

    def _entregar_recompensas(self, dificuldade: str) -> None:
        for tabela in LOOT_TABLES:
            if tabela.difficulty == dificuldade:
                print(
                    f"Recompensa: {tabela.coins} moedas de prata e possíveis itens: {', '.join(tabela.curios)}"
                )
                return
        print("Os ventos não trouxeram recompensas materiais desta vez.")

    # ----- utilidades -----
    def mostrar_ficha(self) -> None:
        if not self.personagem:
            print("Nenhuma ficha registrada.")
            return
        print(self.personagem.resumo())
