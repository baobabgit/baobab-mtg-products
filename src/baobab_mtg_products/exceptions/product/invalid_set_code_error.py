"""Erreur levée lorsque le code de set Magic est invalide."""

from baobab_mtg_products.exceptions.baobab_mtg_products_exception import (
    BaobabMtgProductsException,
)


class InvalidSetCodeError(BaobabMtgProductsException):
    """Code de set (extension) rejeté par les règles métier de format.

    :param message: Détail lisible de la violation d'invariant.
    :type message: str
    """
