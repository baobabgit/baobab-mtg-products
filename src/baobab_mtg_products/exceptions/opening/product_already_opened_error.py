"""Erreur lorsqu'on tente d'ouvrir un produit déjà au statut ouvert."""

from baobab_mtg_products.exceptions.baobab_mtg_products_exception import (
    BaobabMtgProductsException,
)


class ProductAlreadyOpenedError(BaobabMtgProductsException):
    """Le produit porte déjà le statut « opened ».

    :param message: Détail lisible pour l'opérateur ou les logs.
    :type message: str
    """
