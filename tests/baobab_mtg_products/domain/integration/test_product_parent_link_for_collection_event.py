"""Tests pour :class:`ProductParentLinkForCollectionEvent`."""

import pytest

from baobab_mtg_products.domain.integration.product_parent_link_for_collection_event import (
    ProductParentLinkForCollectionEvent,
)
from baobab_mtg_products.exceptions.integration.invalid_integration_payload_error import (
    InvalidIntegrationPayloadError,
)


class TestProductParentLinkForCollectionEvent:
    """Validation du DTO lien parent-enfant pour la collection."""

    def test_attached_requires_non_empty_kind(self) -> None:
        """Un rattachement actif sans kind lève une erreur métier."""
        with pytest.raises(InvalidIntegrationPayloadError):
            ProductParentLinkForCollectionEvent(
                child_product_id="c",
                parent_product_id="p",
                relationship_kind_value=None,
                attached=True,
            )

    def test_detached_allows_empty_kind(self) -> None:
        """Une levée de lien n'impose pas de kind."""
        evt = ProductParentLinkForCollectionEvent(
            child_product_id="c",
            parent_product_id="p",
            relationship_kind_value=None,
            attached=False,
        )
        assert evt.attached is False
        assert evt.relationship_kind_value is None
