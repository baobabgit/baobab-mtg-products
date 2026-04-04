"""Port sortant vers une brique collection (sans implémentation dans la lib)."""

from typing import Protocol

from baobab_mtg_products.domain.integration.product_parent_link_for_collection_event import (
    ProductParentLinkForCollectionEvent,
)
from baobab_mtg_products.domain.integration.product_provenance_for_collection import (
    ProductProvenanceForCollection,
)


class CollectionPort(Protocol):
    """Contrat pour synchroniser provenance et structure parent-enfant.

    Les adaptateurs vivent côté application ; la lib ne fournit que les DTO métier.
    """

    def publish_product_provenance(self, provenance: ProductProvenanceForCollection) -> None:
        """Publie ou met à jour l'instantané d'un produit scellé.

        :param provenance: État courant issu du domaine.
        :type provenance: ProductProvenanceForCollection
        """
        ...

    def publish_parent_child_link(self, link: ProductParentLinkForCollectionEvent) -> None:
        """Signale un rattachement actif ou sa levée pour la vue collection.

        :param link: Détail du lien structurel.
        :type link: ProductParentLinkForCollectionEvent
        """
        ...
