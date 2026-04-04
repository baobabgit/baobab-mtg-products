"""Enregistrement immuable dans l'historique métier d'un produit."""

from dataclasses import dataclass

from baobab_mtg_products.domain.history.product_business_event_kind import (
    ProductBusinessEventKind,
)
from baobab_mtg_products.domain.history.product_business_event_payload import (
    ProductBusinessEventPayload,
)


@dataclass(frozen=True, slots=True)
class ProductBusinessEventRecord:
    """Une ligne de journal ordonnée par :attr:`global_sequence`.

    :param global_sequence: Ordre total d'insertion dans le ledger (monotone).
    :type global_sequence: int
    :param principal_product_id: Identifiant principal concerné (filtrage par défaut).
    :type principal_product_id: str
    :param kind: Type d'événement métier.
    :type kind: ProductBusinessEventKind
    :param payload: Détails optionnels selon le kind.
    :type payload: ProductBusinessEventPayload
    """

    global_sequence: int
    principal_product_id: str
    kind: ProductBusinessEventKind
    payload: ProductBusinessEventPayload
