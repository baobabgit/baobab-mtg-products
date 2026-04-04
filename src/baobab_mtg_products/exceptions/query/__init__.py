"""Exceptions liées aux services de consultation."""

from baobab_mtg_products.exceptions.query.missing_referenced_parent_product_error import (
    MissingReferencedParentProductError,
)
from baobab_mtg_products.exceptions.query.product_not_found_for_query_error import (
    ProductNotFoundForQueryError,
)

__all__ = ["MissingReferencedParentProductError", "ProductNotFoundForQueryError"]
