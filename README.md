# codex-test

Repositório de teste para integração com ChatGPT Codex.

## Aplicativo de RPG ambientado em Westeros

O projeto oferece duas formas de conduzir suas campanhas:

1. **Interface em linha de comando** – ideal para quem quer jogar direto no terminal.
2. **Aplicação web com FastAPI** – fornece formulários e históricos de rolagem para
   administrar sessões pelo navegador.

### Principais funcionalidades

- Criação completa de ficha com perguntas específicas sobre o cenário de Game of Thrones.
- Gestão de capítulos, distribuição de experiência e recompensas coerentes com a ficção.
- Sistema de rolagem de dados honesto, com instruções detalhadas antes de cada teste.
- Adaptação de perícias, armas e magias para o contexto de Westeros, mantendo as regras
  do Livro do Jogador, Livro do Mestre e Manual dos Monstros de D&D 5e como referência.

### Como executar (CLI)

```bash
python main.py
```

O menu exibirá opções para criar a ficha do personagem, iniciar capítulos, solicitar
ações com rolagens e concluir capítulos aplicando XP e recompensas. Mantenha sua ficha
anotada para seguir as instruções durante a campanha.

### Como executar (Web)

```bash
pip install fastapi uvicorn jinja2
uvicorn web_app:app --reload
```

Em seguida acesse [http://127.0.0.1:8000](http://127.0.0.1:8000) e utilize os formulários
para registrar fichas, controlar capítulos, rolar dados e aplicar recompensas conforme
o sistema descrito na ambientação de Westeros.
