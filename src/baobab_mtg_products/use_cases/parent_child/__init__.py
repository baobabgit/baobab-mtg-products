"""Cas d'usage des relations structurelles parent / enfant."""

from baobab_mtg_products.use_cases.parent_child.attach_child_product_to_parent_use_case import (
    AttachChildProductToParentUseCase,
)
from baobab_mtg_products.use_cases.parent_child.detach_child_product_from_parent_use_case import (
    DetachChildProductFromParentUseCase,
)

__all__ = [
    "AttachChildProductToParentUseCase",
    "DetachChildProductFromParentUseCase",
]
