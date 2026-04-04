"""Identifiant interne unique d'une instance de produit dans le domaine."""

from dataclasses import dataclass

from baobab_mtg_products.exceptions.product.invalid_product_identifier_error import (
    InvalidProductIdentifierError,
)

_MAX_LEN = 256


@dataclass(frozen=True, slots=True)
class InternalProductId:
    """Value object pour l'identifiant technique ou métier stable du produit.

    La valeur est normalisée (espaces de tête/queue supprimés) et contrainte en
    longueur pour éviter les identifiants vides ou aberrants.

    :param value: Identifiant non vide après normalisation.
    :type value: str
    :raises InvalidProductIdentifierError: si la valeur est vide ou trop longue.
    """

    value: str

    def __post_init__(self) -> None:
        normalized = self.value.strip()
        if not normalized:
            raise InvalidProductIdentifierError(
                "L'identifiant interne du produit ne peut pas être vide.",
            )
        if len(normalized) > _MAX_LEN:
            raise InvalidProductIdentifierError(
                f"L'identifiant interne dépasse la longueur maximale ({_MAX_LEN}).",
            )
        object.__setattr__(self, "value", normalized)
