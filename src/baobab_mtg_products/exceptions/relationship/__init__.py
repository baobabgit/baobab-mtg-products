"""Exceptions liées aux relations parent / enfant."""

from baobab_mtg_products.exceptions.relationship.child_product_not_attached_error import (
    ChildProductNotAttachedError,
)
from baobab_mtg_products.exceptions.relationship.circular_product_parentage_error import (
    CircularProductParentageError,
)
from baobab_mtg_products.exceptions.relationship.detach_parent_mismatch_error import (
    DetachParentMismatchError,
)
from baobab_mtg_products.exceptions.relationship.incompatible_parent_child_types_error import (
    IncompatibleParentChildTypesError,
)
from baobab_mtg_products.exceptions.relationship.incomplete_product_hierarchy_error import (
    IncompleteProductHierarchyError,
)
from baobab_mtg_products.exceptions.relationship.invalid_product_relationship_link_error import (
    InvalidProductRelationshipLinkError,
)
from baobab_mtg_products.exceptions.relationship.product_already_has_parent_error import (
    ProductAlreadyHasParentError,
)

__all__ = [
    "ChildProductNotAttachedError",
    "CircularProductParentageError",
    "DetachParentMismatchError",
    "IncompleteProductHierarchyError",
    "IncompatibleParentChildTypesError",
    "InvalidProductRelationshipLinkError",
    "ProductAlreadyHasParentError",
]
