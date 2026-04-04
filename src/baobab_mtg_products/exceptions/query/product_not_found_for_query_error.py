"""Produit introuvable lors d'une consultation en lecture seule."""

from baobab_mtg_products.exceptions.baobab_mtg_products_exception import (
    BaobabMtgProductsException,
)


class ProductNotFoundForQueryError(BaobabMtgProductsException):
    """Aucune instance ne correspond à l'identifiant demandé pour la lecture.

    :param message: Détail lisible pour l'opérateur ou les logs.
    :type message: str
    """
