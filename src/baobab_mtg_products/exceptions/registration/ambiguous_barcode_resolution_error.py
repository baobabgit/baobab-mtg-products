"""Erreur lorsque la résolution d'un code-barres est ambiguë."""

from baobab_mtg_products.exceptions.baobab_mtg_products_exception import (
    BaobabMtgProductsException,
)


class AmbiguousBarcodeResolutionError(BaobabMtgProductsException):
    """Plusieurs correspondances valides empêchent de choisir un gabarit produit.

    :param message: Détail lisible pour l'opérateur ou les logs.
    :type message: str
    """
