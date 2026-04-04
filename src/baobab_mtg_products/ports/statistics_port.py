"""Port sortant vers une brique statistiques (sans implémentation dans la lib)."""

from typing import Protocol

from baobab_mtg_products.domain.integration.card_revealed_statistics_event import (
    CardRevealedStatisticsEvent,
)
from baobab_mtg_products.domain.integration.opening_card_scan_statistics_event import (
    OpeningCardScanStatisticsEvent,
)
from baobab_mtg_products.domain.integration.sealed_product_opened_statistics_event import (
    SealedProductOpenedStatisticsEvent,
)


class StatisticsPort(Protocol):
    """Contrat pour enregistrer des faits d'ouverture et de traçabilité carte."""

    def record_sealed_product_opened(self, event: SealedProductOpenedStatisticsEvent) -> None:
        """Comptabilise l'ouverture d'un produit scellé.

        :param event: Données stables pour agrégation.
        :type event: SealedProductOpenedStatisticsEvent
        """
        ...

    def record_card_revealed_from_opening(self, event: CardRevealedStatisticsEvent) -> None:
        """Comptabilise une carte révélée depuis un scellé ouvert.

        :param event: Provenance produit + identifiant carte.
        :type event: CardRevealedStatisticsEvent
        """
        ...

    def record_opening_card_scan(self, event: OpeningCardScanStatisticsEvent) -> None:
        """Comptabilise un scan de carte pendant la session d'ouverture.

        :param event: Produit ouvert et charge utile de scan.
        :type event: OpeningCardScanStatisticsEvent
        """
        ...
