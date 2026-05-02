"""Erreur lorsque le type d'instance ne peut pas jouer le rôle de contenant déconditionné."""

from baobab_mtg_products.exceptions.baobab_mtg_products_exception import (
    BaobabMtgProductsException,
)


class ProductNotDeconditionableContainerError(BaobabMtgProductsException):
    """Seuls certains types (display, bundle, kit prerelease, etc.) sont des contenants."""
