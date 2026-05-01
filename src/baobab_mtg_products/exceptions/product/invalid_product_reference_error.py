"""Erreur lorsque l'agrégat :class:`ProductReference` viole un invariant métier."""

from baobab_mtg_products.exceptions.baobab_mtg_products_exception import (
    BaobabMtgProductsException,
)


class InvalidProductReferenceError(BaobabMtgProductsException):
    """Levée lorsque les données d'une référence commerciale sont incohérentes.

    :param message: Détail lisible de la violation d'invariant.
    :type message: str
    """
