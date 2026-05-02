"""Tests unitaires — types produits déconditionnables comme contenant (feature 12)."""

from __future__ import annotations

from baobab_mtg_products.domain.deconditioning.deconditionable_container_policy import (
    DeconditionableContainerPolicy,
)
from baobab_mtg_products.domain.products.product_type import ProductType


def test_play_booster_not_deconditionable_container() -> None:
    """Un play booster n'est pas un contenant au sens déconditionnement."""
    assert not DeconditionableContainerPolicy.is_deconditionable_container(
        ProductType.PLAY_BOOSTER,
    )


def test_display_is_deconditionable_container() -> None:
    """Une display est un contenant déconditionnable."""
    assert DeconditionableContainerPolicy.is_deconditionable_container(ProductType.DISPLAY)
