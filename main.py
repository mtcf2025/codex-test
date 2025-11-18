"""Interface simples de linha de comando para o RPG em Westeros."""
from __future__ import annotations

from got_rpg import GameMaster


def mostrar_menu() -> None:
    print("\n=== Crônicas de Gelo e Dados ===")
    print("1 - Criar/Atualizar ficha")
    print("2 - Iniciar novo capítulo")
    print("3 - Descrever ação e rolar dados")
    print("4 - Mostrar ficha")
    print("5 - Concluir capítulo")
    print("0 - Sair")


def main() -> None:
    mestre = GameMaster()
    while True:
        mostrar_menu()
        escolha = input("Escolha: ").strip()
        if escolha == "1":
            mestre.iniciar_criacao_personagem()
        elif escolha == "2":
            try:
                mestre.iniciar_capitulo()
            except RuntimeError as exc:
                print(str(exc))
        elif escolha == "3":
            mestre.solicitar_acao()
        elif escolha == "4":
            mestre.mostrar_ficha()
        elif escolha == "5":
            mestre.concluir_capitulo()
        elif escolha == "0":
            print("Que sua canção ecoe em todos os salões de Westeros.")
            break
        else:
            print("Opção inválida.")


if __name__ == "__main__":
    main()
