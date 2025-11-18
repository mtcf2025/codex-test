"""Núcleo do aplicativo de RPG inspirado em Westeros."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

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


@dataclass
class CharacterCreationData:
    nome: str
    epoca: str
    reino: str
    historia: str
    nivel: int
    classe: str
    antecedente: str
    divindade: str
    habilidades: Dict[str, int]
    pericias: List[str]
    equipamentos: List[str]


class GameMaster:
    """Gerencia a sessão de RPG respeitando as regras fornecidas."""

    def __init__(self) -> None:
        self.personagem: Optional[Character] = None
        self.capitulo_atual: Optional[Chapter] = None
        self.capitulos: List[Chapter] = []

    # ----- criação de ficha -----
    def iniciar_criacao_personagem(self) -> Character:
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

        dados = CharacterCreationData(
            nome=input("Qual o nome do personagem? "),
            epoca=epoca,
            reino=reino,
            historia=historia,
            nivel=nivel,
            classe=classe,
            antecedente=antecedente,
            divindade=divindade,
            habilidades=habilidades,
            pericias=pericias,
            equipamentos=equipamentos,
        )
        personagem = self.create_character(dados)
        print("Ficha criada. Resumo:")
        print(personagem.resumo())
        print("Guarde essa ficha; ela será usada em todas as cenas.")
        return personagem

    def create_character(self, dados: CharacterCreationData) -> Character:
        self.personagem = Character(
            nome=dados.nome,
            epoca=dados.epoca,
            reino=dados.reino,
            historia=dados.historia,
            nivel=dados.nivel,
            classe=dados.classe,
            antecedente=dados.antecedente,
            divindade=dados.divindade,
            habilidades=dados.habilidades,
            pericias_treinadas=dados.pericias,
            equipamentos=dados.equipamentos,
        )
        return self.personagem

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
    def iniciar_capitulo(self) -> Chapter:
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
        return capitulo

    # ----- testes e rolagens -----
    def solicitar_acao(self) -> Optional[Dict[str, Any]]:
        if not self.personagem or not self.capitulo_atual:
            print("Você precisa iniciar um capítulo antes de agir.")
            return None
        descricao = input("Descreva sua ação: ")
        tipo = self._selecionar_tipo_teste()
        dificuldade = self._selecionar_dificuldade()
        extra: Dict[str, Any] = {}
        if tipo == "Perícia":
            extra["pericia"] = self._escolher_pericia_para_teste()
        elif tipo == "Ataque":
            extra["arma"] = input("Qual arma está sendo usada? ") or "espada longa"
            extra["dano"] = input("Qual é o dado de dano da arma? (ex.: 1d8) ") or "1d8"
        else:
            extra["escola"] = input("Qual tipo de magia? (piromancia de R'hllor, feitiços dos Filhos da Floresta, etc.) ")
            extra["habilidade"] = (
                input("Usa qual habilidade base? (Inteligência, Sabedoria ou Carisma) ")
                or "Sabedoria"
            )
            extra["dano"] = input("Qual é o efeito/dado de dano da magia? (ex.: 2d6 fogo vivo) ") or "2d6 fogo vivo"
        request = self.preparar_acao(tipo, dificuldade, **extra)
        request.descricao = descricao
        consentimento = input("Posso rolar os dados? (s/n) ")
        resultado = self.executar_acao(request, consentimento.strip().lower().startswith("s"))
        self._exibir_resultado(resultado)
        return resultado

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

    def preparar_acao(self, tipo: str, dificuldade: int, **kwargs: Any) -> ActionRequest:
        assert self.personagem
        if tipo == "Perícia":
            pericia = kwargs.get("pericia") or self._escolher_pericia_para_teste()
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
            arma = kwargs.get("arma") or "espada longa"
            habilidade = "Força" if "arco" not in arma.lower() else "Destreza"
            bonus = self.personagem.habilidade_mod(habilidade) + self.personagem.bonus_proficiencia
            dano = kwargs.get("dano") or "1d8"
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
        escola = kwargs.get("escola") or "Magia ancestral"
        habilidade = kwargs.get("habilidade") or "Sabedoria"
        bonus = self.personagem.habilidade_mod(habilidade) + self.personagem.bonus_proficiencia
        dano = kwargs.get("dano") or "2d6 fogo vivo"
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

    def executar_acao(self, request: ActionRequest, consentido: bool = True) -> Dict[str, Any]:
        assert self.personagem
        resultado: Dict[str, Any] = {
            "tipo": request.tipo_teste,
            "descricao": request.descricao,
            "dificuldade": request.dificuldade,
            "bonus": request.bonus,
            "dados": [],
            "consentido": consentido,
        }
        if not consentido:
            resultado["mensagem"] = "Jogador optou por não rolar os dados."
            return resultado
        rolagem = roll_dice(request.dado_quantidade, request.dado_faces)
        total = sum(rolagem) + request.bonus
        resultado["dados"] = rolagem
        resultado["total"] = total
        resultado["expressao"] = " + ".join(str(r) for r in rolagem)
        sucesso = total >= request.dificuldade
        resultado["sucesso"] = sucesso
        if sucesso:
            resultado["mensagem"] = (
                "Sucesso! O destino favorece seus passos, como diria George Martin: cada açoite "
                "de neve ecoa em sua vitória."
            )
            if request.dano:
                resultado["dano"] = self._resolver_dano(request.dano)
        else:
            resultado["mensagem"] = (
                "Fracasso. A canção dos Sete Reinos lembra que nem todo aço encontra o alvo, e "
                "consequências surgirão."
            )
        return resultado

    def _resolver_dano(self, dano: str) -> Dict[str, Any]:
        if "d" not in dano:
            return {"efeito": dano}
        partes = dano.lower().split("d")
        try:
            quantidade = int(partes[0])
            resto = partes[1].split()
            faces = int(resto[0])
        except (ValueError, IndexError):
            return {"erro": f"Não foi possível interpretar o dado de dano '{dano}'."}
        rolagens = roll_dice(quantidade, faces)
        total = sum(rolagens)
        detalhes = " + ".join(str(r) for r in rolagens)
        efeito = " ".join(resto[1:]) if len(resto) > 1 else "dano"
        return {"detalhes": detalhes, "total": total, "efeito": efeito}

    # ----- XP e recompensas -----
    def concluir_capitulo(self, dificuldade: Optional[str] = None) -> Optional[Dict[str, Any]]:
        if not self.personagem or not self.capitulo_atual:
            print("Nenhum capítulo ativo para concluir.")
            return None
        if dificuldade is None:
            dificuldade = (
                input(
                    "Qual foi a dificuldade geral do capítulo? (trivial/fácil/médio/difícil/mortal) "
                )
                .strip()
                .lower()
                or "médio"
            )
        xp = CHAPTER_DIFFICULTY_XP.get(dificuldade, 600)
        self.personagem.ganhar_xp(xp)
        self.personagem.registrar_capitulo()
        self.capitulo_atual.concluido = True
        print(
            f"Capítulo concluído. Distribuindo {xp} XP conforme as tabelas do Livro do Mestre D&D 5e."
        )
        recompensas = self._entregar_recompensas(dificuldade)
        self.capitulo_atual = None
        return {"xp": xp, "dificuldade": dificuldade, "recompensas": recompensas}

    def _entregar_recompensas(self, dificuldade: str) -> Dict[str, Any]:
        for tabela in LOOT_TABLES:
            if tabela.difficulty == dificuldade:
                mensagem = (
                    f"Recompensa: {tabela.coins} moedas de prata e possíveis itens: {', '.join(tabela.curios)}"
                )
                print(mensagem)
                return {"coins": tabela.coins, "itens": tabela.curios, "mensagem": mensagem}
        mensagem = "Os ventos não trouxeram recompensas materiais desta vez."
        print(mensagem)
        return {"mensagem": mensagem}

    # ----- utilidades -----
    def mostrar_ficha(self) -> Optional[str]:
        if not self.personagem:
            print("Nenhuma ficha registrada.")
            return None
        resumo = self.personagem.resumo()
        print(resumo)
        return resumo

    def _exibir_resultado(self, resultado: Dict[str, Any]) -> None:
        if not resultado.get("consentido", True):
            print(resultado.get("mensagem"))
            return
        print(f"Tipo de teste: {resultado.get('tipo')}")
        dados = resultado.get("dados", [])
        if dados:
            expressao = resultado.get("expressao", "")
            bonus = resultado.get("bonus", 0)
            total = resultado.get("total")
            print(
                f"Rolagem: {expressao} + {bonus:+} = {total} | CD {resultado.get('dificuldade')}"
            )
        print(resultado.get("mensagem"))
        if resultado.get("dano"):
            dano = resultado["dano"]
            if "erro" in dano:
                print(dano["erro"])
            elif "detalhes" in dano:
                print(f"Dano causado: {dano['detalhes']} = {dano['total']} ({dano['efeito']})")
            else:
                print(f"Efeito: {dano.get('efeito')}")
