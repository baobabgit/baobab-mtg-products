"""Code d'extension (set) Magic associé à un produit scellé."""

import re
from dataclasses import dataclass

from baobab_mtg_products.exceptions.product.invalid_set_code_error import InvalidSetCodeError

_PATTERN = re.compile(r"^[A-Za-z0-9]{2,10}$")


@dataclass(frozen=True, slots=True)
class MtgSetCode:
    """Value object pour le code de set (ex. ``MH3``, ``FDN``).

    Le code est normalisé en majuscules pour comparaisons stables.

    :param value: Code alphanumérique du set, longueur 2 à 10.
    :type value: str
    :raises InvalidSetCodeError: si le format est invalide.
    """

    value: str

    def __post_init__(self) -> None:
        candidate = self.value.strip().upper()
        if _PATTERN.fullmatch(candidate) is None:
            raise InvalidSetCodeError(
                "Le code de set doit contenir 2 à 10 caractères alphanumériques.",
            )
        object.__setattr__(self, "value", candidate)
