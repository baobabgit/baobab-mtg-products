"""Erreur lorsqu'on trace une carte alors que le produit source n'est pas ouvert."""

from baobab_mtg_products.exceptions.baobab_mtg_products_exception import (
    BaobabMtgProductsException,
)


class ProductNotOpenedForCardTraceError(BaobabMtgProductsException):
    """Les révélations / scans carte exigent un produit au statut « opened ».

    :param message: Détail lisible pour l'opérateur ou les logs.
    :type message: str
    """
