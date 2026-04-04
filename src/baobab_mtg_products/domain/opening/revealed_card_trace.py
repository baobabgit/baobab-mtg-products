"""Lien de provenance entre un produit ouvert et une carte révélée."""

from dataclasses import dataclass

from baobab_mtg_products.domain.opening.external_card_id import ExternalCardId
from baobab_mtg_products.domain.products.internal_product_id import InternalProductId
from baobab_mtg_products.exceptions.opening.invalid_revealed_card_sequence_error import (
    InvalidRevealedCardSequenceError,
)


@dataclass(frozen=True, slots=True)
class RevealedCardTrace:
    """Trace immuable : quelle carte, depuis quel produit ouvert, à quel rang.

    :param source_product_id: Produit ouvert dont la carte provient.
    :type source_product_id: InternalProductId
    :param external_card_id: Identifiant carte côté intégration externe.
    :type external_card_id: ExternalCardId
    :param sequence_in_opening: Ordre d'enregistrement (0 pour la première carte).
    :type sequence_in_opening: int
    :raises InvalidRevealedCardSequenceError: si la séquence est strictement négative.
    """

    source_product_id: InternalProductId
    external_card_id: ExternalCardId
    sequence_in_opening: int

    def __post_init__(self) -> None:
        if self.sequence_in_opening < 0:
            raise InvalidRevealedCardSequenceError(
                "La séquence d'ouverture doit être positive ou nulle.",
            )
