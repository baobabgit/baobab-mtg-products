"""Erreur lorsque l'ordre d'une trace de carte révélée est incohérent."""

from baobab_mtg_products.exceptions.baobab_mtg_products_exception import (
    BaobabMtgProductsException,
)


class InvalidRevealedCardSequenceError(BaobabMtgProductsException):
    """L'index de séquence dans l'ouverture doit être nul ou positif.

    :param message: Détail lisible pour l'opérateur ou les logs.
    :type message: str
    """
