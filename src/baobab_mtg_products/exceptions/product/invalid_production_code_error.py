"""Erreur lorsque le code de production est invalide."""

from baobab_mtg_products.exceptions.baobab_mtg_products_exception import (
    BaobabMtgProductsException,
)


class InvalidProductionCodeError(BaobabMtgProductsException):
    """Levée lorsque la valeur d'un :class:`ProductionCode` est rejetée.

    :param message: Détail lisible de la violation d'invariant.
    :type message: str
    """
