"""Règles de cohérence des types pour un rattachement parent / enfant."""

from typing import FrozenSet

from baobab_mtg_products.domain.products.product_instance import ProductInstance
from baobab_mtg_products.domain.products.product_type import ProductType
from baobab_mtg_products.domain.products.relationships.product_relationship_kind import (
    ProductRelationshipKind,
)
from baobab_mtg_products.exceptions.relationship.incompatible_parent_child_types_error import (
    IncompatibleParentChildTypesError,
)

_BOOSTER_TYPES: FrozenSet[ProductType] = frozenset(
    {
        ProductType.PLAY_BOOSTER,
        ProductType.COLLECTOR_BOOSTER,
        ProductType.DRAFT_BOOSTER,
        ProductType.SET_BOOSTER,
    },
)


class ParentChildRelationshipRules:
    """Valide la combinaison (parent, enfant, kind) avant persistance."""

    @classmethod
    def validate(
        cls,
        parent: ProductInstance,
        child: ProductInstance,
        kind: ProductRelationshipKind,
    ) -> None:
        """Lève une exception si les types ne respectent pas le kind choisi.

        :param parent: Instance désignée comme parent.
        :type parent: ProductInstance
        :param child: Instance désignée comme enfant.
        :type child: ProductInstance
        :param kind: Règle métier attendue.
        :type kind: ProductRelationshipKind
        :raises IncompatibleParentChildTypesError: si la combinaison est interdite.
        """
        match kind:
            case ProductRelationshipKind.DISPLAY_CONTAINS_BOOSTER:
                cls._validate_display_contains_booster(parent, child)
                return
            case ProductRelationshipKind.BUNDLE_CONTAINS_SUBPRODUCT:
                cls._validate_bundle_contains_subproduct(parent, child)
                return
            case ProductRelationshipKind.GENERIC_STRUCTURAL_ATTACHMENT:
                return

    @staticmethod
    def _validate_display_contains_booster(
        parent: ProductInstance,
        child: ProductInstance,
    ) -> None:
        if parent.product_type is not ProductType.DISPLAY:
            raise IncompatibleParentChildTypesError(
                "Seule une display peut être parente pour le kind « display_contains_booster ».",
            )
        if child.product_type not in _BOOSTER_TYPES:
            raise IncompatibleParentChildTypesError(
                "L'enfant doit être un type de booster pour être rattaché à une display.",
            )

    @staticmethod
    def _validate_bundle_contains_subproduct(
        parent: ProductInstance,
        child: ProductInstance,
    ) -> None:
        if parent.product_type is not ProductType.BUNDLE:
            raise IncompatibleParentChildTypesError(
                "Seul un bundle peut être parent pour le kind « bundle_contains_subproduct ».",
            )
        if child.product_type is ProductType.DISPLAY:
            raise IncompatibleParentChildTypesError(
                "Une display ne peut pas être sous-produit d'un bundle.",
            )
