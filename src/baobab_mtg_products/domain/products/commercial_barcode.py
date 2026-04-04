"""Code-barres commercial (GTIN, UPC, etc.) associé au produit."""

from dataclasses import dataclass

from baobab_mtg_products.exceptions.product.invalid_commercial_barcode_error import (
    InvalidCommercialBarcodeError,
)

_MIN_LEN = 4
_MAX_LEN = 32


@dataclass(frozen=True, slots=True)
class CommercialBarcode:
    """Value object pour un code-barres issu du conditionnement commercial.

    Validation souple (longueur et caractères) pour couvrir EAN/UPC sans
    dépendre d'un référentiel externe.

    :param value: Chaîne numérique ou alphanumérique normalisée.
    :type value: str
    :raises InvalidCommercialBarcodeError: si la valeur est hors plage ou vide.
    """

    value: str

    def __post_init__(self) -> None:
        normalized = self.value.strip()
        if not normalized:
            raise InvalidCommercialBarcodeError(
                "Le code-barres commercial ne peut pas être vide.",
            )
        if not normalized.isdigit():
            raise InvalidCommercialBarcodeError(
                "Le code-barres commercial doit être composé uniquement de chiffres.",
            )
        if len(normalized) < _MIN_LEN or len(normalized) > _MAX_LEN:
            raise InvalidCommercialBarcodeError(
                f"Le code-barres commercial doit compter entre {_MIN_LEN} et "
                f"{_MAX_LEN} chiffres.",
            )
        object.__setattr__(self, "value", normalized)
