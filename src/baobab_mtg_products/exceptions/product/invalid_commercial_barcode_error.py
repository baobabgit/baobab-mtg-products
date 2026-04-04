"""Erreur levée lorsque le code-barres commercial est invalide."""

from baobab_mtg_products.exceptions.baobab_mtg_products_exception import (
    BaobabMtgProductsException,
)


class InvalidCommercialBarcodeError(BaobabMtgProductsException):
    """Code-barres commercial (GTIN / EAN, etc.) rejeté par la validation.

    :param message: Détail lisible de la violation d'invariant.
    :type message: str
    """
