"""Tests unitaires — kind CONTAINER_DECONDITIONED (feature 12)."""

from __future__ import annotations

from baobab_mtg_products.domain.history.product_business_event_kind import (
    ProductBusinessEventKind,
)


def test_container_deconditioned_kind_stable() -> None:
    """Valeur stable pour timeline et sérialisation."""
    assert ProductBusinessEventKind.CONTAINER_DECONDITIONED.value == "container_deconditioned"
