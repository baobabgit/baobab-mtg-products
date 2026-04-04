"""Tests pour :class:`ProductRelationshipKind`."""

from baobab_mtg_products.domain.products.relationships.product_relationship_kind import (
    ProductRelationshipKind,
)


class TestProductRelationshipKind:
    """Valeurs stables exposées aux journaux d'événements."""

    def test_enum_values_are_stable_strings(self) -> None:
        """Les valeurs restent des chaînes sérialisables."""
        assert ProductRelationshipKind.DISPLAY_CONTAINS_BOOSTER.value == "display_contains_booster"
        assert ProductRelationshipKind.BUNDLE_CONTAINS_SUBPRODUCT.value == (
            "bundle_contains_subproduct"
        )
        assert ProductRelationshipKind.GENERIC_STRUCTURAL_ATTACHMENT.value == (
            "generic_structural_attachment"
        )
