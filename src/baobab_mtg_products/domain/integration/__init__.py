"""DTO et messages pour l'intégration collection / statistiques."""

from baobab_mtg_products.domain.integration.card_revealed_statistics_event import (
    CardRevealedStatisticsEvent,
)
from baobab_mtg_products.domain.integration.opening_card_scan_statistics_event import (
    OpeningCardScanStatisticsEvent,
)
from baobab_mtg_products.domain.integration.product_parent_link_for_collection_event import (
    ProductParentLinkForCollectionEvent,
)
from baobab_mtg_products.domain.integration.product_provenance_for_collection import (
    ProductProvenanceForCollection,
)
from baobab_mtg_products.domain.integration.sealed_product_opened_statistics_event import (
    SealedProductOpenedStatisticsEvent,
)

__all__ = [
    "CardRevealedStatisticsEvent",
    "OpeningCardScanStatisticsEvent",
    "ProductParentLinkForCollectionEvent",
    "ProductProvenanceForCollection",
    "SealedProductOpenedStatisticsEvent",
]
