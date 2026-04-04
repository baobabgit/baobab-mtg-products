"""Erreur levée lorsque le code-barres interne est invalide."""

from baobab_mtg_products.exceptions.baobab_mtg_products_exception import (
    BaobabMtgProductsException,
)


class InvalidInternalBarcodeError(BaobabMtgProductsException):
    """Code-barres interne (piste logistique / interne) rejeté par la validation.

    :param message: Détail lisible de la violation d'invariant.
    :type message: str
    """
