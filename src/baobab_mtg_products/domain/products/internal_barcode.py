"""Code-barres ou identifiant interne (logistique, étiquette magasin, etc.)."""

import re
from dataclasses import dataclass

from baobab_mtg_products.exceptions.product.invalid_internal_barcode_error import (
    InvalidInternalBarcodeError,
)

_MAX_LEN = 64
_PATTERN = re.compile(r"^[A-Za-z0-9._:-]+$")


@dataclass(frozen=True, slots=True)
class InternalBarcode:
    """Value object pour une piste interne distincte du code commercial.

    Autorise lettres, chiffres et quelques séparateurs usuels en entrepôt.

    :param value: Identifiant interne non vide après normalisation.
    :type value: str
    :raises InvalidInternalBarcodeError: si le format ou la longueur est invalide.
    """

    value: str

    def __post_init__(self) -> None:
        normalized = self.value.strip()
        if not normalized:
            raise InvalidInternalBarcodeError(
                "Le code-barres interne ne peut pas être vide.",
            )
        if len(normalized) > _MAX_LEN:
            raise InvalidInternalBarcodeError(
                f"Le code-barres interne dépasse {_MAX_LEN} caractères.",
            )
        if _PATTERN.fullmatch(normalized) is None:
            raise InvalidInternalBarcodeError(
                "Le code-barres interne contient des caractères non autorisés.",
            )
        object.__setattr__(self, "value", normalized)
