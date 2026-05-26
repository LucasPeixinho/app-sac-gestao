# Gestão SAC — Contexto do Projeto

## Stack

- **Backend**: FastAPI + SQLAlchemy 2.x + Oracle (oracledb)
- **Frontend**: Jinja2 + Tailwind (CDN Play) + HTMX 2.0 + Alpine.js 3.x (defer)
- **Auth**: JWT via python-jose + passlib bcrypt; sessão web via cookie `gsac_session`
- **Banco leitura**: `read_engine` → schema CEDEP (Oracle)
- **Banco escrita**: `write_engine` → schema `gestao_sac` (Oracle)

## Estrutura de diretórios relevante

```
app/
  main.py                        # monta routers REST (/api/v1/) e web (raiz)
  core/
    database.py                  # read_engine + write_engine + get_write_db
  models/
    ocorrencia.py                # Ocorrencia
    ocorrencia_item.py           # OcorrenciaItem
    ocorrencia_evento.py         # OcorrenciaEvento
    usuario.py                   # Usuario
    anexo.py                     # Anexo
  schemas/
    ocorrencia.py                # Pydantic schemas + validação IMPACTOS_POR_TIPO
  services/
    ocorrencia_service.py        # CRUD + máquina de estados
    evento_service.py            # audit log de eventos
    carregamento_service.py      # consulta nota fiscal no CEDEP (read_engine)
    user_service.py
    anexo_service.py
  api/v1/
    ocorrencias.py               # endpoints REST
  web/
    routes/
      ocorrencias.py             # rotas web (HTML)
      usuarios.py
    dependencies.py              # get_current_web_user
    templates_config.py          # instância Jinja2Templates com now() global
  utils/
    enums.py                     # TipoOcorrenciaEnum, CausaRaizEnum, StatusOcorrenciaEnum, etc.
  templates/
    base/
      base.html                  # carrega HTMX 2.0, Alpine 3.x (defer), Tailwind CDN, Lucide
      authenticated.html         # layout com sidebar + header
    pages/
      ocorrencias/
        create.html              # página nova ocorrência
        list.html                # listagem com KPIs e filtros
        view.html                # visualização + timeline de eventos
        edit.html                # edição
    partials/
      nota_info.html             # resultado HTMX ao buscar NF
      impacto_options.html
sql/
  07_refactor_ocorrencias_fluxo.sql  # migration — EXECUTAR COMO gestao_sac
```

## Fluxo de status das ocorrências

```
EM_TRATAMENTO → PENDENTE | ENCAMINHADO | CONCLUIDO
PENDENTE      → EM_TRATAMENTO | ENCAMINHADO | CONCLUIDO
ENCAMINHADO   → EM_TRATAMENTO | PENDENTE | CONCLUIDO
CONCLUIDO     → FINALIZADO (gerente aprovar) | EM_TRATAMENTO (gerente reprovar)
FINALIZADO    → terminal
```

## Página /ocorrencias/nova (create.html)

### Mecanismo atual

1. Usuário digita NF e clica Buscar
2. HTMX faz `GET /ocorrencias/buscar-nota` e injeta `partials/nota_info.html` em `#nota-info`
3. `nota_info.html` renderiza:
   - `<script id="nota-produtos-json" type="application/json">` com array de produtos
   - Caixa verde com dados da nota
4. `hx-on:htmx:after-swap="onNotaSwap(event)"` no `<form>` captura o evento HTMX
5. `onNotaSwap` (definido em `{% block scripts_extra %}`) lê `#nota-produtos-json` e atualiza o estado Alpine via `Alpine.$data(root)`

### Estado Alpine (x-data em `#ocorrencia-form-root`)

```js
{
  produtos: [],          // array de produtos da NF
  selecionados: [],      // array de codprod selecionados (controla visibilidade)
  itens_selecionados: {}, // mapa codprod → dados do item (para envio)
  motivo: '',
  causa: '',
  notaOk: false,
  arquivosNomes: [],
  // métodos: isSelecionado, toggleItem, updateQtd, selecionarTodos, desselecionarTodos, ...
}
```

### Problema em aberto — seleção de produtos NÃO funciona

Após buscar nota e produtos aparecerem via `x-for`:
- Botão "Selecionar todos" não aparece
- Campo de qtd afetada não aparece ao marcar checkbox

**Hipóteses já descartadas:**
- Timing de Alpine MutationObserver (resolvido com hx-on no form)
- `Object.keys()` não rastreado pelo proxy Alpine (trocado por `.every()`)
- `x-if` vs `x-show` no input de quantidade (já usa `x-show`)
- `itens_selecionados[codprod]` com proxy stale (trocado por `selecionados[]` array)

**Estado atual do código:**
- `selecionados: []` é um array reativo usado para controle de visibilidade
- `isSelecionado(codprod)` usa `selecionados.includes(codprod)`
- `todosSelecionados` usa `selecionados.length === produtos.length`
- `x-show="isSelecionado(p.codprod)"` controla visibilidade do input de qtd
- Produtos carregam corretamente (x-for funciona), mas interações não reagem

**Próxima abordagem a tentar:** a definir

## Rotas principais

| Método | Rota | Descrição |
|--------|------|-----------|
| GET | `/ocorrencias` | listagem |
| GET | `/ocorrencias/nova` | formulário de criação |
| POST | `/ocorrencias` | salva nova ocorrência |
| GET | `/ocorrencias/buscar-nota` | HTMX partial — busca NF no CEDEP |
| GET | `/ocorrencias/{id}` | visualização |
| GET | `/ocorrencias/{id}/editar` | edição |
| POST | `/ocorrencias/{id}/atualizar` | salva edição |
| POST | `/ocorrencias/{id}/pendente` | transição status |
| POST | `/ocorrencias/{id}/encaminhar` | transição status |
| POST | `/ocorrencias/{id}/concluir` | transição status |
| POST | `/ocorrencias/{id}/aprovar` | transição status (gerente) |
| POST | `/ocorrencias/{id}/reprovar` | transição status (gerente) |

## Pendências

- **EXECUTAR** `sql/07_refactor_ocorrencias_fluxo.sql` como usuário `gestao_sac` antes de testar
- **Resolver** problema de interatividade na seleção de produtos em `/ocorrencias/nova`
