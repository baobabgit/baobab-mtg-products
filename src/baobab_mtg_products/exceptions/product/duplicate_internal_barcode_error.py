"""Erreur lorsqu'un code-barres interne est déjà attribué à une autre instance."""

from baobab_mtg_products.exceptions.baobab_mtg_products_exception import (
    BaobabMtgProductsException,
)


class DuplicateInternalBarcodeError(BaobabMtgProductsException):
    """Levée lorsqu'une persistance tente de réutiliser un code-barres interne unique.

    :param message: Détail lisible pour l'appelant.
    :type message: str
    """
