"""Tests structurels du port :class:`~baobab_mtg_products.ports.CollectionPort`."""

from baobab_mtg_products.domain.integration.product_parent_link_for_collection_event import (
    ProductParentLinkForCollectionEvent,
)
from baobab_mtg_products.domain.integration.product_provenance_for_collection import (
    ProductProvenanceForCollection,
)
from baobab_mtg_products.ports.collection_port import CollectionPort


class _FakeCollectionAdapter:
    """Adaptateur minimal compatible avec :class:`CollectionPort`."""

    def __init__(self) -> None:
        self.provenance: list[ProductProvenanceForCollection] = []
        self.links: list[ProductParentLinkForCollectionEvent] = []

    def publish_product_provenance(self, provenance: ProductProvenanceForCollection) -> None:
        """Enregistre l'instantané (double de test)."""
        self.provenance.append(provenance)

    def publish_parent_child_link(self, link: ProductParentLinkForCollectionEvent) -> None:
        """Enregistre l'événement de lien (double de test)."""
        self.links.append(link)


class TestCollectionPort:
    """Vérifie qu'un adaptateur peut satisfaire le contrat du port."""

    def test_adapter_publishes_provenance_and_link(self) -> None:
        """Les méthodes du port sont appelables sur un adaptateur typé."""
        fake = _FakeCollectionAdapter()
        adapter: CollectionPort = fake
        prov = ProductProvenanceForCollection(
            internal_product_id="p-1",
            product_type_value="bundle",
            set_code_value="FDN",
            product_status_value="sealed",
            parent_product_id=None,
        )
        adapter.publish_product_provenance(prov)
        link = ProductParentLinkForCollectionEvent(
            child_product_id="c",
            parent_product_id="p",
            relationship_kind_value="display_contains_booster",
            attached=True,
        )
        adapter.publish_parent_child_link(link)
        assert fake.provenance == [prov]
        assert fake.links == [link]
