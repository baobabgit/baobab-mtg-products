"""Identifiant stable d'une référence commerciale partagée par plusieurs instances."""

from dataclasses import dataclass

from baobab_mtg_products.exceptions.product.invalid_product_reference_id_error import (
    InvalidProductReferenceIdError,
)

_MAX_LEN = 256


@dataclass(frozen=True, slots=True)
class ProductReferenceId:
    """Value object pour l'identifiant technique d'une :class:`ProductReference`.

    La valeur est normalisée (espaces de tête et de queue supprimés) et contrainte
    en longueur pour éviter les identifiants vides ou aberrants.

    :param value: Identifiant non vide après normalisation.
    :type value: str
    :raises InvalidProductReferenceIdError: si la valeur est vide ou trop longue.
    """

    value: str

    def __post_init__(self) -> None:
        normalized = self.value.strip()
        if not normalized:
            raise InvalidProductReferenceIdError(
                "L'identifiant de référence produit ne peut pas être vide.",
            )
        if len(normalized) > _MAX_LEN:
            raise InvalidProductReferenceIdError(
                f"L'identifiant de référence dépasse la longueur maximale ({_MAX_LEN}).",
            )
        object.__setattr__(self, "value", normalized)
