# Projeto Base — Django + Angular

Stack oficial deste repositório (qualquer mudança deve ser refletida aqui, em `.claude/skills/` e em `.specify/specs/`):

## Backend
- Python >= 3.12
- Django >= 4.2
- MySQL como banco de dados
- Auditoria/telemetria: `django-auditlog` (audit trail de models) + `structlog` (logs estruturados) + suporte opcional a `OpenTelemetry` para tracing distribuído

## Frontend
- Angular >= 17
- JavaScript/TypeScript
- Responsividade obrigatória (mobile-first, breakpoints padronizados) em todas as telas

## Estrutura do repositório

```
.
├── .claude/
│   └── skills/              # Boas práticas que o Claude deve seguir neste repo
├── .specify/
│   └── specs/
│       ├── analise-tecnica/ # Specs de decisões e análise técnica
│       ├── desenvolvimento/ # Specs de padrões de desenvolvimento
│       └── code-review/     # Checklist e critérios de code review
├── backend/                 # Projeto Django
└── frontend/                # Projeto Angular
```

## Como funciona a "memória" deste projeto

Este repositório não depende de memória oculta de conversa. Toda decisão de arquitetura,
convenção de código e critério de revisão vive em `.claude/skills/` e `.specify/specs/`.

**Regra fixa**: sempre que um ajuste de stack, padrão ou processo for solicitado via prompt,
o arquivo correspondente nessas duas pastas deve ser atualizado no mesmo momento, para que
qualquer sessão futura (com ou sem memória de conversa) leia o estado atual diretamente do
repositório.
