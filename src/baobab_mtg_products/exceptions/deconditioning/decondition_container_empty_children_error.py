"""Erreur lorsque la commande de déconditionnement ne liste aucun enfant."""

from baobab_mtg_products.exceptions.baobab_mtg_products_exception import (
    BaobabMtgProductsException,
)


class DeconditionContainerEmptyChildrenError(BaobabMtgProductsException):
    """Au moins un enfant doit être fourni pour déconditionner un contenant."""
