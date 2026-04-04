"""Erreur lorsque le statut ne permet pas encore l'ouverture."""

from baobab_mtg_products.exceptions.baobab_mtg_products_exception import (
    BaobabMtgProductsException,
)


class ProductNotReadyForOpeningError(BaobabMtgProductsException):
    """Le produit n'est ni « sealed » ni « qualified » (ex. encore « registered »).

    :param message: Détail lisible pour l'opérateur ou les logs.
    :type message: str
    """
