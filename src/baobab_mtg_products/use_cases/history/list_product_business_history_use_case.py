"""Cas d'usage : consulter l'historique métier d'un produit."""

from baobab_mtg_products.domain.history.product_business_event_record import (
    ProductBusinessEventRecord,
)
from baobab_mtg_products.domain.products.internal_product_id import InternalProductId
from baobab_mtg_products.ports.product_business_history_query_port import (
    ProductBusinessHistoryQueryPort,
)
from baobab_mtg_products.use_cases.use_case import UseCase


class ListProductBusinessHistoryUseCase(UseCase[tuple[ProductBusinessEventRecord, ...]]):
    """Expose la chronologie issue d'un journal cohérent (ex. ledger mémoire).

    :param product_id: Produit dont on veut l'historique.
    :type product_id: InternalProductId
    :param history: Source de lecture (implémentation du port).
    :type history: ProductBusinessHistoryQueryPort
    """

    def __init__(
        self,
        product_id: InternalProductId,
        history: ProductBusinessHistoryQueryPort,
    ) -> None:
        self._product_id = product_id
        self._history = history

    def execute(self) -> tuple[ProductBusinessEventRecord, ...]:
        """Retourne les enregistrements dans l'ordre métier du journal."""
        return self._history.list_events_for_product(self._product_id.value)
