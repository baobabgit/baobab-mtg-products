"""Erreur lorsque le type de produit ne peut pas être ouvert comme unité scellée."""

from baobab_mtg_products.exceptions.baobab_mtg_products_exception import (
    BaobabMtgProductsException,
)


class ProductNotOpenableError(BaobabMtgProductsException):
    """Exemple : une display n'est pas ouverte comme produit feuille unique.

    :param message: Détail lisible pour l'opérateur ou les logs.
    :type message: str
    """
