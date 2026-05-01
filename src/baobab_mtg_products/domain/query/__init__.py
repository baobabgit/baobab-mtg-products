"""Modèles de lecture et vues pour la consultation métier."""

from baobab_mtg_products.domain.query.product_structural_view import ProductStructuralView
from baobab_mtg_products.domain.query.sealed_product_snapshot import SealedProductSnapshot

__all__ = ["ProductStructuralView", "SealedProductSnapshot"]
