"""Service : chronologie métier issue du journal pour un produit."""

from baobab_mtg_products.domain.history.product_business_event_record import (
    ProductBusinessEventRecord,
)
from baobab_mtg_products.domain.products.internal_product_id import InternalProductId
from baobab_mtg_products.ports.product_business_history_query_port import (
    ProductBusinessHistoryQueryPort,
)


class GetProductBusinessTimelineService:
    """Consultation en lecture seule de l'historique métier déjà journalisé.

    :param product_id: Cible de la chronologie.
    :type product_id: InternalProductId
    :param history: Port de lecture (ex. ledger mémoire).
    :type history: ProductBusinessHistoryQueryPort
    """

    def __init__(
        self,
        product_id: InternalProductId,
        history: ProductBusinessHistoryQueryPort,
    ) -> None:
        self._product_id = product_id
        self._history = history

    def load(self) -> tuple[ProductBusinessEventRecord, ...]:
        """Retourne les enregistrements dans l'ordre d'insertion du journal.

        :return: Séquence immuable d'événements.
        :rtype: tuple[ProductBusinessEventRecord, ...]
        """
        return self._history.list_events_for_product(self._product_id.value)
