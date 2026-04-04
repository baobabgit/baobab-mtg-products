"""Lien structurel validé entre un parent et un enfant."""

from dataclasses import dataclass

from baobab_mtg_products.domain.products.internal_product_id import InternalProductId
from baobab_mtg_products.domain.products.relationships.product_relationship_kind import (
    ProductRelationshipKind,
)
from baobab_mtg_products.exceptions.relationship.invalid_product_relationship_link_error import (
    InvalidProductRelationshipLinkError,
)


@dataclass(frozen=True, slots=True)
class ProductRelationship:
    """Représentation immuable d'un rattachement réussi (audit / événements).

    :param parent_id: Identifiant du produit parent.
    :type parent_id: InternalProductId
    :param child_id: Identifiant du produit enfant.
    :type child_id: InternalProductId
    :param kind: Type de relation métier appliqué.
    :type kind: ProductRelationshipKind
    :raises InvalidProductRelationshipLinkError: si parent et enfant sont identiques.
    """

    parent_id: InternalProductId
    child_id: InternalProductId
    kind: ProductRelationshipKind

    def __post_init__(self) -> None:
        if self.parent_id.value == self.child_id.value:
            raise InvalidProductRelationshipLinkError(
                "Une relation parent-enfant doit lier deux identifiants distincts.",
            )
