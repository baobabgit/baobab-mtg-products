"""Port de lecture de l'historique métier par identifiant produit."""

from typing import Protocol

from baobab_mtg_products.domain.history.product_business_event_record import (
    ProductBusinessEventRecord,
)


class ProductBusinessHistoryQueryPort(Protocol):
    """Contrat pour consulter la chronologie des faits liés à un produit."""

    def list_events_for_product(self, product_id: str) -> tuple[ProductBusinessEventRecord, ...]:
        """Retourne les événements pertinents, triés par ordre d'arrivée dans le journal.

        :param product_id: Identifiant interne cible.
        :type product_id: str
        :return: Vue immuable de l'historique.
        :rtype: tuple[ProductBusinessEventRecord, ...]
        """
        ...
