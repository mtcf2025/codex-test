"""Aplicação FastAPI para conduzir o RPG em Westeros via navegador."""
from __future__ import annotations

from typing import Any, Dict, List

from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

from got_rpg.constants import ABILITIES, SKILL_TO_ABILITY
from got_rpg.game import ActionRequest, CharacterCreationData, GameMaster

app = FastAPI(title="Crônicas de Gelo e Dados")
templates = Jinja2Templates(directory="templates")

game_master = GameMaster()
event_log: List[str] = []
last_action: Dict[str, Any] | None = None


def _registrar_evento(mensagem: str) -> None:
    event_log.append(mensagem)
    if len(event_log) > 10:
        event_log.pop(0)


@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "game": game_master,
            "abilities": ABILITIES,
            "skills": SKILL_TO_ABILITY.keys(),
            "event_log": list(event_log),
            "last_action": last_action,
        },
    )


@app.post("/character")
async def criar_personagem(request: Request):
    form = await request.form()
    habilidades = {hab: int(form.get(f"habilidade_{hab}", "10")) for hab in ABILITIES}
    pericias = form.getlist("pericias")  # type: ignore[attr-defined]
    equipamentos = form.get("equipamentos", "")
    equipamentos_list = [item.strip() for item in equipamentos.split(",") if item.strip()]
    dados = CharacterCreationData(
        nome=form.get("nome", "Herói de Westeros"),
        epoca=form.get("epoca", "Livro 1 - A Guerra dos Tronos"),
        reino=form.get("reino", "Winterfell"),
        historia=form.get("historia", ""),
        nivel=int(form.get("nivel", 1)),
        classe=form.get("classe", "guerreiro do Norte"),
        antecedente=form.get("antecedente", "bastardo"),
        divindade=form.get("divindade", "Os Antigos Deuses"),
        habilidades=habilidades,
        pericias=pericias[:4],
        equipamentos=equipamentos_list or ["cota de couro", "espada longa"],
    )
    game_master.create_character(dados)
    _registrar_evento(f"Ficha de {dados.nome} pronta para desafiar Westeros.")
    return RedirectResponse("/", status_code=303)


@app.post("/chapter/start")
async def iniciar_capitulo():
    if not game_master.personagem:
        _registrar_evento("Crie um personagem antes de iniciar capítulos.")
        return RedirectResponse("/", status_code=303)
    capitulo = game_master.iniciar_capitulo()
    _registrar_evento(capitulo.introducao())
    return RedirectResponse("/", status_code=303)


@app.post("/action")
async def realizar_acao(request: Request):
    global last_action
    if not game_master.personagem or not game_master.capitulo_atual:
        _registrar_evento("É necessário ter ficha e capítulo ativo antes de agir.")
        return RedirectResponse("/", status_code=303)
    form = await request.form()
    tipo = form.get("tipo", "Perícia")
    dificuldade = int(form.get("dificuldade", 15))
    descricao = form.get("descricao", "")
    extras: Dict[str, Any] = {}
    if tipo == "Perícia":
        extras["pericia"] = form.get("pericia", "Percepção")
    elif tipo == "Ataque":
        extras["arma"] = form.get("arma", "espada longa")
        extras["dano"] = form.get("dano", "1d8")
    else:
        extras["escola"] = form.get("escola", "Piromancia")
        extras["habilidade"] = form.get("habilidade_magia", "Sabedoria")
        extras["dano"] = form.get("dano", "2d6 fogo vivo")
    request_obj: ActionRequest = game_master.preparar_acao(tipo, dificuldade, **extras)
    request_obj.descricao = descricao
    last_action = game_master.executar_acao(request_obj, consentido=True)
    _registrar_evento(
        f"{last_action.get('tipo')} | Total {last_action.get('total', '-')}/CD {last_action.get('dificuldade')}"
    )
    return RedirectResponse("/", status_code=303)


@app.post("/chapter/conclude")
async def concluir_capitulo(request: Request):
    form = await request.form()
    dificuldade = form.get("dificuldade", "médio").lower()
    resultado = game_master.concluir_capitulo(dificuldade)
    if resultado:
        recompensa = resultado["recompensas"].get("mensagem", "")
        _registrar_evento(
            f"Capítulo encerrado: {resultado['xp']} XP concedidos. {recompensa}"
        )
    return RedirectResponse("/", status_code=303)
