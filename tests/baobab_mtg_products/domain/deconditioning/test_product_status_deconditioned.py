"""Tests unitaires — statut DECONDITIONED (feature 12)."""

from __future__ import annotations

from baobab_mtg_products.domain.products.product_status import ProductStatus


def test_deconditioned_value_stable() -> None:
    """La valeur enum reste stable pour contrats API / persistance."""
    assert ProductStatus.DECONDITIONED.value == "deconditioned"
