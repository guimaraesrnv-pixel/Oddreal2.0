"""
OddReal 2.0
Bookmakers

Responsabilidade:
- normalizar identificadores de bookmakers;
- reconhecer variações de nomes;
- manter uma lista branca de fontes relevantes;
- preservar o nome original recebido pela API;
- fornecer nome de exibição;
- permitir diagnóstico do processo de reconhecimento.

Este módulo NÃO realiza:
- cálculo de probabilidade;
- EV;
- Value Bet;
- Índice OddReal;
- análise matemática.
"""

from __future__ import annotations

import re
import unicodedata
from typing import Dict, FrozenSet, Optional


# ==========================================================
# FONTES RELEVANTES
# ==========================================================

BRAZIL_PRIMARY_BOOKMAKERS: FrozenSet[str] = frozenset(
    {
        "bet365",
        "betano",
        "sportingbet",
        "kto",
        "novibet",
        "betnacional",
    }
)


# ==========================================================
# ALIASES
# ==========================================================

BOOKMAKER_ALIASES: Dict[str, str] = {
    # Bet365
    "bet365": "bet365",
    "bet 365": "bet365",
    "bet-365": "bet365",
    "bet365.com": "bet365",

    # Betano
    "betano": "betano",
    "betano brasil": "betano",
    "betano.com": "betano",

    # Sportingbet
    "sportingbet": "sportingbet",
    "sporting bet": "sportingbet",
    "sporting-bet": "sportingbet",
    "sportingbet brasil": "sportingbet",
    "sportingbet.com": "sportingbet",

    # KTO
    "kto": "kto",
    "kto brasil": "kto",
    "kto.com": "kto",

    # Novibet
    "novibet": "novibet",
    "novibet brasil": "novibet",
    "novibet.com": "novibet",

    # Betnacional
    "betnacional": "betnacional",
    "bet nacional": "betnacional",
    "betnacional brasil": "betnacional",
    "betnacional.com": "betnacional",
}


# ==========================================================
# NOMES DE EXIBIÇÃO
# ==========================================================

BOOKMAKER_DISPLAY_NAMES: Dict[str, str] = {
    "bet365": "bet365",
    "betano": "Betano",
    "sportingbet": "Sportingbet",
    "kto": "KTO",
    "novibet": "Novibet",
    "betnacional": "Betnacional",
}


# ==========================================================
# NORMALIZAÇÃO BÁSICA
# ==========================================================

def _remove_accents(
    value: str,
) -> str:
    """
    Remove acentos sem alterar o conteúdo textual.
    """

    normalized = unicodedata.normalize(
        "NFKD",
        value,
    )

    return "".join(
        char
        for char in normalized
        if not unicodedata.combining(char)
    )


def _normalize_text(
    value: Optional[str],
) -> str:
    """
    Normalização genérica para comparação.

    Não decide se o bookmaker é autorizado.
    """

    if value is None:
        return ""

    value = str(value).strip().lower()

    if not value:
        return ""

    value = _remove_accents(
        value
    )

    # Remove protocolo caso apareça.
    value = re.sub(
        r"^https?://",
        "",
        value,
    )

    # Remove www.
    value = re.sub(
        r"^www\.",
        "",
        value,
    )

    # Remove espaços duplicados.
    value = " ".join(
        value.split()
    )

    return value


def _compact(
    value: str,
) -> str:
    """
    Produz uma forma compacta para comparação.

    Exemplos:

        Bet 365
        bet-365
        bet_365
        bet365

    tornam-se equivalentes.
    """

    value = _normalize_text(
        value
    )

    return re.sub(
        r"[^a-z0-9]+",
        "",
        value,
    )


# ==========================================================
# MAPA COMPACTADO DE ALIASES
# ==========================================================

_COMPACT_ALIASES: Dict[str, str] = {
    _compact(alias): canonical
    for alias, canonical
    in BOOKMAKER_ALIASES.items()
}


# ==========================================================
# NORMALIZAÇÃO DO BOOKMAKER
# ==========================================================

def normalize_bookmaker_name(
    bookmaker: Optional[str],
) -> Optional[str]:
    """
    Retorna o identificador canônico quando a fonte
    é reconhecida.

    Retorna None quando não existe correspondência.

    IMPORTANTE:
    desconhecido NÃO significa automaticamente inválido;
    significa apenas que a aplicação não possui um alias
    conhecido para aquele identificador.
    """

    normalized = _normalize_text(
        bookmaker
    )

    if not normalized:
        return None

    # ------------------------------------------------------
    # Correspondência exata
    # ------------------------------------------------------

    canonical = BOOKMAKER_ALIASES.get(
        normalized
    )

    if canonical:
        return canonical

    # ------------------------------------------------------
    # Correspondência compactada
    # ------------------------------------------------------

    compact = _compact(
        normalized
    )

    canonical = _COMPACT_ALIASES.get(
        compact
    )

    if canonical:
        return canonical

    # ------------------------------------------------------
    # Correspondência direta com nome canônico
    # ------------------------------------------------------

    if compact in {
        _compact(name)
        for name in BRAZIL_PRIMARY_BOOKMAKERS
    }:
        for name in BRAZIL_PRIMARY_BOOKMAKERS:
            if _compact(name) == compact:
                return name

    return None


# ==========================================================
# VERIFICAÇÃO
# ==========================================================

def is_allowed_bookmaker(
    bookmaker: Optional[str],
) -> bool:
    """
    Retorna True somente quando o bookmaker reconhecido
    pertence à lista branca.
    """

    normalized = normalize_bookmaker_name(
        bookmaker
    )

    if normalized is None:
        return False

    return normalized in (
        BRAZIL_PRIMARY_BOOKMAKERS
    )


# ==========================================================
# NOME DE EXIBIÇÃO
# ==========================================================

def bookmaker_display_name(
    bookmaker: Optional[str],
) -> str:
    """
    Retorna o nome amigável para interface.
    """

    normalized = normalize_bookmaker_name(
        bookmaker
    )

    if normalized is None:
        return str(
            bookmaker or "Fonte desconhecida"
        )

    return BOOKMAKER_DISPLAY_NAMES.get(
        normalized,
        normalized.title(),
    )


# ==========================================================
# DIAGNÓSTICO
# ==========================================================

def bookmaker_diagnostics(
    bookmaker: Optional[str],
) -> Dict[str, object]:
    """
    Retorna informações suficientes para diagnosticar
    problemas de reconhecimento sem alterar o pipeline.
    """

    original = str(
        bookmaker or ""
    ).strip()

    normalized = normalize_bookmaker_name(
        original
    )

    return {
        "original": original,
        "normalized": normalized,
        "recognized": normalized is not None,
        "allowed": (
            normalized in BRAZIL_PRIMARY_BOOKMAKERS
            if normalized is not None
            else False
        ),
        "display_name": (
            bookmaker_display_name(
                original
            )
        ),
    }


# ==========================================================
# LISTA DE FONTES
# ==========================================================

def allowed_bookmakers() -> FrozenSet[str]:
    """
    Retorna uma cópia imutável da lista branca.
    """

    return frozenset(
        BRAZIL_PRIMARY_BOOKMAKERS
    )


# ==========================================================
# EXPORTAÇÃO COMPATÍVEL COM O DATAMANAGER ATUAL
# ==========================================================

ALLOWED_BOOKMAKERS = (
    BRAZIL_PRIMARY_BOOKMAKERS
)


__all__ = [
    "BRAZIL_PRIMARY_BOOKMAKERS",
    "ALLOWED_BOOKMAKERS",
    "BOOKMAKER_ALIASES",
    "BOOKMAKER_DISPLAY_NAMES",
    "normalize_bookmaker_name",
    "is_allowed_bookmaker",
    "bookmaker_display_name",
    "bookmaker_diagnostics",
    "allowed_bookmakers",
]
