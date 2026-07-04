# CLAUDE.md — album-copa

Contexto de projeto para agentes. Álbum de figurinhas da Copa 2026: backend Django + MySQL,
frontend Angular. Specs de produto em `specs/`; decisões técnicas em `.specify/specs/`.

## Stack
- Backend: Python 3.12, Django 4.2, MySQL 8.0 (`mysqlclient`), DRF, `django-auditlog`,
  `structlog`/`django-structlog`, `Pillow`, `django-unfold`. Gerenciador: `uv`. Testes: `pytest`.
- Frontend: Angular 17.
- Padrões de API: prefixo `/api/v1/`, paginação DRF, erro `{ "detail", "code" }`.
- Fluxo: branch a partir de `master` (ex.: `feat-04-app-figurinhas`); spec antes do código.

## Modelagem (regra obrigatória)
- **Models base** em `backend/utils/models.py`: toda tabela DEVE herdar de uma das duas classes
  abstratas — `ModelPadrao` (`criado_em`/`alterado_em`) quando **não** é editada por usuário, ou
  `ModelPadraoAuditavel` (adiciona `criado_por`/`alterado_por`) quando **pode** ser editada por
  usuário. Não redeclarar `criado_em`/`alterado_em` nos filhos. Detalhes em
  `.specify/specs/desenvolvimento`.

## Code review (regras obrigatórias)
- **N+1 query**: nunca acessar atributo de relação (FK/OneToOne/reverse/M2M) dentro de laço sem
  otimização. Toda travessia de relação DEVE usar `select_related()` (FK/OneToOne) ou
  `prefetch_related()` (reverse/M2M) — em views, DRF serializers, Django Admin (`list_select_related`),
  management commands e templates. Um `queryset` que itera sobre relações sem isso é reprovação de PR.
- **Herança de model base**: ver regra de Modelagem acima.
- Checklist completo em `.specify/specs/code-review/spec.md`.

## Plano ativo (Spec Kit)
<!-- SPECKIT START -->
- Feature: **Frontend do álbum (Angular 17 + Tailwind)** — plano: [`specs/06-frontend-album/plan.md`](specs/06-frontend-album/plan.md)
  - Artefatos: `spec.md`, `research.md`, `data-model.md`, `contracts/`, `quickstart.md`.
  - Escopo: feature `album` (consolida At.08–12) — grade agrupada por seleção com imagem, estados
    tenho/falta/especial/repetidas, marcar posse (`+`/`-`/definir) com atualização imediata, progresso
    geral e por seleção, filtros (seleção/status/busca) + limpar, estados loading/erro/vazio,
    **responsividade obrigatória** (360/768/1440). Consome a API da At.05. Estilização **Tailwind**
    (SCSS só global); identidade visual base **Panini WC26** (roxo + ouro). Foco: eficiência de
    dados/render (catálogo em cache, filtro client-side, `@for track`, signals).
  - Anterior (concluída): **API REST do álbum (DRF)** — [`specs/05-backend-api-rest/plan.md`](specs/05-backend-api-rest/plan.md).
<!-- SPECKIT END -->
