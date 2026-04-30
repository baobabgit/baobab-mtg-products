"""Instantané consultation : instance physique et référence catalogue associée."""

from __future__ import annotations

from dataclasses import dataclass

from baobab_mtg_products.domain.products.product_instance import ProductInstance
from baobab_mtg_products.domain.products.product_reference import ProductReference


@dataclass(frozen=True, slots=True)
class SealedProductSnapshot:
    """Vue lecture seule alignant un exemplaire physique et sa référence métier.

    :param product: Instance persistée consultée.
    :type product: ProductInstance
    :param reference: Référence catalogue portant nom, visuel et code-barres commercial.
    :type reference: ProductReference
    """

    product: ProductInstance
    reference: ProductReference
