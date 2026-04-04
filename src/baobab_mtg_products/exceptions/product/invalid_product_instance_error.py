"""Erreur levée pour un invariant violé sur une instance produit agrégée."""

from baobab_mtg_products.exceptions.baobab_mtg_products_exception import (
    BaobabMtgProductsException,
)


class InvalidProductInstanceError(BaobabMtgProductsException):
    """Invariant global sur une instance de produit (ex. parent incohérent).

    :param message: Détail lisible de la violation d'invariant.
    :type message: str
    """
