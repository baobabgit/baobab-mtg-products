"""Tests pour :class:`ProductRelationship`."""

import pytest

from baobab_mtg_products.domain.products.internal_product_id import InternalProductId
from baobab_mtg_products.domain.products.relationships.product_relationship import (
    ProductRelationship,
)
from baobab_mtg_products.domain.products.relationships.product_relationship_kind import (
    ProductRelationshipKind,
)
from baobab_mtg_products.exceptions.relationship.invalid_product_relationship_link_error import (
    InvalidProductRelationshipLinkError,
)


class TestProductRelationship:
    """Invariants du value object de lien."""

    def test_builds_when_parent_and_child_differ(self) -> None:
        """Relation valide."""
        rel = ProductRelationship(
            InternalProductId("p"),
            InternalProductId("c"),
            ProductRelationshipKind.GENERIC_STRUCTURAL_ATTACHMENT,
        )
        assert rel.parent_id.value == "p"
        assert rel.child_id.value == "c"

    def test_rejects_self_link(self) -> None:
        """Parent et enfant identiques : erreur dédiée."""
        with pytest.raises(InvalidProductRelationshipLinkError):
            ProductRelationship(
                InternalProductId("x"),
                InternalProductId("x"),
                ProductRelationshipKind.GENERIC_STRUCTURAL_ATTACHMENT,
            )
