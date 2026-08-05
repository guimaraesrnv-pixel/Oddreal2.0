"""
OddReal 2.0
Bookmakers

Configuração central das casas de apostas consideradas pelo sistema.

IMPORTANTE:
Este arquivo funciona como uma LISTA BRANCA.

Somente bookmakers presentes nesta configuração poderão:

- participar do consenso de mercado;
- fornecer a melhor odd;
- aparecer nas análises;
- participar do cálculo do EV;
- participar do Índice OddReal;
- aparecer no dashboard.

Casas desconhecidas, não configuradas ou não reconhecidas
pela aplicação são automaticamente ignoradas.

A lista pode ser alterada sem modificar o Analyzer.
"""

from __future__ import annotations

from typing import Dict, FrozenSet, Optional


# ==========================================================
# BOOKMAKERS PRINCIPAIS
# ==========================================================

# Nomes canônicos utilizados internamente pelo OddReal.
#
# IMPORTANTE:
# Os nomes abaixo são apenas os nomes internos.
# O arquivo também possui aliases para diferentes nomes
# que podem ser retornados pela API.

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

# A API pode retornar pequenas diferenças no nome da casa.
#
# Exemplo:
#
# "Bet365"
# "bet365"
# "Bet 365"
#
# Todos devem ser tratados como a mesma casa.

BOOKMAKER_ALIASES: Dict[str, str] = {

    # ------------------------------------------------------
    # BET365
    # ------------------------------------------------------

    "bet365": "bet365",
    "bet 365": "bet365",
    "bet-365": "bet365",

    # ------------------------------------------------------
    # BETANO
    # ------------------------------------------------------

    "betano": "betano",
    "betano brasil": "betano",
    "betano.com": "betano",

    # ------------------------------------------------------
    # SPORTINGBET
    # ------------------------------------------------------

    "sportingbet": "sportingbet",
    "sporting bet": "sportingbet",
    "sportingbet brasil": "sportingbet",

    # ------------------------------------------------------
    # KTO
    # ------------------------------------------------------

    "kto": "kto",
    "kto brasil": "kto",
    "kto.com": "kto",

    # ------------------------------------------------------
    # NOVIBET
    # ------------------------------------------------------

    "novibet": "novibet",
    "novibet brasil": "novibet",
    "novibet.com": "novibet",

    # ------------------------------------------------------
    # BETNACIONAL
    # ------------------------------------------------------

    "betnacional": "betnacional",
    "bet nacional": "betnacional",
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
# NORMALIZAÇÃO
# ==========================================================

def normalize_bookmaker_name(
    bookmaker: Optional[str],
) -> Optional[str]:
    """
    Normaliza o nome recebido da API.

    Retorna:

        nome canônico

    ou:

        None

    quando o bookmaker não pertence à lista autorizada.
    """

    if bookmaker is None:
        return None

    name = str(bookmaker).strip().lower()

    if not name:
        return None

    # Normalização básica.
    name = " ".join(
        name.split()
    )

    # Primeiro tenta alias exato.
    canonical = BOOKMAKER_ALIASES.get(
        name
    )

    if canonical is not None:
        return canonical

    # Depois tenta comparação removendo alguns
    # caracteres comuns.
    compact = (
        name
        .replace("-", "")
        .replace("_", "")
        .replace(".", "")
    )

    for alias, canonical_name in BOOKMAKER_ALIASES.items():

        alias_compact = (
            alias
            .replace("-", "")
            .replace("_", "")
            .replace(".", "")
            .replace(" ", "")
        )

        if compact == alias_compact:
            return canonical_name

    return None


# ==========================================================
# VERIFICAÇÃO
# ==========================================================

def is_allowed_bookmaker(
    bookmaker: Optional[str],
) -> bool:
    """
    Informa se o bookmaker está autorizado pelo OddReal.
    """

    normalized = normalize_bookmaker_name(
        bookmaker
    )

    return (
        normalized in BRAZIL_PRIMARY_BOOKMAKERS
    )


# ==========================================================
# NOME PARA INTERFACE
# ==========================================================

def bookmaker_display_name(
    bookmaker: Optional[str],
) -> str:
    """
    Retorna o nome amigável para exibição.
    """

    normalized = normalize_bookmaker_name(
        bookmaker
    )

    if normalized is None:
        return "Casa não autorizada"

    return BOOKMAKER_DISPLAY_NAMES.get(
        normalized,
        normalized.title(),
    )


# ==========================================================
# EXPORTAÇÃO
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
      ]
