"""Erreur lorsqu'un second déconditionnement est tenté sur la même instance."""

from baobab_mtg_products.exceptions.baobab_mtg_products_exception import (
    BaobabMtgProductsException,
)


class ContainerAlreadyDeconditionedError(BaobabMtgProductsException):
    """Le contenant porte déjà le statut « déconditionné »."""
