"""Erreur levée lorsque le numéro de série est invalide."""

from baobab_mtg_products.exceptions.baobab_mtg_products_exception import (
    BaobabMtgProductsException,
)


class InvalidSerialNumberError(BaobabMtgProductsException):
    """Numéro de série présent mais vide, trop long ou avec caractères interdits.

    :param message: Détail lisible de la violation d'invariant.
    :type message: str
    """
