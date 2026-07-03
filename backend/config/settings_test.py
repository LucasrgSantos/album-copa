"""Settings de teste.

Usa SQLite em memória para rodar a suíte sem depender do MySQL local (a stack-alvo continua
MySQL em homologação/produção — ver `.specify/specs/analise-tecnica`). Herdadas de `config.settings`.
"""

from .settings import *  # noqa: F401,F403

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}

# Acelera criação de usuários nos testes.
PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]
