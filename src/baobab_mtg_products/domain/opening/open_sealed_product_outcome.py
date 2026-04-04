"""Résultat agrégé de la transition vers le statut « opened »."""

from dataclasses import dataclass

from baobab_mtg_products.domain.opening.product_opening_event import ProductOpeningEvent
from baobab_mtg_products.domain.products.product_instance import ProductInstance


@dataclass(frozen=True, slots=True)
class OpenSealedProductOutcome:
    """Instance persistée après ouverture et événement métier associé.

    :param updated_product: Agrégat produit après passage au statut ``opened``.
    :type updated_product: ProductInstance
    :param opening_event: Fait d'ouverture pour journalisation ou audit.
    :type opening_event: ProductOpeningEvent
    """

    updated_product: ProductInstance
    opening_event: ProductOpeningEvent
