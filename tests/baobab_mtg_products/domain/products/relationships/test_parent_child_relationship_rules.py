"""Tests pour :class:`ParentChildRelationshipRules`."""

from typing import cast

import pytest

from baobab_mtg_products.domain.products.internal_product_id import InternalProductId
from baobab_mtg_products.domain.products.mtg_set_code import MtgSetCode
from baobab_mtg_products.domain.products.product_instance import ProductInstance
from baobab_mtg_products.domain.products.product_status import ProductStatus
from baobab_mtg_products.domain.products.product_type import ProductType
from baobab_mtg_products.domain.products.relationships.parent_child_relationship_rules import (
    ParentChildRelationshipRules,
)
from baobab_mtg_products.domain.products.relationships.product_relationship_kind import (
    ProductRelationshipKind,
)
from baobab_mtg_products.exceptions.relationship.incompatible_parent_child_types_error import (
    IncompatibleParentChildTypesError,
)


def _inst(pid: str, ptype: ProductType) -> ProductInstance:
    return ProductInstance(
        InternalProductId(pid),
        ptype,
        MtgSetCode("TS"),
        ProductStatus.SEALED,
    )


class TestParentChildRelationshipRules:
    """Règles display / bundle / générique."""

    def test_display_booster_ok(self) -> None:
        """Display + play booster."""
        ParentChildRelationshipRules.validate(
            _inst("d", ProductType.DISPLAY),
            _inst("b", ProductType.PLAY_BOOSTER),
            ProductRelationshipKind.DISPLAY_CONTAINS_BOOSTER,
        )

    def test_display_non_booster_rejected(self) -> None:
        """Display + bundle interdit pour ce kind."""
        with pytest.raises(IncompatibleParentChildTypesError):
            ParentChildRelationshipRules.validate(
                _inst("d", ProductType.DISPLAY),
                _inst("u", ProductType.BUNDLE),
                ProductRelationshipKind.DISPLAY_CONTAINS_BOOSTER,
            )

    def test_non_display_parent_rejected_for_display_kind(self) -> None:
        """Parent bundle avec kind display."""
        with pytest.raises(IncompatibleParentChildTypesError):
            ParentChildRelationshipRules.validate(
                _inst("b", ProductType.BUNDLE),
                _inst("p", ProductType.PLAY_BOOSTER),
                ProductRelationshipKind.DISPLAY_CONTAINS_BOOSTER,
            )

    def test_bundle_subproduct_ok(self) -> None:
        """Bundle + booster."""
        ParentChildRelationshipRules.validate(
            _inst("b", ProductType.BUNDLE),
            _inst("p", ProductType.DRAFT_BOOSTER),
            ProductRelationshipKind.BUNDLE_CONTAINS_SUBPRODUCT,
        )

    def test_bundle_display_rejected(self) -> None:
        """Display interdite sous bundle."""
        with pytest.raises(IncompatibleParentChildTypesError):
            ParentChildRelationshipRules.validate(
                _inst("b", ProductType.BUNDLE),
                _inst("d", ProductType.DISPLAY),
                ProductRelationshipKind.BUNDLE_CONTAINS_SUBPRODUCT,
            )

    def test_non_bundle_parent_rejected_for_bundle_kind(self) -> None:
        """Kind bundle avec parent display."""
        with pytest.raises(IncompatibleParentChildTypesError):
            ParentChildRelationshipRules.validate(
                _inst("d", ProductType.DISPLAY),
                _inst("p", ProductType.PLAY_BOOSTER),
                ProductRelationshipKind.BUNDLE_CONTAINS_SUBPRODUCT,
            )

    def test_generic_allows_mixed_types(self) -> None:
        """Kind générique : pas de filtre sur les types."""
        ParentChildRelationshipRules.validate(
            _inst("a", ProductType.OTHER_SEALED),
            _inst("z", ProductType.COMMANDER_DECK),
            ProductRelationshipKind.GENERIC_STRUCTURAL_ATTACHMENT,
        )

    def test_unknown_kind_rejected(self) -> None:
        """Valeur ne correspondant à aucun membre connu de l'enum (garde-fou)."""
        bogus = cast(ProductRelationshipKind, object())
        with pytest.raises(IncompatibleParentChildTypesError):
            ParentChildRelationshipRules.validate(
                _inst("a", ProductType.DISPLAY),
                _inst("b", ProductType.PLAY_BOOSTER),
                bogus,
            )
